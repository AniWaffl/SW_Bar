import sqlalchemy as sa
from .base import metadata

resources = sa.Table(
    "resources", 
    metadata,

    sa.Column("id", sa.Integer, primary_key=True, unique=True),
    sa.Column("name", sa.String, nullable=False),
    sa.Column("icon", sa.String, nullable=True),
    sa.Column("count", sa.Integer, nullable=False, default='0', server_default='0'),
    sa.Column("need_to_store", sa.Integer, nullable=False, default='0', server_default='0'),

)
