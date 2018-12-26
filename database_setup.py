#!/usr/bin/env python3
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy import String, Text, Date, engine, create_engine
from sqlalchemy.orm import relationship

Base = declarative_base()


class Model(Base):
    __tablename__ = 'model'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    information = Column(Text)
    created_date = Column(Date)
    carmaker_id = Column(Integer, ForeignKey('carmaker.id'))
    author = Column(Text)

    carmaker = relationship(
        "Carmaker", back_populates="models")


class Carmaker(Base):
    __tablename__ = 'carmaker'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('carmaker.id'))
    name = Column(String)
    author = Column(Text)

    models = relationship(
        "Model", back_populates="carmaker", cascade="all, delete")


# this will recreate the database tables if it is not present
engine = create_engine('sqlite:///models.db', echo=True)
Base.metadata.create_all(engine)
