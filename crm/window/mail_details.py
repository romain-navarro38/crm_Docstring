"""Module contenant la classe DetailsMail permettant de générer la fenêtre
d'ajout ou modification d'un mail."""
from functools import partial

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtSql import QSqlDatabase, QSqlQueryModel
from PySide6.QtWidgets import QWidget, QGridLayout, QLineEdit, QLabel, QDataWidgetMapper, QPushButton, \
    QVBoxLayout, QHBoxLayout, QComboBox, QSpacerItem, QSizePolicy, QMessageBox

from crm.api.utils import DATA_FILE, check_mail_format, RESOURCE_DIR
from crm.database.client import update_mail, get_tag_to_category_mail, add_mail, add_tag
from crm.window.input_tag import InputTag


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
        self.connect_db()
        self.setup_model()
        self.setup_ui()
        self.setObjectName("details")
        self.setMinimumWidth(350)
        if mode_action == "modify":
            self.setWindowTitle("Modifier une adresse mail")
        else:
            self.setWindowTitle("Ajouter une adresse mail")

    def connect_db(self):
        self.db = QSqlDatabase("QSQLITE")
        self.db.setDatabaseName(str(DATA_FILE))
        self.db.open()

    def setup_model(self):
        self.model = QSqlQueryModel()
        self.mapper = QDataWidgetMapper()
        self.mapper.setModel(self.model)

        query = f"""
            SELECT id, mail, tag_id FROM mail
            WHERE id={self.id_mail}
        """
        self.model.setQuery(query, db=self.db)

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.la_mail = QLabel("Mail")
        self.le_mail = QLineEdit()
        self.la_tag = QLabel("Tag")
        self.cbx_tag = QComboBox()
        self.btn_new_tag = QPushButton("")
        self.btn_validate = QPushButton("Valider")
        self.btn_cancel = QPushButton("Annuler")

    def modify_widgets(self):
        self.mapper.addMapping(self.le_mail, 1)
        self.mapper.toFirst()
        self.tags, self.idx = get_tag_to_category_mail()
        self.cbx_tag.addItems(self.tags)
        if self.mode_action == "modify":
            self.cbx_tag.setCurrentText(self.tags[self.idx.index(self.model.query().value(2))])
        self.cbx_tag.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.cbx_tag.setObjectName("mail")
        self.btn_new_tag.setIcon(QIcon(QPixmap(RESOURCE_DIR / "tag--plus.png")))
        self.btn_new_tag.setStyleSheet("QPushButton {min-width: 0px;}")

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.values_layout = QGridLayout()
        self.btn_layout = QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.values_layout.addWidget(QLabel("Mail"), 0, 0, 1, 1)
        self.values_layout.addWidget(self.le_mail, 0, 1, 1, 2)
        self.values_layout.addWidget(QLabel("Tag"), 1, 0, 1, 1)
        self.values_layout.addWidget(self.cbx_tag, 1, 1, 1, 1)
        self.values_layout.addWidget(self.btn_new_tag, 1, 2, 1, 1)

        self.btn_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.btn_layout.addWidget(self.btn_validate)
        self.btn_layout.addWidget(self.btn_cancel)
        self.btn_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.main_layout.addLayout(self.values_layout)
        self.main_layout.addLayout(self.btn_layout)

    def setup_connections(self):
        self.btn_new_tag.clicked.connect(self.open_new_tag)
        self.btn_validate.clicked.connect(self.save_changes)
        self.btn_cancel.clicked.connect(self.close)

    def open_new_tag(self):
        """Ouvre la fenêtre de saisi utilisateur pour ajouter un tag."""
        category = self.cbx_tag.objectName()
        self.new_tag = InputTag(self, "adding", category)
        self.new_tag.setWindowModality(Qt.ApplicationModal)
        self.new_tag.save_tag.connect(partial(self.add_tag, category))
        self.new_tag.show()

    def add_tag(self, category: str, new_tag: str):
        id_ = add_tag(tag=new_tag, category=category)
        self.tags.append(new_tag)
        self.idx.append(id_)
        self.cbx_tag.addItem(new_tag)

    def save_changes(self):
        """Sauvegarde en bdd du mail et du tag associé après vérifications"""
        if not self.validate_mail():
            return

        id_tag = self.idx[self.tags.index(self.cbx_tag.currentText())]
        if self.mode_action == "modify":
            update_mail(self.le_mail.text(), id_tag, self.id_mail)
        else:
            add_mail(mail=self.le_mail.text(), contact_id=self.id_contact, tag_id=id_tag)
        # Emission à la fenêtre parente qu'une modification a eu lieu
        self.update_main_window.emit()
        self.close()

    def validate_mail(self):
        """Vérification de la validité du mail renseigné"""
        if not self.le_mail.text():
            return False

        if not check_mail_format(self.le_mail.text()):
            msg = QMessageBox(self)
            msg.setWindowTitle("Invalide")
            msg.setText("cette adresse mail n'a pas le bon format.")
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
            return False
        return True


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = DetailsMail(0, "adding", 1)
    window.show()
    app.exec()
