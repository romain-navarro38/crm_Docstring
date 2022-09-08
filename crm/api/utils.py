"""Module qui gère le paramétrage de l'application : chemins, settings.json et fonctions de validations"""

import re
from pathlib import Path
from datetime import datetime
import json

CUR_FILE = Path(__file__)
BASE_DIR = CUR_FILE.parent.parent.parent
DATA_FILE = BASE_DIR / "db.sqlite3"
SETTINGS_FILE = BASE_DIR / "settings.json"
RESOURCE_DIR = BASE_DIR / "resource"

DEFAULT_SETTINGS = {
    "theme": "dark"
}

DEFAULT_TAGS = (
    {"tag": "Famille", "category": "group"},
    {"tag": "Collègue", "category": "group"},
    {"tag": "Personnel", "category": "phone"},
    {"tag": "Travail", "category": "phone"},
    {"tag": "Personnel", "category": "mail"},
    {"tag": "Travail", "category": "mail"},
    {"tag": "Domicile", "category": "address"},
    {"tag": "Travail", "category": "address"},
)


def get_light_style_sheet() -> str:
    """Retourne le contenu du fichier qss au style clair"""
    with open(RESOURCE_DIR / "light.qss", 'r') as f:
        style = f.read()
    return style


def get_dark_style_sheet() -> str:
    """Retourne le contenu du fichier qss au style sombre"""
    with open(RESOURCE_DIR / "combinear.qss", 'r') as f:
        style = f.read()
    return style


def check_settings():
    """Crée le fichier de paramètrage s'il n'existe pas et
    insère le paramètrage par défaut"""
    if not SETTINGS_FILE.exists():
        write_settings(DEFAULT_SETTINGS)


def write_settings(content: dict):
    """Ecrase le contenu du fichier de paramètrage par le contenu du paramètre content"""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(content, f, indent=4)


def read_settings() -> dict:
    """Retourne le contenu du fichier de paramètrage"""
    with open(SETTINGS_FILE, "r") as f:
        content = json.load(f)
    return content


def get_theme_application():
    """Recupère le contenu du fichier de style en rapport avec le paramètrage"""
    check_settings()
    settings = read_settings()
    theme = settings["theme"]
    if theme == "light":
        return get_light_style_sheet()
    elif theme == "dark":
        return get_dark_style_sheet()


def update_theme_setting(theme: str):
    """Mise à jour du dans le paramètrage du style à utiliser"""
    settings = read_settings()
    settings["theme"] = theme
    write_settings(settings)


def check_phone_number_format(number: str) -> bool:
    """Vérification du bon format d'un numéro de téléphone"""
    return bool(
        re.match(r"^(?:(?:\+|00)33[\s.-]{0,3}(?:\(0\)[\s.-]{0,3})?|0)"
                 r"[1-9](?:(?:[\s.-]?\d{2}){4}|\d{2}(?:[\s.-]?\d{3}){2})$",
                 number)
    )


def check_mail_format(mail: str) -> bool:
    """Vérification du bon format d'une adresse mail"""
    return bool(
        re.match(r'^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@'
                 r'((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$',
                 mail)
    )


def get_age_from_birthday(birthday: datetime) -> int:
    today = datetime.now()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))


if __name__ == '__main__':
    print(check_mail_format("aon.a38@gmail.com"))
