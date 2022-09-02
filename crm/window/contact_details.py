import sys
from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtSql import QSqlDatabase, QSqlQueryModel
from PySide6.QtWidgets import QApplication, QWidget, QFormLayout, QLineEdit, QLabel, QDataWidgetMapper, QDateEdit, \
    QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QListWidget, QMessageBox

from crm.api.utils import DATA_FILE
from crm.window.list_item import CustomListWidgetItem
from crm.database.client import get_tag_to_category_group, get_tag_to_category_group_by_contact, \
    add_tag_group_at_contact, del_group_of_contact, update_contact, add_contact


# noinspection PyAttributeOutsideInit
class DetailsContact(QWidget):
    update_main_window = Signal()

    def __init__(self,
                 mode_action: str,
                 id_contact: int = 0):
        super().__init__()

        self.id_contact = id_contact
        self.mode_action = mode_action
        self.connect_db()
        self.setup_model()
        self.setup_ui()
        if mode_action == "modify":
            self.setWindowTitle("Editer un contact")
        else:
            self.setWindowTitle("Ajouter un contact")

    def connect_db(self):
        self.db = QSqlDatabase("QSQLITE")
        self.db.setDatabaseName(str(DATA_FILE))
        self.db.open()

    def setup_model(self):
        self.model = QSqlQueryModel()
        self.mapper = QDataWidgetMapper()
        self.mapper.setModel(self.model)

        query = f"""
            SELECT id, firstname, lastname, birthday, company, job 
            FROM contact 
            WHERE id={self.id_contact}
        """
        self.model.setQuery(query, db=self.db)

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.le_firstname = QLineEdit()
        self.le_lastname = QLineEdit()
        self.date_birthday = QDateEdit()
        self.le_company = QLineEdit()
        self.le_job = QLineEdit()
        self.lw_group = QListWidget()
        self.btn_validate = QPushButton("Valider")
        self.btn_cancel = QPushButton("Annuler")

    def modify_widgets(self):
        self.mapper.addMapping(self.le_firstname, 1)
        self.mapper.addMapping(self.le_lastname, 2)
        if self.mode_action == "modify":
            self.mapper.addMapping(self.date_birthday, 3)
        else:
            self.date_birthday.setDate(datetime(year=1899, month=12, day=31))
        self.mapper.addMapping(self.le_company, 4)
        self.mapper.addMapping(self.le_job, 5)
        self.mapper.toFirst()

        self.all_items = get_tag_to_category_group()
        contact_items, self.contact_ids = get_tag_to_category_group_by_contact(self.id_contact)
        for tag, id_tag in self.all_items:
            lw_item = CustomListWidgetItem(item=tag, idx=id_tag)
            if tag in contact_items:
                lw_item.checked
            else:
                lw_item.unchecked
            self.lw_group.addItem(lw_item)

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.contact_layout = QFormLayout()
        self.btn_layout = QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.contact_layout.addRow(QLabel("Prénom"), self.le_firstname)
        self.contact_layout.addRow(QLabel("Nom"), self.le_lastname)
        self.contact_layout.addRow(QLabel("Date de naissance"), self.date_birthday)
        self.contact_layout.addRow(QLabel("Société"), self.le_company)
        self.contact_layout.addRow(QLabel("Métier"), self.le_job)
        self.contact_layout.addRow(QLabel("Groupe"), self.lw_group)

        self.btn_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.btn_layout.addWidget(self.btn_validate)
        self.btn_layout.addWidget(self.btn_cancel)
        self.btn_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.main_layout.addLayout(self.contact_layout)
        self.main_layout.addLayout(self.btn_layout)

    def setup_connections(self):
        self.btn_validate.clicked.connect(self.save_changes)
        self.btn_cancel.clicked.connect(self.close)
        self.lw_group.itemClicked.connect(self.change_etat_group)

    def save_changes(self):
        if not self.check_data():
            return

        date = datetime.strptime(self.date_birthday.text(), "%d/%m/%Y")
        if self.mode_action == "modify":
            update_contact(id_contact=self.id_contact,
                           firstname=self.le_firstname.text().capitalize(),
                           lastname=self.le_lastname.text().upper(),
                           birthday=date.strftime("%Y-%m-%d"),
                           company=self.le_company.text(),
                           job=self.le_job.text())
        else:
            self.id_contact = add_contact(firstname=self.le_firstname.text().capitalize(),
                                          lastname=self.le_lastname.text().upper(),
                                          birthday=date.strftime("%Y-%m-%d"),
                                          company=self.le_company.text(),
                                          job=self.le_job.text())

        for item in [self.lw_group.item(i) for i in range(self.lw_group.count())]:
            if item.is_checked and item.id not in self.contact_ids:
                add_tag_group_at_contact(self.id_contact, item.id)
            elif not item.is_checked and item.id in self.contact_ids:
                del_group_of_contact(self.id_contact, item.id)
        self.update_main_window.emit()
        self.close()

    def check_data(self):
        if not self.le_firstname.text() and not self.le_lastname.text():
            msg = QMessageBox(self)
            msg.setWindowTitle("Incomplet")
            msg.setText("Veuillez renseigner un nom et/ou un prénom.")
            msg.setIcon(QMessageBox.Information)
            msg.exec()
            return False
        return True

    @staticmethod
    def change_etat_group(item):
        item.change_etat()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DetailsContact("modify", 10)
    window.show()
    app.exec()
