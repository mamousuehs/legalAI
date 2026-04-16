from pathlib import Path


def list_local_templates() -> list[Path]:
    template_root = Path(__file__).resolve().parents[1] / "templates" / "taoxin"
    return sorted(template_root.glob("*"))


if __name__ == "__main__":
    for path in list_local_templates():
        print(path)
