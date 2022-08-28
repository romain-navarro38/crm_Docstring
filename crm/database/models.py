import datetime

from sqlalchemy import create_engine, Integer, Column, String, Boolean, ForeignKey, DateTime, Enum, Float
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from crm.api.utils import DATA_FILE


engine = create_engine(f'sqlite:///{DATA_FILE}', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Contact(Base):
    __tablename__ = "contact"

    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String)
    surname = Column(String)
    birthday = Column(DateTime, default=datetime.datetime.now)

    mail = relationship('Mail', back_populates='contact')
    phone = relationship('Phone', back_populates='contact')


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String)
    category = Column(String)

    mail = relationship('Mail', back_populates='tag')
    phone = relationship('Phone', back_populates='tag')


class Mail(Base):
    __tablename__ = 'mail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contact_id = Column(Integer, ForeignKey('contact.id'), nullable=False)
    tag_id = Column(Integer, ForeignKey('tag.id'), nullable=False)
    mail = Column(String)
    favori = Column(Boolean, nullable=True)

    contact = relationship('Contact', back_populates='mail')
    tag = relationship('Tag', back_populates='mail')


class Phone(Base):
    __tablename__ = 'phone'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contact_id = Column(Integer, ForeignKey('contact.id'), nullable=False)
    tag_id = Column(Integer, ForeignKey('tag.id'), nullable=False)
    phone = Column(String)
    favori = Column(Boolean, nullable=False)

    contact = relationship('Contact', back_populates='phone')
    tag = relationship('Tag', back_populates='phone')


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    # session.add(Contact(firstname="Bertrand", surname="Dales"))
    # session.commit()
    contact = session.query(Contact).where(Contact.id == 1)
    print(contact.firstname)
    print(datetime.datetime.strptime(str(contact.birthday), "%Y-%m-%d"))
