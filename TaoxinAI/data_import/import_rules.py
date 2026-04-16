from pathlib import Path


def get_rule_files() -> list[Path]:
    rule_root = Path(__file__).resolve().parents[1] / "templates" / "taoxin"
    return sorted(rule_root.glob("*rules*.yaml"))


if __name__ == "__main__":
    for path in get_rule_files():
        print(path)
