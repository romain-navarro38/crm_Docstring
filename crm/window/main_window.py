import shutil
from datetime import datetime
from functools import partial
from pathlib import Path

from PySide6.QtCore import QSize, QModelIndex, Qt, Signal, QSortFilterProxyModel
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QPalette, QAction, QIcon, QKeySequence
from PySide6.QtSql import QSqlDatabase, QSqlQueryModel
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QTableView, QGridLayout, QHeaderView, QLineEdit, \
    QLabel, QAbstractItemView, QVBoxLayout, QFormLayout, QHBoxLayout, QMenuBar, QMenu, QPushButton, QMessageBox, \
    QSpacerItem, QSizePolicy, QFileDialog
from PIL import Image

from crm.api.utils import DATA_FILE, RESOURCE_DIR, get_dark_style_sheet, update_theme_setting, get_light_style_sheet, \
    get_age_from_birthday
from crm.window.contact_details import DetailsContact
from crm.window.phone_details import DetailsPhone
from crm.window.mail_details import DetailsMail
from crm.window.address_details import DetailsAddress
from crm.window.tag import Tag
from crm.window.about import About
from crm.database.client import QUERY_PHONE, QUERY_MAIL, QUERY_ADDRESS, del_contact_by_id, del_address_by_id, \
    del_mail_by_id, del_phone_by_id, update_profil_picture, get_contact_informations, get_contact_group

column_titles = {
    "phone": "Téléphone",
    "mail": "Mail",
    "address": "Adresse"
}


def create_background_picture(color: tuple[int]):
    """Enregistre dans le dossier resources une image png de la couleur passé en paramètre."""
    bg = Image.new('RGB', (128, 128), color)
    bg.save(RESOURCE_DIR / "bg.png", 'PNG')


class ProfilePicture(QLabel):
    """Génére une image ronde dans un QLabel"""
    doubleClicked = Signal()

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

    def mouseDoubleClickEvent(self, ev):
        self.doubleClicked.emit()


class CustomTableView(QTableView):
    """Personnalisation des QTableView"""
    def __init__(self,
                 name: str,
                 model: QSqlQueryModel,
                 header_stretch: str):
        super().__init__()

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(model)
        self.setModel(proxy_model)
        self.setSortingEnabled(True)
        self.sortByColumn(1, Qt.AscendingOrder)
        self.verticalHeader().setHidden(True)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        if header_stretch == "all":
            self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        elif header_stretch == "last":
            self.horizontalHeader().setStretchLastSection(True)
        self.hide_first_column()
        self.setObjectName(name)

        match name:
            case "contact":
                self.model().setHeaderData(1, Qt.Orientation.Horizontal, "Prénom")
                self.model().setHeaderData(2, Qt.Orientation.Horizontal, "Nom")
            case _:
                self.model().setHeaderData(1, Qt.Orientation.Horizontal, "Tag")
                self.model().setHeaderData(2, Qt.Orientation.Horizontal, column_titles[name])

    def hide_first_column(self):
        self.horizontalHeader().setSectionHidden(0, True)


class MessageDelete(QMessageBox):
    """Message de demande de confirmation avant la suppression d'une donnée."""
    def __init__(self, type_data: str, *args: str):
        super().__init__()
        self.setWindowTitle("Confirmation")

        match type_data:
            case "contact":
                text = "Etes-vous sur de vouloir supprimer le contact "
            case "phone":
                text = "Etes-vous sur de vouloir supprimer le numéro "
            case "mail":
                text = "Etes-vous sur de vouloir supprimer l'adresse mail "
            case "address":
                text = "Etes-vous sur de vouloir supprimer l'adresse "
        text += " ".join(args)
        self.setText(text)
        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        btn_yes = self.button(QMessageBox.Yes)
        btn_yes.setText('Oui')
        btn_no = self.button(QMessageBox.No)
        btn_no.setText('Non')
        self.setIcon(QMessageBox.Icon.Warning)


# noinspection PyAttributeOutsideInit
class Crm(QMainWindow):
    """Fenêtre principale de l'application"""
    def __init__(self, parent: QApplication):
        super().__init__()

        self.parent = parent
        self.theme = None
        self.background_color = None
        self.setMinimumSize(QSize(1024, 512))
        self.connect_db()
        self.setup_model()
        self.setup_menu()
        self.setup_ui()
        self.setWindowTitle("CRM Docstring by Rocket")

    def connect_db(self):
        self.db = QSqlDatabase("QSQLITE")
        self.db.setDatabaseName(str(DATA_FILE))
        self.db.open()

    def setup_model(self):
        self.model_contact = QSqlQueryModel()
        self.query_contact = 'SELECT id, firstname, lastname FROM contact'
        self.model_contact.setQuery(self.query_contact, db=self.db)
        self.model_phone = QSqlQueryModel()
        self.query_phone = QUERY_PHONE.format(id=0)
        self.model_phone.setQuery(self.query_phone, db=self.db)
        self.model_mail = QSqlQueryModel()
        self.query_mail = QUERY_MAIL.format(id=0)
        self.model_mail.setQuery(self.query_mail, db=self.db)
        self.model_address = QSqlQueryModel()
        self.query_address = QUERY_ADDRESS.format(id=0)
        self.model_address.setQuery(self.query_address, db=self.db)

    def setup_menu(self):
        self.menu = QMenuBar(self)

        self.menu_contact = QMenu(self.menu, title="&Contact")
        self.action_editing = QAction(self, text="&Editer")
        self.action_editing.setShortcut(QKeySequence("Ctrl+e"))
        self.action_editing.setIcon(QIcon(QPixmap(RESOURCE_DIR / "pencil.png")))
        self.action_editing.triggered.connect(self.distribution_editing_action)
        self.menu_insertion = QMenu(self.menu_contact, title="&Ajouter")
        self.menu_insertion.setIcon(QIcon(QPixmap(RESOURCE_DIR / "plus.png")))
        self.action_add_contact = QAction(self, text="&Contact")
        self.action_add_contact.setIcon(QIcon(QPixmap(RESOURCE_DIR / "users.png")))
        self.action_add_contact.triggered.connect(partial(self.open_details_contact, "adding"))
        self.action_add_contact.setShortcut(QKeySequence("Ctrl+n"))
        self.action_add_phone = QAction(self, text="&Téléphone")
        self.action_add_phone.setIcon(QIcon(QPixmap(RESOURCE_DIR / "mobile-phone.png")))
        self.action_add_phone.triggered.connect(partial(self.open_details_phone, "adding"))
        self.action_add_phone.setShortcut(QKeySequence("Ctrl+t"))
        self.action_add_mail = QAction(self, text="&Mail")
        self.action_add_mail.setIcon(QIcon(QPixmap(RESOURCE_DIR / "at-sign.png")))
        self.action_add_mail.triggered.connect(partial(self.open_details_mail, "adding"))
        self.action_add_mail.setShortcut(QKeySequence("Ctrl+m"))
        self.action_add_address = QAction(self, text="&Adresse")
        self.action_add_address.setIcon(QIcon(QPixmap(RESOURCE_DIR / "map-pin.png")))
        self.action_add_address.triggered.connect(partial(self.open_details_address, "adding"))
        self.action_add_address.setShortcut(QKeySequence("Ctrl+a"))
        self.action_deleting = QAction(self, text="&Supprimer")
        self.action_deleting.setShortcut(QKeySequence("Del"))
        self.action_deleting.triggered.connect(self.distribution_deleting_action)
        self.action_deleting.setIcon(QIcon(QPixmap(RESOURCE_DIR / "cross.png")))
        self.menu.addAction(self.menu_contact.menuAction())
        self.menu_contact.addAction(self.action_editing)
        self.menu_contact.addAction(self.menu_insertion.menuAction())
        self.menu_insertion.addAction(self.action_add_contact)
        self.menu_insertion.addAction(self.action_add_phone)
        self.menu_insertion.addAction(self.action_add_mail)
        self.menu_insertion.addAction(self.action_add_address)
        self.menu_contact.addAction(self.action_deleting)

        self.menu_tag = QMenu(self.menu, title="&Tag")
        self.action_tag = QAction(self, text="&Gestion")
        self.action_tag.setShortcut(QKeySequence("Ctrl+g"))
        self.action_tag.triggered.connect(self.manage_tag)
        self.action_tag.setIcon(QIcon(QPixmap(RESOURCE_DIR / "tag.png")))
        self.menu.addAction(self.menu_tag.menuAction())
        self.menu_tag.addAction(self.action_tag)

        self.menu_setting = QMenu(self.menu, title="&Préférence")
        self.menu_theme = QMenu(self.menu_setting, title="&Thème")
        self.action_light = QAction(self, text="&Clair")
        self.action_light.setShortcut(QKeySequence("Ctrl+Shift+l"))
        self.action_light.triggered.connect(partial(self.change_theme, "light"))
        self.action_dark = QAction(self, text="&Sombre")
        self.action_dark.setShortcut(QKeySequence("Ctrl+Shift+d"))
        self.action_dark.triggered.connect(partial(self.change_theme, "dark"))
        self.menu.addAction(self.menu_setting.menuAction())
        self.menu_setting.addAction(self.menu_theme.menuAction())
        self.menu_theme.addAction(self.action_light)
        self.menu_theme.addAction(self.action_dark)

        self.menu_about = QMenu(self.menu)
        self.menu_about.setTitle("?")
        self.action_about = QAction(self, text="A pr&opos")
        self.action_about.triggered.connect(self.open_about)
        self.menu.addAction(self.menu_about.menuAction())
        self.menu_about.addAction(self.action_about)

        self.setMenuBar(self.menu)

    def distribution_editing_action(self, table_view: str = None):
        """Appel une des méthodes pour éditer une donnée en fonction
        du TableView actif ou passé en paramètre."""
        if table_view:
            widget = self.findChild(CustomTableView, table_view)
            if widget.currentIndex().sibling(widget.currentIndex().row(), 0).data() is None:
                return
            target = table_view
        else:
            widget = self.check_widget_with_focus()
            if not widget or widget.currentIndex().sibling(widget.currentIndex().row(), 0).data() is None:
                return
            target = widget.objectName()

        match target:
            case "contact":
                self.open_details_contact(mode_action="modify", selected=widget.currentIndex())
            case "phone":
                self.open_details_phone(mode_action="modify", selected=widget.currentIndex())
            case "mail":
                self.open_details_mail(mode_action="modify", selected=widget.currentIndex())
            case "address":
                self.open_details_address(mode_action="modify", selected=widget.currentIndex())

    def distribution_deleting_action(self, table_view: str = None):
        """Appel une des méthodes pour supprimer une donnée en fonction
        du TableView actif ou passé en paramètre."""
        if table_view:
            widget = self.findChild(CustomTableView, table_view)
            if widget.currentIndex().sibling(widget.currentIndex().row(), 0).data() is None:
                return
            target = table_view
        else:
            widget = self.check_widget_with_focus()
            if not widget or widget.currentIndex().sibling(widget.currentIndex().row(), 0).data() is None:
                return
            target = widget.objectName()

        match target:
            case "contact":
                self.deleting_contact(selected=widget.currentIndex())
            case "phone":
                self.deleting_phone(selected=widget.currentIndex())
            case "mail":
                self.deleting_mail(selected=widget.currentIndex())
            case "address":
                self.deleting_address(selected=widget.currentIndex())

    def check_widget_with_focus(self) -> CustomTableView | None:
        """Vérifie si le widget possédant le focus est un CustomTableView.
        Si oui, le retourne."""
        widget = self.centralWidget().focusWidget()
        if not isinstance(widget, CustomTableView):
            return

        if widget.currentIndex().row() == -1:
            return

        return widget

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.le_search = QLineEdit()
        self.tv_contact = CustomTableView("contact", self.model_contact, header_stretch="all")
        self.btn_modify_contact = QPushButton()
        self.btn_add_contact = QPushButton()
        self.btn_del_contact = QPushButton()
        self.tv_phone = CustomTableView("phone", self.model_phone, header_stretch="last")
        self.btn_modify_phone = QPushButton()
        self.btn_add_phone = QPushButton()
        self.btn_del_phone = QPushButton()
        self.tv_mail = CustomTableView("mail", self.model_mail, header_stretch="last")
        self.btn_modify_mail = QPushButton()
        self.btn_add_mail = QPushButton()
        self.btn_del_mail = QPushButton()
        self.tv_address = CustomTableView("address", self.model_address, header_stretch="last")
        self.btn_modify_address = QPushButton()
        self.btn_add_address = QPushButton()
        self.btn_del_address = QPushButton()
        self.la_profile_picture = ProfilePicture(RESOURCE_DIR / "pp_00000.png")
        self.la_birthday = QLabel("Age :")
        self.la_birthday_value = QLabel("")
        self.la_company = QLabel("Société :")
        self.la_company_value = QLabel("")
        self.la_job = QLabel("Poste :")
        self.la_job_value = QLabel("")
        self.la_group = QLabel("Groupe :")
        self.la_group_value = QLabel("")

    def modify_widgets(self):
        self.le_search.setPlaceholderText("Rechercher...")

        self.btn_modify_contact.setIcon(QIcon(QPixmap(RESOURCE_DIR / "user--pencil.png")))
        self.btn_modify_contact.setStyleSheet("QPushButton {min-width: 0px;}")
        self.btn_add_contact.setIcon(QIcon(QPixmap(RESOURCE_DIR / "user--plus.png")))
        self.btn_add_contact.setStyleSheet("QPushButton {min-width: 0px;}")
        self.btn_del_contact.setIcon(QIcon(QPixmap(RESOURCE_DIR / "user--minus.png")))
        self.btn_del_contact.setStyleSheet("QPushButton {min-width: 0px;}")

        self.btn_modify_phone.setIcon(QIcon(QPixmap(RESOURCE_DIR / "mobile-phone--pencil.png")))
        self.btn_modify_phone.setStyleSheet("QPushButton {min-width: 0px;}")
        self.btn_add_phone.setIcon(QIcon(QPixmap(RESOURCE_DIR / "mobile-phone--plus.png")))
        self.btn_add_phone.setStyleSheet("QPushButton {min-width: 0px;}")
        self.btn_del_phone.setIcon(QIcon(QPixmap(RESOURCE_DIR / "mobile-phone--minus.png")))
        self.btn_del_phone.setStyleSheet("QPushButton {min-width: 0px;}")

        self.btn_modify_mail.setIcon(QIcon(QPixmap(RESOURCE_DIR / "mail--pencil.png")))
        self.btn_modify_mail.setStyleSheet("QPushButton {min-width: 0px;}")
        self.btn_add_mail.setIcon(QIcon(QPixmap(RESOURCE_DIR / "mail--plus.png")))
        self.btn_add_mail.setStyleSheet("QPushButton {min-width: 0px;}")
        self.btn_del_mail.setIcon(QIcon(QPixmap(RESOURCE_DIR / "mail--minus.png")))
        self.btn_del_mail.setStyleSheet("QPushButton {min-width: 0px;}")

        self.btn_modify_address.setIcon(QIcon(QPixmap(RESOURCE_DIR / "map--pencil.png")))
        self.btn_modify_address.setStyleSheet("QPushButton {min-width: 0px;}")
        self.btn_add_address.setIcon(QIcon(QPixmap(RESOURCE_DIR / "map--plus.png")))
        self.btn_add_address.setStyleSheet("QPushButton {min-width: 0px;}")
        self.btn_del_address.setIcon(QIcon(QPixmap(RESOURCE_DIR / "map--minus.png")))
        self.btn_del_address.setStyleSheet("QPushButton {min-width: 0px;}")

    def create_layouts(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QGridLayout(self.central_widget)
        self.contact_layout = QVBoxLayout()
        self.btn_contact_layout = QHBoxLayout()
        self.phone_layout = QVBoxLayout()
        self.btn_phone_layout = QHBoxLayout()
        self.mail_layout = QVBoxLayout()
        self.btn_mail_layout = QHBoxLayout()
        self.address_layout = QVBoxLayout()
        self.btn_address_layout = QHBoxLayout()
        self.other_layout = QVBoxLayout()
        self.profile_picture_layout = QHBoxLayout()
        self.information_layout = QFormLayout()

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.le_search, 0, 0, 1, 3)
        self.main_layout.addLayout(self.contact_layout, 1, 0, 2, 1)
        self.main_layout.addLayout(self.phone_layout, 1, 1, 1, 1)
        self.main_layout.addLayout(self.mail_layout, 1, 2, 1, 1)
        self.main_layout.addLayout(self.other_layout, 2, 1, 1, 1)
        self.main_layout.addLayout(self.address_layout, 2, 2, 1, 1)

        self.btn_contact_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.btn_contact_layout.addWidget(self.btn_modify_contact)
        self.btn_contact_layout.addWidget(self.btn_add_contact)
        self.btn_contact_layout.addWidget(self.btn_del_contact)
        self.btn_contact_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.contact_layout.addLayout(self.btn_contact_layout)
        self.contact_layout.addWidget(self.tv_contact)

        self.btn_phone_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.btn_phone_layout.addWidget(self.btn_modify_phone)
        self.btn_phone_layout.addWidget(self.btn_add_phone)
        self.btn_phone_layout.addWidget(self.btn_del_phone)
        self.btn_phone_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.phone_layout.addLayout(self.btn_phone_layout)
        self.phone_layout.addWidget(self.tv_phone)

        self.btn_mail_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.btn_mail_layout.addWidget(self.btn_modify_mail)
        self.btn_mail_layout.addWidget(self.btn_add_mail)
        self.btn_mail_layout.addWidget(self.btn_del_mail)
        self.btn_mail_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.mail_layout.addLayout(self.btn_mail_layout)
        self.mail_layout.addWidget(self.tv_mail)

        self.btn_address_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.btn_address_layout.addWidget(self.btn_modify_address)
        self.btn_address_layout.addWidget(self.btn_add_address)
        self.btn_address_layout.addWidget(self.btn_del_address)
        self.btn_address_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.address_layout.addLayout(self.btn_address_layout)
        self.address_layout.addWidget(self.tv_address)

        self.other_layout.addLayout(self.profile_picture_layout)
        self.profile_picture_layout.addWidget(self.la_profile_picture)
        self.other_layout.addLayout(self.information_layout)
        self.information_layout.addRow(self.la_birthday, self.la_birthday_value)
        self.information_layout.addRow(self.la_company, self.la_company_value)
        self.information_layout.addRow(self.la_job, self.la_job_value)
        self.information_layout.addRow(self.la_group, self.la_group_value)

    def setup_connections(self):
        self.le_search.textChanged.connect(self.update_tv_contact)
        self.tv_contact.selectionModel().currentRowChanged.connect(self.update_other_display)
        self.tv_contact.doubleClicked.connect(partial(self.open_details_contact, "modify"))
        self.btn_modify_contact.clicked.connect(partial(self.distribution_editing_action, "contact"))
        self.btn_add_contact.clicked.connect(partial(self.open_details_contact, "adding"))
        self.btn_del_contact.clicked.connect(partial(self.distribution_deleting_action, "contact"))
        self.tv_phone.doubleClicked.connect(partial(self.open_details_phone, "modify"))
        self.btn_modify_phone.clicked.connect(partial(self.distribution_editing_action, "phone"))
        self.btn_add_phone.clicked.connect(partial(self.open_details_phone, "adding"))
        self.btn_del_phone.clicked.connect(partial(self.distribution_deleting_action, "phone"))
        self.tv_mail.doubleClicked.connect(partial(self.open_details_mail, "modify"))
        self.btn_modify_mail.clicked.connect(partial(self.distribution_editing_action, "mail"))
        self.btn_add_mail.clicked.connect(partial(self.open_details_mail, "adding"))
        self.btn_del_mail.clicked.connect(partial(self.distribution_deleting_action, "mail"))
        self.tv_address.doubleClicked.connect(partial(self.open_details_address, "modify"))
        self.btn_modify_address.clicked.connect(partial(self.distribution_editing_action, "address"))
        self.btn_add_address.clicked.connect(partial(self.open_details_address, "adding"))
        self.btn_del_address.clicked.connect(partial(self.distribution_deleting_action, "address"))
        self.la_profile_picture.doubleClicked.connect(self.get_filename_image)

    def get_filename_image(self):
        """Ouvre une boite de dialogue afin de récupérer le chemin d'une image.
        La sauvegarde (resources et bdd) et l'applique à interface.
        Beaucoup trop d'action : À décomposer"""
        row = self.tv_contact.currentIndex().row()
        if row == -1:
            return
        filters = "Image (*.png;*.jpg;*.jpeg)"
        selected_file, _ = QFileDialog.getOpenFileName(self, dir=str(Path.home()), filter=filters)

        if not selected_file:
            return

        path = Path(selected_file)
        id_: int = self.tv_contact.currentIndex().sibling(row, 0).data()
        new_filename = RESOURCE_DIR / f"pp_{str(id_).zfill(5)}{path.suffix}"
        if new_filename.exists():
            new_filename.unlink()
        shutil.copy(path, new_filename)
        update_profil_picture(id_contact=id_, filename=new_filename.name)
        self.update_other_display(self.tv_contact.currentIndex())

    def open_details_contact(self, mode_action: str, selected: QModelIndex = None):
        """Ouvre la fenêtre pour l'ajout ou la modification d'un contact."""
        if mode_action == "modify":
            row = selected.row()
            selected_row_index = self.tv_contact.currentIndex()
            id_contact: int = selected_row_index.sibling(row, 0).data()
        else:
            id_contact = 0

        self.details_contact = DetailsContact(mode_action=mode_action, id_contact=id_contact)
        if mode_action == "modify":
            self.details_contact.update_main_window.connect(partial(self.refresh_tv_contact, selected_row_index))
        else:
            self.details_contact.update_main_window.connect(self.refresh_tv_contact)

        self.details_contact.setWindowModality(Qt.ApplicationModal)
        self.details_contact.show()

    def open_details_phone(self, mode_action: str, selected: QModelIndex = None):
        """Ouvre la fenêtre pour l'ajout ou la modification d'un numéro de téléphone."""
        if self.tv_contact.currentIndex().row() == -1:
            return

        if mode_action == "modify":
            row = selected.row()
            selected_row_index = self.tv_phone.currentIndex()
            id_phone = selected_row_index.sibling(row, 0).data()
        else:
            id_phone = 0

        self.details_phone = DetailsPhone(id_phone, mode_action=mode_action, id_contact=self.id_contact)
        if mode_action == "modify":
            self.details_phone.update_main_window.connect(partial(self.refresh_tv_phone, selected_row_index))
        else:
            self.details_phone.update_main_window.connect(self.refresh_tv_phone)
        self.details_phone.setWindowModality(Qt.ApplicationModal)
        self.details_phone.show()

    def open_details_mail(self, mode_action: str, selected: QModelIndex = None):
        """Ouvre la fenêtre pour l'ajout ou la modification d'un mail."""
        if self.tv_contact.currentIndex().row() == -1:
            return

        if mode_action == "modify":
            row = selected.row()
            selected_row_index = self.tv_mail.currentIndex()
            id_mail = selected_row_index.sibling(row, 0).data()
        else:
            id_mail = 0

        self.details_mail = DetailsMail(id_mail, mode_action=mode_action, id_contact=self.id_contact)
        if mode_action == "modify":
            self.details_mail.update_main_window.connect(partial(self.refresh_tv_mail, selected_row_index))
        else:
            self.details_mail.update_main_window.connect(self.refresh_tv_mail)
        self.details_mail.setWindowModality(Qt.ApplicationModal)
        self.details_mail.show()

    def open_details_address(self, mode_action: str, selected: QModelIndex = None):
        """Ouvre la fenêtre pour l'ajout ou la modification d'une adresse."""
        if self.tv_contact.currentIndex().row() == -1:
            return

        if mode_action == "modify":
            row = selected.row()
            selected_row_index = self.tv_address.currentIndex()
            id_address = selected_row_index.sibling(row, 0).data()
        else:
            id_address = 0

        self.details_address = DetailsAddress(id_address, mode_action=mode_action, id_contact=self.id_contact)
        if mode_action == "modify":
            self.details_address.update_main_window.connect(partial(self.refresh_tv_address, selected_row_index))
        else:
            self.details_address.update_main_window.connect(self.refresh_tv_address)
        self.details_address.setWindowModality(Qt.ApplicationModal)
        self.details_address.show()

    def manage_tag(self):
        """Ouvre la fenêtre de gestion des tags."""
        self.win = Tag()
        self.win.setWindowModality(Qt.ApplicationModal)
        self.win.show()

    def open_about(self):
        """Ouvre la fenêtre 'A propos' de l'application"""
        self.win = About()
        self.win.setWindowModality(Qt.ApplicationModal)
        self.win.show()

    def refresh_tv_contact(self, selected_row: QModelIndex = None):
        """Rafraichi les données de tv_contact après ajout ou modification d'une donnée"""
        self.model_contact.setQuery(self.query_contact, db=self.db)
        if selected_row:
            self.tv_contact.setCurrentIndex(selected_row)

    def refresh_tv_phone(self, selected_row: QModelIndex = None):
        """Rafraichi les données de tv_phone après ajout ou modification d'une donnée"""
        self.model_phone.setQuery(self.query_phone, db=self.db)
        if selected_row:
            self.tv_phone.setCurrentIndex(selected_row)

    def refresh_tv_mail(self, selected_row: QModelIndex = None):
        """Rafraichi les données de tv_mail après ajout ou modification d'une donnée"""
        self.model_mail.setQuery(self.query_mail, db=self.db)
        if selected_row:
            self.tv_mail.setCurrentIndex(selected_row)

    def refresh_tv_address(self, selected_row: QModelIndex = None):
        """Rafraichi les données de tv_address après ajout ou modification d'une donnée"""
        self.model_address.setQuery(self.query_address, db=self.db)
        if selected_row:
            self.tv_address.setCurrentIndex(selected_row)

    def update_tv_contact(self):
        """Actualisation des données affichées dans tv_contact suite à une
        saisie dans la barre de recherche le_search."""
        if search := self.le_search.text():
            self.query_contact = f'''SELECT DISTINCT contact.id, firstname, lastname FROM contact 
                             LEFT OUTER JOIN mail ON contact.id = mail.contact_id 
                             LEFT OUTER JOIN phone ON contact.id = phone.contact_id 
                             LEFT OUTER JOIN address ON contact.id = address.contact_id 
                             LEFT OUTER JOIN group_ ON contact.id = group_.contact_id 
                             LEFT OUTER JOIN tag ON group_.tag_id = tag.id 
                             WHERE lastname LIKE "%{search}%" 
                             OR firstname LIKE "%{search}%" 
                             OR mail LIKE "%{search}%" 
                             OR number LIKE "%{search}%" 
                             OR address LIKE "%{search}%" 
                             OR tag LIKE "%{search}%"'''
        else:
            self.query_contact = 'SELECT id, firstname, lastname FROM contact'

        self.model_contact.setQuery(self.query_contact, db=self.db)
        self.clean_other_display()
        self.update_other_display(self.tv_contact.currentIndex())

    def clean_other_display(self):
        """Nettoyage de toutes les données affichées hormis tv_contact."""
        self.model_phone.setQuery("")
        self.model_mail.setQuery("")
        self.model_address.setQuery("")
        self.la_birthday_value.setText("")
        self.la_company_value.setText("")
        self.la_job_value.setText("")
        self.la_group_value.setText("")
        self.la_profile_picture.set_image(RESOURCE_DIR / "bg.png")
        self.la_profile_picture.set_image(RESOURCE_DIR / "pp_00000.png")

    def update_other_display(self, selected: QModelIndex):
        """Actualisation des données affichées hormis tv_contact.
        Beaucoup trop long : À décomposer."""
        row = selected.row()
        selected_row_index = self.tv_contact.currentIndex()
        self.id_contact = selected_row_index.sibling(row, 0).data()

        informations = get_contact_informations(id_contact=self.id_contact)
        if not informations:
            return

        if file_picture := informations[0]:
            if not self.background_color:
                self.generate_background_picture()
            self.la_profile_picture.set_image(RESOURCE_DIR / "bg.png")
            self.la_profile_picture.set_image(RESOURCE_DIR / file_picture)

        birthday = informations[1]
        if birthday and birthday != "1899-12-31":
            birthday = datetime.strptime(birthday, '%Y-%m-%d')
            age = get_age_from_birthday(birthday)
            self.la_birthday_value.setText(f"{age} ans ({birthday.strftime('%d/%m/%Y')})")
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

        self.la_group_value.setText(get_contact_group(self.id_contact))

        self.query_phone = QUERY_PHONE.format(id=self.id_contact)
        self.model_phone.setQuery(self.query_phone, db=self.db)
        self.tv_phone.hide_first_column()

        self.query_mail = QUERY_MAIL.format(id=self.id_contact)
        self.model_mail.setQuery(self.query_mail, db=self.db)
        self.tv_mail.hide_first_column()

        self.query_address = QUERY_ADDRESS.format(id=self.id_contact)
        self.model_address.setQuery(self.query_address, db=self.db)
        self.tv_address.hide_first_column()

    def change_theme(self, theme: str):
        """Permet la bascule entre les thèmes clair et sombre"""
        if self.theme == theme:
            return

        if theme == "light":
            self.parent.setStyleSheet(get_light_style_sheet())
            self.theme = "light"
        elif theme == "dark":
            self.parent.setStyleSheet(get_dark_style_sheet())
            self.theme = "dark"
        update_theme_setting(theme)
        self.generate_background_picture()
        selected_row_index = self.tv_contact.currentIndex()
        self.update_other_display(selected_row_index)

    def generate_background_picture(self):
        """Génération d'une image de la couleur de fond de l'application."""
        self.background_color = self.palette().color(QPalette.Window).toTuple()
        create_background_picture(self.background_color)

    def deleting_contact(self, selected: QModelIndex):
        """Suppression après confirmation d'un contact."""
        firstname = selected.sibling(selected.row(), 1).data()
        lastname = selected.sibling(selected.row(), 2).data()

        msg = MessageDelete("contact", firstname, lastname)
        button = msg.exec()
        button = QMessageBox.StandardButton(button)
        if button != QMessageBox.StandardButton.Yes:
            return

        id_contact = selected.sibling(selected.row(), 0).data()
        del_contact_by_id(id_contact)
        self.refresh_tv_contact(selected)
        self.refresh_tv_mail(selected)
        self.refresh_tv_address(selected)
        self.refresh_tv_phone(selected)

    def deleting_phone(self, selected: QModelIndex):
        """Suppression après confirmation d'un numéro de téléphone."""
        number = selected.sibling(selected.row(), 2).data()

        msg = MessageDelete("phone", number)
        button = msg.exec()
        button = QMessageBox.StandardButton(button)
        if button != QMessageBox.StandardButton.Yes:
            return

        id_phone = selected.sibling(selected.row(), 0).data()
        del_phone_by_id(id_phone)
        self.refresh_tv_phone(selected)

    def deleting_mail(self, selected: QModelIndex):
        """Suppression après confirmation d'un mail."""
        mail = selected.sibling(selected.row(), 2).data()

        msg = MessageDelete("mail", mail)
        button = msg.exec()
        button = QMessageBox.StandardButton(button)
        if button != QMessageBox.StandardButton.Yes:
            return

        id_mail = selected.sibling(selected.row(), 0).data()
        del_mail_by_id(id_mail)
        self.refresh_tv_mail(selected)

    def deleting_address(self, selected: QModelIndex):
        """Suppression après confirmation d'une adresse."""
        address = selected.sibling(selected.row(), 2).data()

        msg = MessageDelete("address", address)
        button = msg.exec()
        button = QMessageBox.StandardButton(button)
        if button != QMessageBox.StandardButton.Yes:
            return

        id_address = selected.sibling(selected.row(), 0).data()
        del_address_by_id(id_address)
        self.refresh_tv_address(selected)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    app.setStyleSheet(get_dark_style_sheet())
    window = Crm(app)
    window.show()
    app.exec()
