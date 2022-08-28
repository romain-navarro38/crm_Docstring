import sys

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel


# noinspection PyAttributeOutsideInit
class About(QWidget):
    def __init__(self):
        super().__init__()

        self.setup_ui()
        self.setWindowTitle("A propos crmDostring")

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.la_about = QLabel()
        self.btn_ok = QPushButton("OK")

    def modify_widgets(self):
        self.la_about.setWordWrap(True)
        text = """
        crmDocstring by Rocket
        https://github.com/romain-navarro38
        
        PySide6 v6.3.1
        Pillow v9.2.0
        
        icons :
            Yaicon - Basic ui
            https://creativecommons.org/licenses/by/4.0/
            https://www.iconfinder.com/yaicon90
        
            Yusuke Kamiyamane - Fugue Icons
            http://creativecommons.org/licenses/by/3.0/
            http://p.yusukekamiyamane.com
            
            Arief Mochjiyat - User interface
            https://creativecommons.org/licenses/by/4.0/
            https://dribbble.com/AriefMoch
        """
        self.la_about.setText(text)

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.la_about)
        self.main_layout.addWidget(self.btn_ok)

    def setup_connections(self):
        self.btn_ok.clicked.connect(self.close)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = About()
    window.show()
    app.exec()
