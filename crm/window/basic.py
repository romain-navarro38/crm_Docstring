import sys
import sqlite3
from datetime import datetime

from PySide6.QtCore import QSize, QModelIndex, Qt
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QPalette
from PySide6.QtSql import QSqlDatabase, QSqlQueryModel
from PySide6.QtWidgets import QApplication, QWidget, QTableView, QGridLayout, QHeaderView, QLineEdit, QLabel, \
    QAbstractItemView, QVBoxLayout, QFormLayout, QHBoxLayout
from PIL import Image

from crm.api.utils import DATA_FILE, RESSOURCE_DIR, get_style_sheet

db = QSqlDatabase("QSQLITE")
db.setDatabaseName(str(DATA_FILE))
db.open()


def get_age_from_birthday(birthday: datetime) -> int:
    today = datetime.today()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))


def get_contact_information(id_contact: int) -> tuple:
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    d = {"id_contact": id_contact}
    c.execute("SELECT profile_picture, birthday, company, job FROM contact WHERE id=:id_contact", d)
    data = c.fetchone()
    conn.close()
    return data


def get_contact_group(id_contact: int) -> str:
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    d = {"id_contact": id_contact}
    c.execute("SELECT tag FROM tag INNER JOIN group_ ON tag.id = group_.tag_id WHERE group_.contact_id=:id_contact", d)
    data = c.fetchall()
    conn.close()
    return ", ".join([d[0] for d in data])


def create_background_picture(color):
    bg = Image.new('RGB', (128, 128), color)
    bg.save(RESSOURCE_DIR / "bg.png", 'PNG')


class ProfilePicture(QLabel):
    def __init__(self, path_image, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMaximumSize(128, 128)
        self.setMinimumSize(128, 128)
        self.radius = 64

        self.setAutoFillBackground(True)
        self.target = QPixmap(self.size())
        self.target.fill(Qt.transparent)

        self.set_image(path_image=path_image)

    def set_image(self, path_image):
        p = QPixmap(path_image).scaled(
            128, 128, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        painter = QPainter(self.target)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius, Qt.AbsoluteSize)

        painter.setClipPath(path)
        painter.drawPixmap(0, 0, p)
        self.setPixmap(self.target)


class TableViewCustom(QTableView):
    def __init__(self,
                 model: QSqlQueryModel,
                 header_stretch: str):
        super().__init__()

        self.setModel(model)
        self.verticalHeader().setHidden(True)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        if header_stretch == "all":
            self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        elif header_stretch == "last":
            self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionHidden(0, True)


# noinspection PyAttributeOutsideInit
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(QSize(1024, 512))
        self.setup_model()
        self.setup_ui()
        self.background_color = None

    def setup_model(self):
        self.model_contact = QSqlQueryModel()
        self.query = 'SELECT id, firstname, surname FROM contact'
        self.model_contact.setQuery(self.query, db=db)
        self.model_phone = QSqlQueryModel()
        self.model_mail = QSqlQueryModel()
        self.model_address = QSqlQueryModel()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.le_search = QLineEdit()
        self.tv_contact = TableViewCustom(model=self.model_contact, header_stretch="all")
        self.tv_phone = TableViewCustom(model=self.model_phone, header_stretch="last")
        self.tv_mail = TableViewCustom(model=self.model_mail, header_stretch="last")
        self.la_profile_picture = ProfilePicture(r"C:\Users\Romain\Projet\crm_Docstring\ressource\pp_00000.png")
        self.la_birthday = QLabel("Date de naissance :")
        self.la_birthday_value = QLabel("")
        self.la_company = QLabel("Société :")
        self.la_company_value = QLabel("")
        self.la_job = QLabel("Poste :")
        self.la_job_value = QLabel("")
        self.la_group = QLabel("Groupe :")
        self.la_group_value = QLabel("")
        self.tv_address = TableViewCustom(model=self.model_address, header_stretch="last")

    def modify_widgets(self):
        self.le_search.setPlaceholderText("Rechercher...")

    def create_layouts(self):
        self.main_layout = QGridLayout(self)
        self.other_layout = QVBoxLayout()
        self.profile_picture_layout = QHBoxLayout()
        self.information_layout = QFormLayout()

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.le_search, 0, 0, 1, 3)
        self.main_layout.addWidget(self.tv_contact, 1, 0, 2, 1)
        self.main_layout.addWidget(self.tv_phone, 1, 1, 1, 1)
        self.main_layout.addWidget(self.tv_mail, 1, 2, 1, 1)
        self.main_layout.addLayout(self.other_layout, 2, 1, 1, 1)
        self.main_layout.addWidget(self.tv_address, 2, 2, 1, 1)

        self.other_layout.addLayout(self.profile_picture_layout)
        self.profile_picture_layout.addWidget(self.la_profile_picture)
        self.other_layout.addLayout(self.information_layout)
        self.information_layout.addRow(self.la_birthday, self.la_birthday_value)
        self.information_layout.addRow(self.la_company, self.la_company_value)
        self.information_layout.addRow(self.la_job, self.la_job_value)
        self.information_layout.addRow(self.la_group, self.la_group_value)

    def setup_connections(self):
        self.tv_contact.selectionModel().currentRowChanged.connect(self.update_other_tableview)
        self.le_search.textChanged.connect(self.update_tv_contact)

    def update_tv_contact(self):
        if search := self.le_search.text():
            self.query = f'''SELECT DISTINCT contact.id, firstname, surname FROM contact 
                             LEFT OUTER JOIN mail ON contact.id = mail.contact_id 
                             LEFT OUTER JOIN phone ON contact.id = phone.contact_id 
                             LEFT OUTER JOIN address ON contact.id = address.contact_id 
                             LEFT OUTER JOIN group_ ON contact.id = group_.contact_id 
                             LEFT OUTER JOIN tag ON group_.tag_id = tag.id 
                             WHERE surname LIKE "%{search}%" 
                             OR firstname LIKE "%{search}%" 
                             OR mail LIKE "%{search}%" 
                             OR number LIKE "%{search}%" 
                             OR address LIKE "%{search}%" 
                             OR tag LIKE "%{search}%"'''
        else:
            self.query = 'SELECT id, firstname, surname FROM contact'

        self.model_contact.setQuery(self.query, db=db)
        self.update_other_tableview(self.tv_contact.currentIndex())

    def update_other_tableview(self, selected: QModelIndex):
        row = selected.row()
        selectedRowIndex = self.tv_contact.currentIndex()
        id_contact = selectedRowIndex.sibling(row, 0).data()

        informations = get_contact_information(id_contact=id_contact)
        if not informations:
            return

        if file_picture := informations[0]:
            if not self.background_color:
                self.background_color = self.palette().color(QPalette.Window).toTuple()
                create_background_picture(self.background_color)
            self.la_profile_picture.set_image(RESSOURCE_DIR / "bg.png")
            self.la_profile_picture.set_image(file_picture)

        if birthday := informations[1]:
            birthday = datetime.strptime(birthday, '%Y-%m-%d')
            age = get_age_from_birthday(birthday)
            self.la_birthday_value.setText(f"{birthday.strftime('%d/%m/%Y')} ({age} ans)")
        else:
            self.la_birthday_value.setText("")

        if company := informations[2]:
            self.la_company_value.setText(company)
        else:
            self.la_company_value.setText("")

        if job := informations[3]:
            self.la_job_value.setText(job)
        else:
            self.la_job_value.setText("")

        self.la_group_value.setText(get_contact_group(id_contact))

        self.query = f'''SELECT tag, number FROM phone 
                         INNER JOIN tag ON phone.tag_id = tag.id 
                         WHERE contact_id = {id_contact}'''
        self.model_phone.setQuery(self.query, db=db)

        query = f'''SELECT tag, mail FROM mail 
                    INNER JOIN tag ON mail.tag_id = tag.id 
                    WHERE contact_id = {id_contact}'''
        self.model_mail.setQuery(query, db=db)

        query = f'''SELECT tag, address FROM address 
                    INNER JOIN tag ON address.tag_id = tag.id 
                    WHERE contact_id = {id_contact}'''
        self.model_address.setQuery(query, db=db)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(get_style_sheet())
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
