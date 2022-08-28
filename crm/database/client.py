import sqlite3

from crm.api.utils import DATA_FILE

QUERY_PHONE = """
    SELECT phone.id, tag, number FROM phone
    INNER JOIN tag ON phone.tag_id = tag.id
    WHERE contact_id={id}
"""

QUERY_MAIL = """
    SELECT mail.id, tag, mail FROM mail 
    INNER JOIN tag ON mail.tag_id = tag.id 
    WHERE contact_id={id}
"""

QUERY_ADDRESS = """
    SELECT address.id, tag, address FROM address 
    INNER JOIN tag ON address.tag_id = tag.id 
    WHERE contact_id={id}
"""


def update_contact(**kwargs):
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("""UPDATE contact SET firstname=:firstname, 
                                    lastname=:lastname, 
                                    birthday=:birthday, 
                                    company=:company, 
                                    job=:job 
                 WHERE contact.id=:id_contact""", kwargs)
    conn.commit()
    conn.close()


def update_number_phone(number: str, id_tag: int, id_phone: int):
    conn = sqlite3.connect(DATA_FILE)
    d = {'number': number, 'id_tag': id_tag, 'id_phone': id_phone}
    c = conn.cursor()
    c.execute("UPDATE phone SET number=:number, tag_id=:id_tag WHERE phone.id=:id_phone", d)
    conn.commit()
    conn.close()


def update_mail(mail: str, id_tag: int, id_mail: int):
    conn = sqlite3.connect(DATA_FILE)
    d = {'mail': mail, 'id_tag': id_tag, 'id_mail': id_mail}
    c = conn.cursor()
    c.execute("UPDATE mail SET mail=:mail, tag_id=:id_tag WHERE mail.id=:id_mail", d)
    conn.commit()
    conn.close()


def update_address(address: str, id_tag: int, id_address: int):
    conn = sqlite3.connect(DATA_FILE)
    d = {'address': address, 'id_tag': id_tag, 'id_address': id_address}
    c = conn.cursor()
    c.execute("UPDATE address SET address=:address, tag_id=:id_tag WHERE address.id=:id_address", d)
    conn.commit()
    conn.close()


def add_contact(**kwargs) -> int:
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("""INSERT INTO contact 
                 (firstname, lastname, profile_picture, birthday, company, job) 
                 VALUES (:firstname, :lastname, 'pp_00000.png', :birthday, :company, :job)""", kwargs)
    last_id = c.lastrowid
    conn.commit()
    conn.close()
    return last_id


def add_phone(**kwargs):
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("""INSERT INTO phone 
                 (number, contact_id, tag_id) 
                 VALUES (:number, :contact_id, :tag_id)""", kwargs)
    conn.commit()
    conn.close()


def add_mail(**kwargs):
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("""INSERT INTO mail 
                 (mail, contact_id, tag_id) 
                 VALUES (:mail, :contact_id, :tag_id)""", kwargs)
    conn.commit()
    conn.close()


def add_address(**kwargs):
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("""INSERT INTO address 
                 (address, contact_id, tag_id) 
                 VALUES (:address, :contact_id, :tag_id)""", kwargs)
    conn.commit()
    conn.close()


def get_tag_to_category_group() -> list[tuple[str, int]]:
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("""SELECT tag.tag, tag.id FROM tag
                 WHERE category='group'""")
    values = c.fetchall()
    conn.close()
    return values


def get_tag_to_category_group_by_contact(id_contact: int) -> tuple[tuple[str], tuple[int]]:
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute(f"""SELECT tag.tag, tag.id FROM tag
                  INNER JOIN group_ ON tag.id = group_.tag_id
                  WHERE category='group'
                  AND contact_id={id_contact}""")
    values = c.fetchall()
    conn.close()
    return tuple(tag[0] for tag in values), tuple(idx[1] for idx in values)


def get_tag_to_category_phone() -> tuple[list[str], list[int]]:
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("SELECT id, tag FROM tag WHERE category='phone'")
    values = c.fetchall()
    conn.close()
    return [tag[1] for tag in values], [idx[0] for idx in values]


def get_tag_to_category_mail() -> tuple[list[str], list[int]]:
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("SELECT id, tag FROM tag WHERE category='mail'")
    values = c.fetchall()
    conn.close()
    return [tag[1] for tag in values], [idx[0] for idx in values]


def get_tag_to_category_address() -> tuple[list[str], list[int]]:
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("SELECT id, tag FROM tag WHERE category='address'")
    values = c.fetchall()
    conn.close()
    return [tag[1] for tag in values], [idx[0] for idx in values]


def add_tag_group_at_contact(id_contact: int, id_tag: int):
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    values = {"id": None, "contact_id": id_contact, "tag_id": id_tag}
    c.execute("INSERT INTO group_ VALUES (:id, :contact_id, :tag_id)", values)
    conn.commit()
    conn.close()


def add_tag(**kwargs) -> int:
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO tag (tag, category) VALUES (:tag, :category)", kwargs)
    last_id = c.lastrowid
    conn.commit()
    conn.close()
    return last_id


def del_group_of_contact(id_contact: int, id_tag: int):
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    values = {"contact_id": id_contact, "tag_id": id_tag}
    c.execute("DELETE FROM group_ WHERE contact_id=:contact_id AND tag_id=:tag_id", values)
    conn.commit()
    conn.close()


def del_contact_by_id(id_contact: int):
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    contact = {"contact_id": id_contact}
    c.execute("DELETE FROM group_ WHERE contact_id=:contact_id", contact)
    c.execute("DELETE FROM phone WHERE contact_id=:contact_id", contact)
    c.execute("DELETE FROM address WHERE contact_id=:contact_id", contact)
    c.execute("DELETE FROM mail WHERE contact_id=:contact_id", contact)
    c.execute("DELETE FROM contact WHERE id=:contact_id", contact)
    conn.commit()
    conn.close()


def del_phone_by_id(id_phone: int):
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    phone = {"phone_id": id_phone}
    c.execute("DELETE FROM phone WHERE id=:phone_id", phone)
    conn.commit()
    conn.close()


def del_mail_by_id(id_mail: int):
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    mail = {"mail_id": id_mail}
    c.execute("DELETE FROM mail WHERE id=:mail_id", mail)
    conn.commit()
    conn.close()


def del_address_by_id(id_address: int):
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    address = {"address_id": id_address}
    c.execute("DELETE FROM address WHERE id=:address_id", address)
    conn.commit()
    conn.close()


def del_tag_by_id(id_tag: int, category: str) -> bool:
    link_table = {"group": "group_",
                  "phone": "phone",
                  "mail": "mail",
                  "address": "address"}
    table = link_table[category]

    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute(f"""SELECT {table}.id 
                  FROM {table} 
                  WHERE {table}.tag_id={id_tag}""")
    if c.fetchall():
        return False

    tag = {"id": id_tag}
    c.execute("DELETE FROM tag WHERE id=:id", tag)
    conn.commit()
    conn.close()
    return True


if __name__ == '__main__':
    print(del_tag_by_id(10, "group"))
