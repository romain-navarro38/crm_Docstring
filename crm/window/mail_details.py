import sys

from PySide6.QtCore import Signal
from PySide6.QtSql import QSqlDatabase, QSqlQueryModel
from PySide6.QtWidgets import QApplication, QWidget, QFormLayout, QLineEdit, QLabel, QDataWidgetMapper, QPushButton, \
    QVBoxLayout, QHBoxLayout, QComboBox, QSpacerItem, QSizePolicy

from crm.api.utils import DATA_FILE
from crm.database.client import update_mail, get_tag_to_category_mail, add_mail

db = QSqlDatabase("QSQLITE")
db.setDatabaseName(str(DATA_FILE))
db.open()


# noinspection PyAttributeOutsideInit
class DetailsMail(QWidget):
    update_main_window = Signal()

    def __init__(self,
                 id_mail: int,
                 mode_action: str,
                 id_contact: int = 0):
        super().__init__()

        self.id_mail = id_mail
        self.id_contact = id_contact
        self.mode_action = mode_action
        self.setup_model()
        self.setup_ui()
        self.setMinimumWidth(350)
        if mode_action == "modify":
            self.setWindowTitle("Modifier une adresse mail")
        else:
            self.setWindowTitle("Ajouter une adresse mail")

    def setup_model(self):
        self.model = QSqlQueryModel()
        self.mapper = QDataWidgetMapper()
        self.mapper.setModel(self.model)

        query = f"""
            SELECT id, mail, tag_id FROM mail
            WHERE id={self.id_mail}
        """
        self.model.setQuery(query, db=db)

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.le_mail = QLineEdit()
        self.cbx_tag = QComboBox()
        self.btn_validate = QPushButton("Valider")
        self.btn_cancel = QPushButton("Annuler")

    def modify_widgets(self):
        self.mapper.addMapping(self.le_mail, 1)
        self.mapper.toFirst()
        self.tags, self.idx = get_tag_to_category_mail()
        self.cbx_tag.addItems(self.tags)
        if self.mode_action == "modify":
            self.cbx_tag.setCurrentText(self.tags[self.idx.index(self.model.query().value(2))])

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.values_layout = QFormLayout()
        self.btn_layout = QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.values_layout.addRow(QLabel("Mail"), self.le_mail)
        self.values_layout.addRow(QLabel("Tag"), self.cbx_tag)

        self.btn_layout.addWidget(self.btn_validate)
        self.btn_layout.addWidget(self.btn_cancel)

        self.btn_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addLayout(self.values_layout)
        self.main_layout.addLayout(self.btn_layout)
        self.btn_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

    def setup_connections(self):
        self.btn_validate.clicked.connect(self.save_changes)
        self.btn_cancel.clicked.connect(self.close)

    def save_changes(self):
        id_tag = self.idx[self.tags.index(self.cbx_tag.currentText())]
        if self.mode_action == "modify":
            update_mail(self.le_mail.text(), id_tag, self.id_mail)
        else:
            add_mail(mail=self.le_mail.text(), contact_id=self.id_contact, tag_id=id_tag)
        self.update_main_window.emit()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DetailsMail(0, "adding", 1)
    window.show()
    app.exec()
