from pathlib import Path


LEGACY_BACKEND_DIR = Path(__file__).resolve().parents[2] / "huxin_backend"


def get_legacy_case_source() -> Path:
    """Returns the legacy wage-recovery case spreadsheet path."""

    return LEGACY_BACKEND_DIR / "涉欠薪典型案例汇总.xlsx"


if __name__ == "__main__":
    path = get_legacy_case_source()
    print(f"legacy case source: {path}")
