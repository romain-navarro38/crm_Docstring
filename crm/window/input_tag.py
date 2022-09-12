from unidecode import unidecode
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QLabel, QListWidget, QPushButton, QHBoxLayout, QSpacerItem, \
    QSizePolicy, QMessageBox, QLineEdit, QVBoxLayout, QComboBox

from crm.window.list_item import CustomListWidgetItem


def check_tag(tag: str, widget) -> bool:
    """Vérifie si un tag existe déjà dans le Widget"""
    if isinstance(widget, QComboBox):
        tags = [unidecode(widget.itemText(i)).lower() for i in range(widget.count())]
    elif isinstance(widget, QListWidget):
        tags = [unidecode(widget.item(i).text()).lower() for i in range(widget.count())]
    return bool(tag and unidecode(tag).lower() not in tags)


# noinspection PyAttributeOutsideInit
class InputTag(QWidget):
    """Fenêtre permettant l'ajout ou la modification d'un tag après vérifications"""
    save_tag = Signal(str)

    def __init__(self,
                 parent: QWidget,
                 mode_action: str,
                 category: str,
                 old_tag: CustomListWidgetItem = None):
        super().__init__()

        self.parent = parent
        self.mode_action = mode_action
        self.category = category
        self.old_tag = old_tag
        if mode_action == "modify":
            self.setWindowTitle("Modifier un tag")
        else:
            self.setWindowTitle("Ajouter un tag")
        self.resize(300, 75)
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.la_prompt = QLabel("Nouveau tag :")
        self.le_tag = QLineEdit()
        self.btn_validate = QPushButton("Valider")
        self.btn_cancel = QPushButton("Annuler")

    def modify_widgets(self):
        if self.mode_action == "modify":
            self.le_tag.setText(self.old_tag.text())

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.tag_layout = QHBoxLayout()
        self.btn_layout = QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.tag_layout.addWidget(self.la_prompt)
        self.tag_layout.addWidget(self.le_tag)
        self.btn_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.btn_layout.addWidget(self.btn_validate)
        self.btn_layout.addWidget(self.btn_cancel)
        self.main_layout.addLayout(self.tag_layout)
        self.main_layout.addLayout(self.btn_layout)

    def setup_connections(self):
        self.btn_validate.clicked.connect(self.save_input_user)
        self.btn_cancel.clicked.connect(self.close)

    def save_input_user(self):
        """Enregistrement en bdd d'un tag après sa vérification."""
        if self.parent.objectName() == "tag":
            widget = self.parent.findChild(QListWidget, self.category)
        elif self.parent.objectName() == "details":
            widget = self.parent.findChild(QComboBox, self.category)
        if not check_tag(self.le_tag.text(), widget):
            msg = QMessageBox(self)
            msg.setWindowTitle("Erreur")
            msg.setText("Tag invalide")
            msg.setIcon(QMessageBox.Critical)
            msg.exec()
            return

        new_tag = self.le_tag.text().capitalize()
        self.save_tag.emit(new_tag)
        self.close()
