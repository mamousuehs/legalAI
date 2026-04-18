from pathlib import Path
import yaml

def get_rule_files() -> list[Path]:
    rule_root = Path(__file__).resolve().parents[1] / "templates" / "taoxin"
    return sorted(rule_root.glob("*rules*.yaml"))

def validate_rules():
    files = get_rule_files()
    if not files:
        print("⚠️ 未发现任何规则配置 (.yaml) 文件")
        return

    print(f"🔍 发现 {len(files)} 个规则文件，开始校验格式...")
    success_count = 0
    
    for path in files:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data is not None:
                    success_count += 1
                    print(f"  ✅ [通过] {path.name}")
        except yaml.YAMLError as e:
            print(f"  ❌ [失败] {path.name} 格式错误:\n    {e}")
        except Exception as e:
            print(f"  ❌ [错误] 无法读取 {path.name}: {e}")
            
    print(f"🎉 规则校验完成！通过: {success_count}/{len(files)}")

if __name__ == "__main__":
    validate_rules()
