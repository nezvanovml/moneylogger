"""empty message

Revision ID: 62e0540ab8f5
Revises: e129cc6ef5f9
Create Date: 2022-10-13 08:28:21.099740

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '62e0540ab8f5'
down_revision = 'e129cc6ef5f9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('date_of_spent', sa.DateTime(), nullable=True),
    sa.Column('sum', sa.Float(), nullable=False),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('spents')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('spents',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('category_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('date_of_spent', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('sum', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('comment', sa.TEXT(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='spents_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='spents_pkey')
    )
    op.drop_table('transactions')
    # ### end Alembic commands ###
