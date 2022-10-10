import sqlalchemy as sa
import datetime as dt
from sqlalchemy import \
    Column, String, BigInteger, DateTime, Time, \
    Date, ForeignKey, Boolean, Float, Integer, event
from sqlalchemy.orm import relation, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.event import listens_for

# connecting
address = 'postgresql://postgres:postgres@pg:5432/temperatura'
engine = sa.create_engine(address)

if not database_exists(engine.url):
    create_database(engine.url)

connect = engine.connect()

# metadados
meta = sa.MetaData(bind=engine)
# base declarativa
Base = declarative_base(bind=connect, metadata=meta)

# incluir dados
sqlSessionMaker = sessionmaker()
sqlSessionMaker.configure(bind=engine)

session = sqlSessionMaker()

type_coercion = {
    Integer: int,
    String: str,
    Float: float,
    BigInteger: int,
    # Boolean: lambda x: x,
    Date: lambda x: dt.date.strptime(x, '%d/%m/%Y'),
    # DateTime: lambda x: x,
    # Time: lambda x: x

}

# this event is called whenever an attribute
# on a class is instrumented
@event.listens_for(Base, 'attribute_instrument')
def configure_listener(class_, key, inst):
    if not hasattr(inst.property, 'columns'):
        return
    # this event is called whenever a "set"
    # occurs on that instrumented attribute
    @event.listens_for(inst, "set", retval=True)
    def set_(instance, value, oldvalue, initiator):
        desired_type = type_coercion.get(
            inst.property.columns[0].type.__class__,
            lambda x: x
        )
        coerced_value = desired_type(value)
        if desired_type == str:
            coerced_value = coerced_value.upper()
        return coerced_value

class Registro(Base):
    __tablename__ = 'registro'
    _registro = Column(BigInteger, primary_key=True)
    _da_estacao = Column(Integer, ForeignKey('estacao._estacao'))

    data = Column(Date)
    hora_utc = Column(String)
    temperatura_C = Column(Float)
    umidade_relativa = Column(Float)
    pressao_hpa = Column(Float)
    velocidade_vento_ms = Column(Float)
    direcao_vento_grad = Column(Float)
    nebulosidade_dec = Column(Float)
    insolacao_h = Column(Float)
    temp_max_C = Column(Float)
    temp_min_C = Column(Float)
    chuva_mm = Column(Float)
    umidade_min = Column(Float)
    umidade_max = Column(Float)
    orvalho_C = Column(Float)
    orvalho_min_C = Column(Float)
    orvalho_max_C = Column(Float)
    pressao_min_hpa = Column(Float)
    pressao_max_hpa = Column(Float)
    rajada_vento_ms = Column(Float)
    radiacao_kjmq = Column(Float)

    def __repr__(self):
        return f'<Registro({self.data}, {self.hora_utc})>'


class Estacao(Base):
    __tablename__ = 'estacao'
    _estacao = Column(BigInteger, primary_key=True)
    _registros = relationship('Registro')
    
    dc_nome = Column(String)
    sg_estado = Column(String)
    cd_situacao = Column(String)
    vl_latitude = Column(Float)
    vl_longitude = Column(Float)
    vl_altitude = Column(Float)
    dt_inicio_operacao = Column(Date)
    cd_estacao = Column(String)

    def __repr__(self):
        return f'<Estacao({self.cd_estacao})>'


class Altitude(Base):
    __tablename__ = 'altitude'
    _altitude = Column(BigInteger, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    valor = Column(Float)

    def __repr__(self):
        return f'<Altitude(long={self.longitude}, lat={self.latitude})>'


meta.create_all(engine)