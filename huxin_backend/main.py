from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
from openai import AsyncOpenAI

# ==========================================
# 1. 基础配置：打地基与请保安
# ==========================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2. 核心组件连接：大模型与数据库
# ==========================================
# 连接本地 Ollama 大模型
client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama" # 本地调用无需真实 key
)

# 连接刚才用 import_data.py 灌入数据的本地向量数据库
try:
    chroma_client = chromadb.PersistentClient(path="./legal_db")
    collection = chroma_client.get_collection(name="laws")
except Exception as e:
    print(f"⚠️ 警告：无法加载数据库，请确保已运行过 import_data.py。错误: {e}")
    collection = None

# ==========================================
# 3. 数据模型：定义前端传过来的参数
# ==========================================
class ChatRequest(BaseModel):
    message: str

# ==========================================
# 4. 接口路由：大门的接待逻辑
# ==========================================
# 迎宾测试接口（打开浏览器直接访问时显示）
@app.get("/")
async def root():
    return {"message": "✅ LegalOne 法律大模型后端已成功启动，API 接口正常运行中！"}

# 核心对话接口（给前端调用的 POST 接口）
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    user_message = request.message
    retrieved_context = ""

    # 第一步：去数据库里“翻卷宗”
    if collection:
        results = collection.query(
            query_texts=[user_message],
            n_results=3 # 提取最相关的 3 条法条或案例
        )
        if results and results['documents'] and results['documents'][0]:
            retrieved_context = "\n\n".join(results['documents'][0])
    
    # 第二步：构建“开卷考试”的提示词 (Prompt)
    system_prompt = f"""你是一个专业、富有同理心的中国法律援助AI，专门帮助农民工解决欠薪等劳动纠纷。
请根据以下【参考资料】来回答用户的提问。如果参考资料中没有相关信息，请根据你的专业法律知识解答。
态度要平易近人，不要用晦涩的法言法语，尽量给出可操作的【解决路径】。

【参考资料】：
{retrieved_context}
"""
    try:
        # 第三步：呼叫本地大模型答题
        response = await client.chat.completions.create(
            model="legalone", # 就是你之前打包出来的模型名字
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        
        ai_reply = response.choices[0].message.content

        # 第四步：把成绩单打包发回给前端
        return {
            "status": "success",
            "retrieved_context": retrieved_context if retrieved_context else "未在知识库匹配到相关资料，使用模型原生知识解答。",
            "reply": ai_reply
        }
        
    except Exception as e:
        # 如果 Ollama 没开，或者模型名字不对，这里会抓住报错并丢给前端
        raise HTTPException(status_code=500, detail=f"大模型调用失败，请检查 Ollama 是否启动。错误详情: {str(e)}")