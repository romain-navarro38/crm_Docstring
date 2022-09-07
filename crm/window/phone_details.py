import sys

from PySide6.QtCore import Signal
from PySide6.QtSql import QSqlDatabase, QSqlQueryModel
from PySide6.QtWidgets import QApplication, QWidget, QFormLayout, QLineEdit, QLabel, QDataWidgetMapper, QPushButton, \
    QVBoxLayout, QHBoxLayout, QComboBox, QSpacerItem, QSizePolicy, QMessageBox

from crm.api.utils import DATA_FILE, check_phone_number_format
from crm.database.client import update_number_phone, get_tag_to_category_phone, add_phone


class MessageConfirm(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Confirmation")
        self.setText("Ce format n'est pas valide.\nVoulez-vous quand même l'enregistrer ?")
        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        btn_yes = self.button(QMessageBox.Yes)
        btn_yes.setText('Oui')
        btn_no = self.button(QMessageBox.No)
        btn_no.setText('Non')
        self.setIcon(QMessageBox.Icon.Question)


# noinspection PyAttributeOutsideInit
class DetailsPhone(QWidget):
    update_main_window = Signal()

    def __init__(self,
                 id_phone: int,
                 mode_action: str,
                 id_contact: int = 0):
        super().__init__()

        self.id_phone = id_phone
        self.id_contact = id_contact
        self.mode_action = mode_action
        self.connect_db()
        self.setup_model()
        self.setup_ui()
        self.setMinimumWidth(350)
        if self.mode_action == "modify":
            self.setWindowTitle("Modifier un numéro de téléphone")
        else:
            self.setWindowTitle("Ajouter un numéro de téléphone")

    def connect_db(self):
        self.db = QSqlDatabase("QSQLITE")
        self.db.setDatabaseName(str(DATA_FILE))
        self.db.open()

    def setup_model(self):
        self.model = QSqlQueryModel()
        self.mapper = QDataWidgetMapper()
        self.mapper.setModel(self.model)

        query = f"""
            SELECT id, number, tag_id FROM phone
            WHERE id={self.id_phone}
        """
        self.model.setQuery(query, db=self.db)

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.le_number = QLineEdit()
        self.cbx_tag = QComboBox()
        self.btn_validate = QPushButton("Valider")
        self.btn_cancel = QPushButton("Annuler")

    def modify_widgets(self):
        self.mapper.addMapping(self.le_number, 1)
        self.mapper.toFirst()
        self.tags, self.idx = get_tag_to_category_phone()
        self.cbx_tag.addItems(self.tags)
        if self.mode_action == "modify":
            self.cbx_tag.setCurrentText(self.tags[self.idx.index(self.model.query().value(2))])

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.values_layout = QFormLayout()
        self.btn_layout = QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.values_layout.addRow(QLabel("Numéro"), self.le_number)
        self.values_layout.addRow(QLabel("Tag"), self.cbx_tag)

        self.btn_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.btn_layout.addWidget(self.btn_validate)
        self.btn_layout.addWidget(self.btn_cancel)
        self.btn_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.main_layout.addLayout(self.values_layout)
        self.main_layout.addLayout(self.btn_layout)

    def setup_connections(self):
        self.btn_validate.clicked.connect(self.save_changes)
        self.btn_cancel.clicked.connect(self.close)

    def save_changes(self):
        if not self.validate_phone():
            return False

        id_tag = self.idx[self.tags.index(self.cbx_tag.currentText())]
        if self.mode_action == "modify":
            update_number_phone(self.le_number.text(), id_tag, self.id_phone)
        else:
            add_phone(number=self.le_number.text(), contact_id=self.id_contact, tag_id=id_tag)
        self.update_main_window.emit()
        self.close()

    def validate_phone(self):
        if not self.le_number.text():
            return False

        if not check_phone_number_format(self.le_number.text()):
            msg = MessageConfirm()
            button = msg.exec()
            button = QMessageBox.StandardButton(button)
            if button == QMessageBox.StandardButton.No:
                return False

        return True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DetailsPhone(1)
    window.show()
    app.exec()
