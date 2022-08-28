import sys

from PySide6.QtCore import Signal
from PySide6.QtSql import QSqlDatabase, QSqlQueryModel
from PySide6.QtWidgets import QApplication, QWidget, QFormLayout, QLineEdit, QLabel, QDataWidgetMapper, QPushButton, \
    QVBoxLayout, QHBoxLayout, QComboBox

from crm.api.utils import DATA_FILE
from crm.database.client import update_address, add_address, get_tag_to_category_address

db = QSqlDatabase("QSQLITE")
db.setDatabaseName(str(DATA_FILE))
db.open()


# noinspection PyAttributeOutsideInit
class DetailsAddress(QWidget):
    update_main_window = Signal()

    def __init__(self,
                 id_address: int,
                 mode_action: str,
                 id_contact: int = 0):
        super().__init__()

        self.id_address = id_address
        self.id_contact = id_contact
        self.mode_action = mode_action
        self.setup_model()
        self.setup_ui()
        self.setMinimumWidth(350)
        if self.mode_action == "modify":
            self.setWindowTitle("Modifier une adresse")
        else:
            self.setWindowTitle("Ajouter une adresse")

    def setup_model(self):
        self.model = QSqlQueryModel()
        self.mapper = QDataWidgetMapper()
        self.mapper.setModel(self.model)

        query = f"""
            SELECT id, address, tag_id FROM address
            WHERE id={self.id_address}
        """
        self.model.setQuery(query, db=db)

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.le_address = QLineEdit()
        self.cbx_tag = QComboBox()
        self.btn_validate = QPushButton("Valider")
        self.btn_cancel = QPushButton("Annuler")

    def modify_widgets(self):
        self.mapper.addMapping(self.le_address, 1)
        self.mapper.toFirst()
        self.tags, self.idx = get_tag_to_category_address()
        self.cbx_tag.addItems(self.tags)
        if self.mode_action == "modify":
            self.cbx_tag.setCurrentText(self.tags[self.idx.index(self.model.query().value(2))])

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.values_layout = QFormLayout()
        self.btn_layout = QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.values_layout.addRow(QLabel("Adresse"), self.le_address)
        self.values_layout.addRow(QLabel("Tag"), self.cbx_tag)

        self.btn_layout.addWidget(self.btn_validate)
        self.btn_layout.addWidget(self.btn_cancel)

        self.main_layout.addLayout(self.values_layout)
        self.main_layout.addLayout(self.btn_layout)

    def setup_connections(self):
        self.btn_validate.clicked.connect(self.save_changes)
        self.btn_cancel.clicked.connect(self.close)

    def save_changes(self):
        id_tag = self.idx[self.tags.index(self.cbx_tag.currentText())]
        if self.mode_action == "modify":
            update_address(self.le_address.text(), id_tag, self.id_address)
        else:
            add_address(address=self.le_address.text(), contact_id=self.id_contact, tag_id=id_tag)
        self.update_main_window.emit()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DetailsAddress(0, "adding", 1)
    window.show()
    app.exec()
