import chromadb
import pandas as pd
from docx import Document
import os

print("🔌 正在连接本地知识库...")
chroma_client = chromadb.PersistentClient(path="./legal_db")
collection = chroma_client.get_or_create_collection(name="laws")

# 准备两个空纸箱，用来装整理好的文本和对应的编号
documents_list = []
ids_list = []
counter = 0

# ==========================================
# 任务一：吃掉 Word 里的法条
# ==========================================
word_filename = "法条适用.docx"  # ⚠️如果你的文件名不同，请在这里修改
print(f"📖 正在读取 Word 文件：{word_filename}...")

if os.path.exists(word_filename):
    doc = Document(word_filename)
    # 逐段读取 Word 里的文字
    for para in doc.paragraphs:
        text = para.text.strip()
        # 过滤掉空格和太短的无意义标题（比如少于10个字的段落）
        if len(text) > 10: 
            # 给法条加上标签，方便大模型区分
            documents_list.append(f"【法律规范】{text}")
            ids_list.append(f"law_{counter}")
            counter += 1
    print(f"✅ Word 读取完毕！提取了 {counter} 段法律规范。")
else:
    print(f"❌ 找不到文件 {word_filename}，请检查名字拼写！")

# ==========================================
# 任务二：吃掉 Excel 里的案例
# ==========================================
excel_filename = "涉欠薪典型案例汇总.xlsx" # ⚠️如果你的文件名不同，请在这里修改
print(f"📊 正在读取 Excel 文件：{excel_filename}...")

if os.path.exists(excel_filename):
    df = pd.read_excel(excel_filename)
    
    # ⚠️【关键修改点】：你需要看一下法学同学 Excel 里的表头叫什么名字
    # 假设记录案情的那一列叫 "案情摘要"（请替换成真实的表头名字）
    column_name = "案情摘要" 
    
    if column_name in df.columns:
        case_texts = df[column_name].dropna().astype(str).tolist()
        for text in case_texts:
            documents_list.append(f"【参考类案】{text}")
            ids_list.append(f"case_{counter}")
            counter += 1
        print(f"✅ Excel 读取完毕！提取了 {len(case_texts)} 个案例。")
    else:
        print(f"❌ Excel 里找不到叫【{column_name}】的列，请修改代码里的列名！")
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
    print("🎉 数据注入大功告成！大模型现在可以引经据典了！")
else:
    print("⚠️ 没有提取到任何有效数据，数据库未更新。")