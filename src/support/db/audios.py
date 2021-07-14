import sqlalchemy as sa
from .base import metadata
import datetime

audios = sa.Table(
    "audios", 
    metadata,

    sa.Column("db_id", sa.Integer, primary_key=True, unique=True),
    sa.Column("message_id", sa.Integer, unique=True, nullable=False),
    sa.Column("title", sa.String, nullable=True),
    sa.Column("performer", sa.String, nullable=True),
    sa.Column("file_id", sa.String, nullable=False),
    sa.Column("duration", sa.Integer, nullable=False),
    sa.Column("is_banned", sa.Boolean, default=False),
    sa.Column("created_at", sa.DateTime, default=datetime.datetime.utcnow),
)