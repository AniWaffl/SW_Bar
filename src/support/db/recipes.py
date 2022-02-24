import sqlalchemy as sa
from .base import metadata
import datetime

def now():
    return datetime.datetime.utcnow()

recipes = sa.Table(
    "recipes", 
    metadata,

    sa.Column("db_id", sa.Integer, primary_key=True, unique=True),
    sa.Column("from_user", sa.Integer, nullable=False),
    sa.Column("recipe", sa.String, nullable=False),
    sa.Column("pos_find", sa.Integer, nullable=False),
    sa.Column("bonus", sa.String, default=None),
    sa.Column("date", sa.DateTime, default=datetime.datetime.utcnow)
)