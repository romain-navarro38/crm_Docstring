"""Module générant la fenêtre 'A propos'"""

import sys

from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QHBoxLayout

TEXTS = [
    {"text": "crmDocstring by Rocket - <a href=https://github.com/romain-navarro38>github</a>",
     "link": True,
     "indent": False,
     "space": True},
    {"text": "Langage de programmation :",
     "link": False,
     "indent": False,
     "space": False},
    {"text": "Python v3.10.5",
     "link": False,
     "indent": True,
     "space": True},
    {"text": "Librairies tiers :",
     "link": False,
     "indent": False,
     "space": False},
    {"text": "PySide6 v6.3.1\nPillow v9.2.0\nUnidecode v1.3.4",
     "link": False,
     "indent": True,
     "space": True},
    {"text": "Icones :",
     "link": False,
     "indent": False,
     "space": False},
    {"text": "<a href=https://www.iconfinder.com/yaicon90>Yaicon - Basic ui</a> - CC BY 4.0 <br /> "
             "<a href=http://p.yusukekamiyamane.com>Yusuke Kamiyamane - Fugue Icons</a> - CC BY 3.0 <br /> "
             "<a href=https://www.iconfinder.com/arief_moch>Arief Mochjiyat - User interface</a> - CC BY 4.0",
     "link": True,
     "indent": True,
     "space": False}
]


# noinspection PyAttributeOutsideInit
class About(QWidget):
    def __init__(self):
        super().__init__()

        self.setup_ui()
        self.setWindowTitle("A propos crmDocstring")

    def setup_ui(self):
        self.create_layouts()
        self.create_and_add_widgets_to_layouts()
        self.setup_connections()

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.btn_layout = QHBoxLayout()

    def create_and_add_widgets_to_layouts(self):
        for params in TEXTS:
            label = QLabel(params["text"])
            if params["link"]:
                label.setOpenExternalLinks(True)
            if params["indent"]:
                label.setIndent(25)
            self.main_layout.addWidget(label)
            if params["space"]:
                self.main_layout.addItem(QSpacerItem(0, 15, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.btn_ok = QPushButton("Fermer")
        self.btn_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.btn_layout.addWidget(self.btn_ok)
        self.btn_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addLayout(self.btn_layout)

    def setup_connections(self):
        self.btn_ok.clicked.connect(self.close)


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = About()
    window.show()
    sys.exit(app.exec())
