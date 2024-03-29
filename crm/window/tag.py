from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtWidgets import QWidget, QLabel, QListWidget, QPushButton, QGridLayout, QHBoxLayout, \
    QSpacerItem, QSizePolicy, QMessageBox

from crm.api.utils import RESOURCE_DIR
from crm.database.client import get_tag_to_category_group, get_tag_to_category_phone, get_tag_to_category_mail, \
    get_tag_to_category_address, del_tag_by_id, add_tag, update_tag
from crm.window.list_item import CustomListWidgetItem
from crm.window.input_tag import InputTag


# noinspection PyAttributeOutsideInit
class Tag(QWidget):
    def __init__(self):
        super().__init__()

        self.setup_ui()
        self.resize(600, 300)
        self.setWindowTitle("Gestion des tags")
        self.setObjectName("tag")
        self.btn_close.setFocus()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.la_group = QLabel("Groupe")
        self.la_phone = QLabel("Téléphone")
        self.la_mail = QLabel("Mail")
        self.la_address = QLabel("Adresse")
        self.lw_group = QListWidget()
        self.lw_phone = QListWidget()
        self.lw_mail = QListWidget()
        self.lw_address = QListWidget()
        self.btn_add_group = QPushButton("")
        self.btn_del_group = QPushButton("")
        self.btn_add_phone = QPushButton("")
        self.btn_del_phone = QPushButton("")
        self.btn_add_mail = QPushButton("")
        self.btn_del_mail = QPushButton("")
        self.btn_add_address = QPushButton("")
        self.btn_del_address = QPushButton("")
        self.btn_close = QPushButton("Fermer")

    def modify_widgets(self):
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        self.la_group.setFont(font)
        self.la_phone.setFont(font)
        self.la_mail.setFont(font)
        self.la_address.setFont(font)
        self.la_group.setAlignment(Qt.AlignCenter)
        self.la_phone.setAlignment(Qt.AlignCenter)
        self.la_mail.setAlignment(Qt.AlignCenter)
        self.la_address.setAlignment(Qt.AlignCenter)
        self.lw_group.setObjectName("group")
        self.lw_phone.setObjectName("phone")
        self.lw_mail.setObjectName("mail")
        self.lw_address.setObjectName("address")
        self.btn_add_group.setIcon(QIcon(QPixmap(RESOURCE_DIR / "plus.png")))
        self.btn_del_group.setIcon(QIcon(QPixmap(RESOURCE_DIR / "cross.png")))
        self.btn_add_phone.setIcon(QIcon(QPixmap(RESOURCE_DIR / "plus.png")))
        self.btn_del_phone.setIcon(QIcon(QPixmap(RESOURCE_DIR / "cross.png")))
        self.btn_add_mail.setIcon(QIcon(QPixmap(RESOURCE_DIR / "plus.png")))
        self.btn_del_mail.setIcon(QIcon(QPixmap(RESOURCE_DIR / "cross.png")))
        self.btn_add_address.setIcon(QIcon(QPixmap(RESOURCE_DIR / "plus.png")))
        self.btn_del_address.setIcon(QIcon(QPixmap(RESOURCE_DIR / "cross.png")))
        self.btn_add_group.setStyleSheet("QPushButton {min-width: 0px;}")
        self.btn_add_phone.setStyleSheet("QPushButton {min-width: 0px;}")
        self.btn_add_mail.setStyleSheet("QPushButton {min-width: 0px;}")
        self.btn_add_address.setStyleSheet("QPushButton {min-width: 0px;}")
        self.btn_del_group.setStyleSheet("QPushButton {min-width: 0px;}")
        self.btn_del_phone.setStyleSheet("QPushButton {min-width: 0px;}")
        self.btn_del_mail.setStyleSheet("QPushButton {min-width: 0px;}")
        self.btn_del_address.setStyleSheet("QPushButton {min-width: 0px;}")
        item_group = get_tag_to_category_group()
        for tag, id_tag in item_group:
            lw_item = CustomListWidgetItem(item=tag, idx=id_tag)
            self.lw_group.addItem(lw_item)

        tags, idx = get_tag_to_category_phone()
        for tag, id_tag in zip(tags, idx):
            lw_item = CustomListWidgetItem(item=tag, idx=id_tag)
            self.lw_phone.addItem(lw_item)

        tags, idx = get_tag_to_category_mail()
        for tag, id_tag in zip(tags, idx):
            lw_item = CustomListWidgetItem(item=tag, idx=id_tag)
            self.lw_mail.addItem(lw_item)

        tags, idx = get_tag_to_category_address()
        for tag, id_tag in zip(tags, idx):
            lw_item = CustomListWidgetItem(item=tag, idx=id_tag)
            self.lw_address.addItem(lw_item)

    def create_layouts(self):
        self.main_layout = QGridLayout(self)
        self.action_group_layout = QHBoxLayout()
        self.action_phone_layout = QHBoxLayout()
        self.action_mail_layout = QHBoxLayout()
        self.action_address_layout = QHBoxLayout()
        self.close_layout = QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.la_group, 0, 0, 1, 1)
        self.main_layout.addWidget(self.la_phone, 0, 1, 1, 1)
        self.main_layout.addWidget(self.la_mail, 0, 2, 1, 1)
        self.main_layout.addWidget(self.la_address, 0, 3, 1, 1)
        self.main_layout.addWidget(self.lw_group, 1, 0, 1, 1)
        self.main_layout.addWidget(self.lw_phone, 1, 1, 1, 1)
        self.main_layout.addWidget(self.lw_mail, 1, 2, 1, 1)
        self.main_layout.addWidget(self.lw_address, 1, 3, 1, 1)
        self.main_layout.addLayout(self.action_group_layout, 2, 0, 1, 1)
        self.main_layout.addLayout(self.action_phone_layout, 2, 1, 1, 1)
        self.main_layout.addLayout(self.action_mail_layout, 2, 2, 1, 1)
        self.main_layout.addLayout(self.action_address_layout, 2, 3, 1, 1)
        self.main_layout.addLayout(self.close_layout, 3, 0, 1, 4)

        self.action_group_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.action_group_layout.addWidget(self.btn_add_group)
        self.action_group_layout.addWidget(self.btn_del_group)
        self.action_group_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.action_phone_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.action_phone_layout.addWidget(self.btn_add_phone)
        self.action_phone_layout.addWidget(self.btn_del_phone)
        self.action_phone_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.action_mail_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.action_mail_layout.addWidget(self.btn_add_mail)
        self.action_mail_layout.addWidget(self.btn_del_mail)
        self.action_mail_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.action_address_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.action_address_layout.addWidget(self.btn_add_address)
        self.action_address_layout.addWidget(self.btn_del_address)
        self.action_address_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.close_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.close_layout.addWidget(self.btn_close)
        self.close_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

    def setup_connections(self):
        self.lw_group.itemDoubleClicked.connect(partial(self.open_modify_tag, "group"))
        self.lw_phone.itemDoubleClicked.connect(partial(self.open_modify_tag, "phone"))
        self.lw_mail.itemDoubleClicked.connect(partial(self.open_modify_tag, "mail"))
        self.lw_address.itemDoubleClicked.connect(partial(self.open_modify_tag, "address"))
        self.btn_add_group.clicked.connect(partial(self.open_add_tag, "group"))
        self.btn_add_phone.clicked.connect(partial(self.open_add_tag, "phone"))
        self.btn_add_mail.clicked.connect(partial(self.open_add_tag, "mail"))
        self.btn_add_address.clicked.connect(partial(self.open_add_tag, "address"))
        self.btn_del_group.clicked.connect(partial(self.del_tag, "group"))
        self.btn_del_phone.clicked.connect(partial(self.del_tag, "phone"))
        self.btn_del_mail.clicked.connect(partial(self.del_tag, "mail"))
        self.btn_del_address.clicked.connect(partial(self.del_tag, "address"))
        self.btn_close.clicked.connect(self.close)

    def open_modify_tag(self, category: str, item: CustomListWidgetItem):
        """Ouvre la fenêtre de saisi utilisateur pour modifier un tag."""
        self.alter_tag = InputTag(self, "modify", category, item)
        self.alter_tag.setWindowModality(Qt.ApplicationModal)
        self.alter_tag.save_tag.connect(partial(self.modify_tag, item))
        self.alter_tag.show()

    @staticmethod
    def modify_tag(item: CustomListWidgetItem, new_tag: str):
        item.setText(new_tag)
        update_tag(tag=new_tag, id_=item.id)

    def open_add_tag(self, category: str):
        """Ouvre la fenêtre de saisi utilisateur pour ajouter un tag."""
        self.new_tag = InputTag(self, "adding", category)
        self.new_tag.setWindowModality(Qt.ApplicationModal)
        self.new_tag.save_tag.connect(partial(self.add_tag, category))
        self.new_tag.show()

    def add_tag(self, category: str, new_tag: str):
        id_ = add_tag(tag=new_tag, category=category)
        lw_item = CustomListWidgetItem(item=new_tag, idx=id_)
        list_widget: QListWidget = self.findChild(QListWidget, category)
        list_widget.addItem(lw_item)

    def del_tag(self, category: str):
        """Supression d'un tag seulement s'il n'est pas associé à un contact."""
        widget: QListWidget = self.findChild(QListWidget, category)
        if widget.currentIndex().data() is None:
            return

        item = widget.currentItem()
        if not del_tag_by_id(item.id, category):
            msg = QMessageBox(self)
            msg.setWindowTitle("Suppression impossible")
            msg.setText(f"Le tag {item.text()} ne peut pas être supprimé tant qu'il est associé "
                        f"à un ou plusieurs contacts.")
            msg.exec()
            return

        widget.takeItem(widget.row(item))


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = Tag()
    window.show()
    app.exec()
