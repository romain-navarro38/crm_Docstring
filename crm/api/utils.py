from pathlib import Path
import json

CUR_FILE = Path(__file__)
BASE_DIR = CUR_FILE.parent.parent.parent
DATA_FILE = BASE_DIR / "db_.sqlite3"
SETTINGS_FILE = BASE_DIR / "settings.json"
RESOURCE_DIR = BASE_DIR / "resource"

DEFAULT_SETTINGS = {
    "theme": "light"
}


def get_light_style_sheet() -> str:
    with open(RESOURCE_DIR / "light.qss", 'r') as f:
        style = f.read()
    return style


def get_dark_style_sheet() -> str:
    with open(RESOURCE_DIR / "combinear.qss", 'r') as f:
        style = f.read()
    return style


def check_settings():
    if not SETTINGS_FILE.exists():
        write_settings(DEFAULT_SETTINGS)


def write_settings(content: dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(content, f, indent=4)


def read_settings() -> dict:
    with open(SETTINGS_FILE, "r") as f:
        content = json.load(f)
    return content


def get_theme_application():
    check_settings()
    settings = read_settings()
    theme = settings["theme"]
    if theme == "light":
        return get_light_style_sheet()
    elif theme == "dark":
        return get_dark_style_sheet()


def update_theme_setting(theme: str):
    settings = read_settings()
    settings["theme"] = theme
    write_settings(settings)
