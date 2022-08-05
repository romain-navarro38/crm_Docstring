from pathlib import Path

CUR_FILE = Path(__file__)
BASE_DIR = CUR_FILE.parent.parent.parent
DATA_FILE = BASE_DIR / "db_.sqlite3"
RESSOURCE_DIR = BASE_DIR / "ressource"


def get_style_sheet() -> str:
    with open(RESSOURCE_DIR / "combinear.qss", 'r') as f:
        style = f.read()
    return style
