from datetime import datetime


class User:
    def __init__(self, last_name: str,
                 first_name,
                 mail: str = "",
                 phone: str = "",
                 address: str = "",
                 birthday: datetime = ""):

        self.last_name = last_name
        self.first_name = first_name
        self.mail = mail
        self.phone = phone
        self.address = address
        self.birthday = birthday

    def __repr__(self):
        return f"User('{self.last_name}', '{self.first_name}')"

    def __str__(self):
        return f"{self.last_name.upper()} {self.first_name.capitalize()}"


if __name__ == '__main__':
    patrick = User("Bruel", "Patrick")
    print(patrick)
    print(patrick.__repr__())
