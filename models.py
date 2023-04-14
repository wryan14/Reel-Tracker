from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float 
from sqlalchemy import Table, ForeignKey
from sqlalchemy.orm import  sessionmaker, relationship 
from sqlalchemy.ext.declarative import declarative_base 
import datetime

engine = create_engine('postgresql://wryan14:89957@localhost:5432/mydb', echo=False)
Session = sessionmaker(bind=engine) 
session = Session() 

Base = declarative_base() 


class IMDB_Movies(Base):
    __tablename__='imdb_movie'
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    runtime = Column(Integer)
    budget = Column(String(100))
    opening_weekend = Column(String(100))
    worldwide_gross = Column(String(100))
    rating = Column(Float)
    votes = Column(Integer)
    cover_url = Column(String(1000))
    cover_url_full = Column(String(1000))
    plot_outline = Column(String(10000))
    year  = Column(Integer)
    plot = Column(String(100000))
    synopsis = Column(String(100000))
    locations = Column(String(200))
    genres = Column(String(100))

class IMDB_Persons(Base):
    __tablename__='imdb_person'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))

class IMDB_Companies(Base):
    __tablename__='imdb_company'
    id = Column(Integer, primary_key=True)
    name = Column(String(120))

class Personal(Base):
    __tablename__='personal'
    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer)
    watch_date = Column(String(100))
    rating = Column(Integer)
    method = Column(String(100))

class Movie_Cast(Base):
    __tablename__='moviecast'
    id =  Column(Integer, primary_key=True)
    movie_id = Column(Integer)
    person_id = Column(Integer)

class Directors(Base):
    __tablename__='director'
    id =  Column(Integer, primary_key=True)
    movie_id = Column(Integer)
    person_id = Column(Integer)

class Producers(Base):
    __tablename__='producer'
    id =  Column(Integer, primary_key=True)
    movie_id = Column(Integer) 
    person_id = Column(Integer)

class Writers(Base):
    __tablename__='writer'
    id =  Column(Integer, primary_key=True)
    movie_id = Column(Integer)
    person_id = Column(Integer)

class Composers(Base):
    __tablename__='composer'
    id =  Column(Integer, primary_key=True)
    movie_id = Column(Integer)
    person_id = Column(Integer)

class Cinematographers(Base):
    __tablename__='cinematographer'
    id =  Column(Integer, primary_key=True)
    movie_id = Column(Integer)
    person_id = Column(Integer)

class Production_Company(Base):
    __tablename__='production_company'
    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer)
    company_id = Column(Integer) 


Base.metadata.create_all(engine)

session.commit() 