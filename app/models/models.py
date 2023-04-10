import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

Base = declarative_base()
Base.metadata = MetaData()

class GoogleTrends(Base):
    __tablename__ = 'influenza_gtrends'

    id = sa.Column(sa.Integer, primary_key=True)

    date = sa.Column(sa.DateTime)
    cough = sa.Column(sa.Integer)
    flu = sa.Column(sa.Integer)
    tamiflu = sa.Column(sa.Integer)
    sore_throat = sa.Column(sa.Integer)
    level = sa.Column(sa.String(200))
    state = sa.Column(sa.String(200))
    state_code = sa.Column(sa.String(200))
    week_number = sa.Column(sa.Integer)
    year = sa.Column(sa.Integer)

    sa.UniqueConstraint(date, level, state, state_code, name="unique_gtrends")

class ILINet(Base):
    __tablename__ = 'influenza_ilinet'

    id = sa.Column(sa.Integer, primary_key=True)

    region_type = sa.Column(sa.String(200), nullable=False)
    region = sa.Column(sa.String(200))
    year = sa.Column(sa.Integer, nullable=False) 
    week = sa.Column(sa.Integer, nullable=False) 
    perc_weight_ili = sa.Column(sa.Float)
    perc_unweight_ili = sa.Column(sa.Float)
    age_0_4 = sa.Column(sa.Integer)
    age_25_49 = sa.Column(sa.Integer)
    age_25_64 = sa.Column(sa.Integer)
    age_5_24 = sa.Column(sa.Integer)
    age_50_64 = sa.Column(sa.Integer)
    age_65 = sa.Column(sa.Integer)
    ilitotal = sa.Column(sa.Integer)
    num_providers = sa.Column(sa.Integer)
    total_patients = sa.Column(sa.Integer)

    sa.UniqueConstraint(region_type, region, year, week, name="unique_ilinet")
