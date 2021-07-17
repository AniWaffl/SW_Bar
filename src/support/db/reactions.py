import sqlalchemy as sa
from .base import metadata
import datetime

reactions = sa.Table(
    "reactions", 
    metadata,

    sa.Column("channel_id", sa.Integer, nullable=False),
    sa.Column("message_id", sa.Integer, nullable=False),
    sa.Column("user_id", sa.Integer, nullable=False),
    sa.Column("created_at", sa.DateTime, default=datetime.datetime.utcnow),

    sa.UniqueConstraint("channel_id", "message_id", "user_id", name="uniq_reaction_constr")
)