import sqlalchemy as sa
from .base import metadata
import datetime

chats = sa.Table(
    "chats", 
    metadata,

    sa.Column("db_id", sa.Integer, primary_key=True, unique=True),
    sa.Column("id", sa.BigInteger, index=True, unique=True, nullable=False),
    sa.Column("username", sa.String, default=None),
    sa.Column("title", sa.String, nullable=False),
    sa.Column("invite_link", sa.String),

    sa.Column("is_banned", sa.Boolean, default=False),

    # Data
    sa.Column("is_parse_smoothie", sa.Boolean, default=False),

    sa.Column("created_at", sa.DateTime, default=datetime.datetime.utcnow),
    sa.Column("updated_at", sa.DateTime, default=datetime.datetime.utcnow)
)