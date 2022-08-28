from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QListWidgetItem

from crm.api.utils import RESOURCE_DIR


class CustomListWidgetItem(QListWidgetItem):
    def __init__(self, item: str, idx: int):
        super().__init__(item)
        self.is_checked = None
        self.id = idx

    @property
    def checked(self) -> None:
        self.is_checked = True
        return self.setIcon(QIcon(QPixmap(RESOURCE_DIR / "tick.png")))

    @property
    def unchecked(self) -> None:
        self.is_checked = False
        return self.setIcon(QIcon(QPixmap(RESOURCE_DIR / "cross.png")))

    def change_etat(self):
        if self.is_checked:
            self.unchecked
        else:
            self.checked
