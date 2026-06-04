"""add financial fields to project

Revision ID: 66b7db660c6c
Revises: 498244d8a882
Create Date: 2026-06-04 08:29:41.553781

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66b7db660c6c'
down_revision: Union[str, Sequence[str], None] = '498244d8a882'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    risk_level = sa.Enum('LOW', 'MEDIUM', 'HIGH', name='risk_level')
    risk_level.create(op.get_bind(), checkfirst=True)

    op.add_column('PROJECT', sa.Column('min_amount', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('PROJECT', sa.Column('risk', sa.Enum('LOW', 'MEDIUM', 'HIGH', name='risk_level'), nullable=True))
    op.add_column('PROJECT', sa.Column('annual_expenses', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('PROJECT', sa.Column('annual_profits', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('PROJECT', sa.Column('roi', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('PROJECT', sa.Column('annual_benefits', sa.Numeric(precision=12, scale=2), nullable=True))


def downgrade() -> None:
    op.drop_column('PROJECT', 'annual_benefits')
    op.drop_column('PROJECT', 'roi')
    op.drop_column('PROJECT', 'annual_profits')
    op.drop_column('PROJECT', 'annual_expenses')
    op.drop_column('PROJECT', 'risk')
    op.drop_column('PROJECT', 'min_amount')

    sa.Enum(name='risk_level').drop(op.get_bind(), checkfirst=True)