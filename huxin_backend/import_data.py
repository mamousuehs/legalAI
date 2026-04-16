import chromadb
import pandas as pd
from docx import Document
import os

print("🔌 正在连接本地知识库...")
chroma_client = chromadb.PersistentClient(path="./legal_db")
collection = chroma_client.get_or_create_collection(name="laws")

documents_list = []
ids_list = []
counter = 0

# ==========================================
# 任务一：吃掉 Word 里的法条
# ==========================================
word_filename = "法条适用.docx"  
print(f"📖 正在读取 Word 文件：{word_filename}...")

if os.path.exists(word_filename):
    doc = Document(word_filename)
    for para in doc.paragraphs:
        text = para.text.strip()
        if len(text) > 10: 
            documents_list.append(f"【法律规范】{text}")
            ids_list.append(f"law_{counter}")
            counter += 1
    print(f"✅ Word 读取完毕！提取了 {counter} 段法律规范。")
else:
    print(f"❌ 找不到文件 {word_filename}，请检查名字拼写！")

# ==========================================
# 任务二：吃掉 Excel 里的案例（为你专门优化的多列组合版）
# ==========================================
excel_filename = "涉欠薪典型案例汇总.xlsx" 
print(f"📊 正在读取 Excel 文件：{excel_filename}...")

if os.path.exists(excel_filename):
    # 读取 Excel，并把里面空白的格子填上空字符串，防止程序报错
    df = pd.read_excel(excel_filename).fillna("")
    
    # 逐行遍历表格
    for index, row in df.iterrows():
        # 提取核心的几列内容
        case_name = str(row.get("案件名称", "")).strip()
        cause = str(row.get("案由", "")).strip()
        claim = str(row.get("主张", "")).strip()
        difficulty = str(row.get("申请执行人的困难", "")).strip()
        solution = str(row.get("解决路径", "")).strip()
        
        # 如果这行连案件名称或解决路径都没有，说明是无效空行，直接跳过
        if not case_name or not solution:
            continue
            
        # 🏆【最核心的一步】：把表格数据拼接成大模型最爱看的“结构化小作文”
        combined_text = (
            f"【参考类案】案件名称：{case_name}。\n"
            f"- 案由与劳方主张：{cause}，{claim}。\n"
            f"- 案件难点/执行困难：{difficulty}。\n"
            f"- 最终解决路径与经验：{solution}。"
        )
        
        documents_list.append(combined_text)
        ids_list.append(f"case_{counter}")
        counter += 1
        
    print(f"✅ Excel 读取完毕！成功将多列合并成了连贯的案例卷宗。")
else:
    print(f"❌ 找不到文件 {excel_filename}，请检查名字拼写！")

# ==========================================
# 任务三：把所有数据打包装入大模型知识库
# ==========================================
if len(documents_list) > 0:
    print(f"🚀 开始将总计 {len(documents_list)} 条知识注入向量数据库...")
    collection.add(
        documents=documents_list,
        ids=ids_list
    )
    print("🎉 数据注入大功告成！大模型现在的脑子里有完整的办案逻辑了！")
else:
    print("⚠️ 没有提取到任何有效数据，数据库未更新。")