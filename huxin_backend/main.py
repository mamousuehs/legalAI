import chromadb
from fastapi import FastAPI
from pydantic import BaseModel
from openai import AsyncOpenAI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 【跨域设置】：允许前端 Vue 顺利连接这个后端
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 1. 引擎初始化：连接本地模型与知识库
# ==========================================
# 指向你本地的 Ollama 接口
client = AsyncOpenAI(
    base_url="http://127.0.0.1:11434/v1",
    api_key="ollama"
)

# 初始化 ChromaDB 向量数据库（会自动在项目目录下建一个 legal_db 文件夹）
chroma_client = chromadb.PersistentClient(path="./legal_db")
collection = chroma_client.get_or_create_collection(name="laws")

# 【新手体验补丁】：如果数据库是空的，先塞两条测试数据进去，方便你马上测试 RAG 效果
if collection.count() == 0:
    print("检测到数据库为空，正在注入测试法律条文...")
    collection.add(
        documents=[
            "《劳动合同法》第八十二条：用人单位自用工之日起超过一个月不满一年未与劳动者订立书面劳动合同的，应当向劳动者每月支付二倍的工资。",
            "【办案指导】：在没有老板欠条的情况下，微信聊天记录、转账记录、考勤打卡记录均可作为认定存在事实劳动关系的有效证据。"
        ],
        ids=["law_1", "case_1"]
    )

# 定义前端发来的数据格式
class ChatRequest(BaseModel):
    message: str

# ==========================================
# 2. 核心业务接口：接收前端消息，检索法条，生成回答
# ==========================================
@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    print(f"收到用户提问: {req.message}")
    
    # 步骤 A：去数据库搜相关法条（这里设置搜最相关的 2 条）
    results = collection.query(
        query_texts=[req.message],
        n_results=2 
    )
    # 把搜到的条文拼成一个长字符串
    context = "\n".join(results['documents'][0])
    print(f"为大模型提供的参考资料:\n{context}")

    # 步骤 B：组装 Prompt，把“资料”和“问题”包在一起
    system_prompt = f"""
    你是一个专业的中国劳动法律师。请严格根据以下【参考资料】回答用户问题，绝不要自己编造法条。
    如果资料里没有对应信息，请告诉用户还需要补充什么证据。
    
    【参考资料开始】
    {context}
    【参考资料结束】
    """

    # 步骤 C：让 LegalOne 开卷考试
    response = await client.chat.completions.create(
        model="legalone", # 注意：必须和你当时 ollama create 用的名字一模一样
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": req.message}
        ],
        temperature=0.1
    )

    # 返回结果给前端
    return {
        "status": "success",
        "retrieved_context": context, # 把后台查到的资料也传给前端看看
        "reply": response.choices[0].message.content
    }