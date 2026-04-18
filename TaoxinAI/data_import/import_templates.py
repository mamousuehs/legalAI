from pathlib import Path
import yaml

def list_local_templates() -> list[Path]:
    template_root = Path(__file__).resolve().parents[1] / "templates" / "taoxin"
    return sorted(template_root.glob("*"))

def validate_templates():
    files = [f for f in list_local_templates() if f.is_file()]
    if not files:
        print("⚠️ 未发现任何模板文件")
        return

    print(f"🔍 发现 {len(files)} 个模板文件，开始校验...")
    
    for path in files:
        ext = path.suffix.lower()
        try:
            if ext == '.yaml' or ext == '.yml':
                with open(path, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
                print(f"  ✅ [YAML 通过] {path.name}")
            elif ext == '.txt' or ext == '.md':
                with open(path, 'r', encoding='utf-8') as f:
                    f.read()
                print(f"  ✅ [文本 通过] {path.name}")
            else:
                print(f"  ⏩ [跳过] {path.name} (不支持的类型)")
        except Exception as e:
            print(f"  ❌ [读取失败] {path.name}: {e}")
            
    print("🎉 模板文件扫描完毕！")

if __name__ == "__main__":
    validate_templates()
