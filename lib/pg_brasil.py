from sqlite3 import ProgrammingError
import sqlalchemy as sa
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relation, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from geoalchemy2 import Geometry

# connecting
address = 'postgresql://postgres:postgres@pg_brasil:5432/brasil'
engine = sa.create_engine(address)

if not database_exists(engine.url):
    create_database(engine.url)

connect = engine.connect()
connect.execute('CREATE EXTENSION IF NOT EXISTS postgis;')


# metadados
meta = sa.MetaData(bind=engine)
# base declarativa
Base = declarative_base(bind=connect, metadata=meta)

# incluir dados
sqlSessionMaker = sessionmaker()
sqlSessionMaker.configure(bind=engine)

session = sqlSessionMaker()



class Municipio(Base):
    __tablename__ = 'municipio'
    ibge = Column(Integer, primary_key=True)
    nome_uf = Column(String)
    nome_limpo_uf = Column(String)
    sigla_uf = Column(String)
    regiao_uf = Column(String)
    codigo_uf = Column(Integer)
    nome = Column(String)
    nome_limpo = Column(String)
    geometria = Column(Geometry('POLYGON'))
    da_uf = Column(Integer, ForeignKey('uf.codigo_ibge'))


class UF(Base):
    __tablename__ = 'uf'
    codigo_ibge = Column(Integer, primary_key=True)
    regiao = Column(String)
    sigla = Column(String)
    nome = Column(String)
    nome_limpo = Column(String)
    geometria = Column(Geometry('MULTIPOLYGON'))
    municipios = relationship('Municipio')


meta.create_all(engine)
