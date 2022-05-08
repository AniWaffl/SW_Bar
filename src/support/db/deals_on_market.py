import enum

import sqlalchemy as sa
from .base import metadata


class DealOffer(str, enum.Enum):
    buy = "buy"
    sell = "sell"


deals_on_market = sa.Table(
    "deals_on_market", 
    metadata,

    sa.Column("id", sa.Integer, primary_key=True, unique=True),
    sa.Column("offer", sa.Enum(DealOffer), nullable=False),
    sa.Column("user_id", sa.Integer, nullable=False),
    sa.Column("resource_id", sa.ForeignKey('resources.id'), nullable=False),
    sa.Column("count", sa.Integer, nullable=False),

)
