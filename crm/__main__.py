"""Module contenant le point d'entrée principal de l'application."""

import sys

from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication

from crm.database.client import init_database_structure, init_database_tag
from crm.window.main_window import Crm
from crm.api.utils import RESOURCE_DIR, get_theme_application, DATA_FILE


def check_start():
    """Vérifie la présence d'une base de données.
    La crée et lui insére des données par défauts si elle n'existe pas."""
    if not DATA_FILE.exists():
        init_database_structure()
        init_database_tag()


def main():
    """Point d'entrée de l'application."""
    check_start()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(QPixmap(RESOURCE_DIR / "book_address.ico")))
    app.setStyleSheet(get_theme_application())
    window = Crm(app)
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
