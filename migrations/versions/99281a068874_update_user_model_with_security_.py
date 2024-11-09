"""update_user_model_with_security_questions

Revision ID: 99281a068874
Revises: 001
Create Date: 2024-11-09 21:45:08.970773

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '99281a068874'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('webhook')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('security_answer1', sa.String(length=256), nullable=False))
        batch_op.add_column(sa.Column('security_answer2', sa.String(length=256), nullable=False))
        batch_op.add_column(sa.Column('security_answer3', sa.String(length=256), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('security_answer3')
        batch_op.drop_column('security_answer2')
        batch_op.drop_column('security_answer1')

    op.create_table('webhook',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
