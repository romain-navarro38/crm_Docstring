import sys

from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication

from crm.window.basic import MainWindow
from crm.api.utils import RESOURCE_DIR, get_theme_application


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(QPixmap(RESOURCE_DIR / "book_address.ico")))
    app.setStyleSheet(get_theme_application())
    window = MainWindow(app)
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
