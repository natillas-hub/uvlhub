"""create_deposition_model

Revision ID: e7fe84368699
Revises: 99281a068874
Create Date: 2024-12-08 23:14:11.549620

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7fe84368699'
down_revision = '99281a068874'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('deposition',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dep_metadata', sa.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('deposition')
    # ### end Alembic commands ###
