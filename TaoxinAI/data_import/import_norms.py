from pathlib import Path


LEGACY_BACKEND_DIR = Path(__file__).resolve().parents[2] / "huxin_backend"


def get_legacy_norm_source() -> Path:
    """Returns the legacy wage-recovery norm document path."""

    return LEGACY_BACKEND_DIR / "法条适用.docx"


if __name__ == "__main__":
    path = get_legacy_norm_source()
    print(f"legacy norm source: {path}")
