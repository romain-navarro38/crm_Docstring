"""Module faisant le lien entre la base de données et l'application pour les opérations CRUD"""

import sqlite3

from crm.api.utils import DATA_FILE, DEFAULT_TAGS

##############
#   CREATE   #
##############

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

CONTACT = """ CREATE TABLE IF NOT EXISTS contact (
                    id INTEGER PRIMARY KEY,
                    firstname TEXT,
                    lastname TEXT,
                    profile_picture TEXT,
                    birthday TEXT,
                    company TEXT,
                    job TEXT
              );
"""

TAG = """
    CREATE TABLE IF NOT EXISTS tag (
        id integer PRIMARY KEY,
        tag text,
        category text
    );
"""

PHONE = """
    CREATE TABLE IF NOT EXISTS phone (
        id integer PRIMARY KEY,
        number text,
        contact_id integer NOT NULL,
        tag_id integer NOT NULL,
        FOREIGN KEY (contact_id) REFERENCES contact (id),
        FOREIGN KEY (tag_id) REFERENCES tag (id)
    );
"""

MAIL = """
    CREATE TABLE IF NOT EXISTS mail (
        id integer PRIMARY KEY,
        mail text,
        contact_id integer NOT NULL,
        tag_id integer NOT NULL,
        FOREIGN KEY (contact_id) REFERENCES contact (id),
        FOREIGN KEY (tag_id) REFERENCES tag (id)
    );
"""

ADDRESS = """
    CREATE TABLE IF NOT EXISTS address (
        id integer PRIMARY KEY,
        address text,
        contact_id integer NOT NULL,
        tag_id integer NOT NULL,
        FOREIGN KEY (contact_id) REFERENCES contact (id),
        FOREIGN KEY (tag_id) REFERENCES tag (id)
    );
"""

GROUP = """
    CREATE TABLE IF NOT EXISTS group_ (
        id integer PRIMARY KEY,
        contact_id integer NOT NULL,
        tag_id integer NOT NULL,
        FOREIGN KEY (contact_id) REFERENCES contact (id),
        FOREIGN KEY (tag_id) REFERENCES tag (id)
    );
"""

def init_database_structure():
    """Création de la base de données"""
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute(CONTACT)
    c.execute(TAG)
    c.execute(PHONE)
    c.execute(MAIL)
    c.execute(ADDRESS)
    c.execute(GROUP)
    conn.commit()
    conn.close()


def init_database_tag():
    """Insertion de tags par défaut.
    À appeler après initialisation de la base de données."""
    for tag in DEFAULT_TAGS:
        add_tag(**tag)


def add_contact(**kwargs) -> int:
    """Insertion d'un nouveau contact. Retourne l'id correspondant."""
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
    """Insertion d'un numéro de téléphone associé à un contact et à un tag."""
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("""INSERT INTO phone 
                 (number, contact_id, tag_id) 
                 VALUES (:number, :contact_id, :tag_id)""", kwargs)
    conn.commit()
    conn.close()


def add_mail(**kwargs):
    """Insertion d'un mail associé à un contact et à un tag."""
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("""INSERT INTO mail 
                 (mail, contact_id, tag_id) 
                 VALUES (:mail, :contact_id, :tag_id)""", kwargs)
    conn.commit()
    conn.close()


def add_address(**kwargs):
    """Insertion d'une adresse associée à un contact et à un tag."""
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("""INSERT INTO address 
                 (address, contact_id, tag_id) 
                 VALUES (:address, :contact_id, :tag_id)""", kwargs)
    conn.commit()
    conn.close()


def add_tag_group_at_contact(id_contact: int, id_tag: int):
    """Insertion d'un groupe associé à un contact et à un tag."""
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    values = {"id": None, "contact_id": id_contact, "tag_id": id_tag}
    c.execute("INSERT INTO group_ VALUES (:id, :contact_id, :tag_id)", values)
    conn.commit()
    conn.close()


def add_tag(**kwargs) -> int:
    """Insertion d'un nouveau tag avec sa catégorie. Retourne l'id correspondant."""
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO tag (tag, category) VALUES (:tag, :category)", kwargs)
    last_id = c.lastrowid
    conn.commit()
    conn.close()
    return last_id

##############
#    READ    #
##############

def get_tag_to_category_group() -> list[tuple[str, int]]:
    """Retourne une liste de tuple où chaque tuple est un tag de la catégorie 'group' et son id"""
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("""SELECT tag.tag, tag.id FROM tag
                 WHERE category='group'""")
    values = c.fetchall()
    conn.close()
    return values


def get_tag_to_category_group_by_contact(id_contact: int) -> tuple[tuple[str], tuple[int]]:
    """Retourne deux tuples pour un contact donné :
    L'un des tags associés à la catégrie 'group'.
    L'autre des id correspondants au premier."""
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
    """Retourne deux listes :
    L'une des tags associés à la catégrie 'phone'.
    L'autre des id correspondants à la première."""
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("SELECT id, tag FROM tag WHERE category='phone'")
    values = c.fetchall()
    conn.close()
    return [tag[1] for tag in values], [idx[0] for idx in values]


def get_tag_to_category_mail() -> tuple[list[str], list[int]]:
    """Retourne deux listes :
    L'une des tags associés à la catégrie 'mail'.
    L'autre des id correspondants à la première."""
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("SELECT id, tag FROM tag WHERE category='mail'")
    values = c.fetchall()
    conn.close()
    return [tag[1] for tag in values], [idx[0] for idx in values]


def get_tag_to_category_address() -> tuple[list[str], list[int]]:
    """Retourne deux listes :
    L'une des tags associés à la catégrie 'address'.
    L'autre des id correspondants à la première."""
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("SELECT id, tag FROM tag WHERE category='address'")
    values = c.fetchall()
    conn.close()
    return [tag[1] for tag in values], [idx[0] for idx in values]


def get_contact_informations(id_contact: int) -> tuple:
    """Retourne les données d'un contact"""
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    d = {"id_contact": id_contact}
    c.execute("SELECT profile_picture, birthday, company, job FROM contact WHERE id=:id_contact", d)
    data = c.fetchone()
    conn.close()
    return data


def get_contact_group(id_contact: int) -> str:
    """Retourne les tags de la catégorie groupe d'un contact"""
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    d = {"id_contact": id_contact}
    c.execute("SELECT tag FROM tag INNER JOIN group_ ON tag.id = group_.tag_id WHERE group_.contact_id=:id_contact", d)
    data = c.fetchall()
    conn.close()
    return ", ".join([d[0] for d in data])

##############
#   UPDATE   #
##############

def update_tag(**kwargs):
    """Remplacement de l'intitulé d'un tag."""
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    c.execute("""UPDATE tag SET tag=:tag 
                 WHERE id=:id_""", kwargs)
    conn.commit()
    conn.close()


def update_contact(**kwargs):
    """Modification d'un contact hormis 'profile_picture'."""
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
    """Modification d'un numéro de téléphone et du tag associé."""
    conn = sqlite3.connect(DATA_FILE)
    d = {'number': number, 'id_tag': id_tag, 'id_phone': id_phone}
    c = conn.cursor()
    c.execute("UPDATE phone SET number=:number, tag_id=:id_tag WHERE phone.id=:id_phone", d)
    conn.commit()
    conn.close()


def update_mail(mail: str, id_tag: int, id_mail: int):
    """Modification d'un mail et du tag associé."""
    conn = sqlite3.connect(DATA_FILE)
    d = {'mail': mail, 'id_tag': id_tag, 'id_mail': id_mail}
    c = conn.cursor()
    c.execute("UPDATE mail SET mail=:mail, tag_id=:id_tag WHERE mail.id=:id_mail", d)
    conn.commit()
    conn.close()


def update_address(address: str, id_tag: int, id_address: int):
    """Modification d'une adresse et du tag associé."""
    conn = sqlite3.connect(DATA_FILE)
    d = {'address': address, 'id_tag': id_tag, 'id_address': id_address}
    c = conn.cursor()
    c.execute("UPDATE address SET address=:address, tag_id=:id_tag WHERE address.id=:id_address", d)
    conn.commit()
    conn.close()


def update_profil_picture(id_contact: int, filename: str):
    """Remplacement du nom de fichier pour la 'profile_picture' d'un contact."""
    conn = sqlite3.connect(DATA_FILE)
    d = {'id': id_contact, 'pp': filename}
    c = conn.cursor()
    c.execute("UPDATE contact SET profile_picture=:pp WHERE id=:id", d)
    conn.commit()
    conn.close()

##############
#   DELETE   #
##############

def del_group_of_contact(id_contact: int, id_tag: int):
    """Suppression d'un groupe asssocié à un contact."""
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    values = {"contact_id": id_contact, "tag_id": id_tag}
    c.execute("DELETE FROM group_ WHERE contact_id=:contact_id AND tag_id=:tag_id", values)
    conn.commit()
    conn.close()


def del_contact_by_id(id_contact: int):
    """Suppression d'un contact :
        - Suppression de tous les liens vers le contact dans les tables jointes.
        - Suppression du contact lui-même."""
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
    """Suppression d'un numéro de téléphone en fonction de son id"""
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    phone = {"phone_id": id_phone}
    c.execute("DELETE FROM phone WHERE id=:phone_id", phone)
    conn.commit()
    conn.close()


def del_mail_by_id(id_mail: int):
    """Suppression d'un mail en fonction de son id"""
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    mail = {"mail_id": id_mail}
    c.execute("DELETE FROM mail WHERE id=:mail_id", mail)
    conn.commit()
    conn.close()


def del_address_by_id(id_address: int):
    """Suppression d'une adresse en fonction de son id"""
    conn = sqlite3.connect(DATA_FILE)
    c = conn.cursor()
    address = {"address_id": id_address}
    c.execute("DELETE FROM address WHERE id=:address_id", address)
    conn.commit()
    conn.close()


def del_tag_by_id(id_tag: int, category: str) -> bool:
    """Suppression d'un tag seulement s'il n'est pas associé."""
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
    init_database_structure()
    # init_database_tag()
