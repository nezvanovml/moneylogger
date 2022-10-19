"""empty message

Revision ID: 8b55ae54aa6a
Revises: 
Create Date: 2022-10-18 09:05:42.333966

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8b55ae54aa6a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('privilegiexrole')
    op.drop_table('userxprivilegie')
    op.drop_table('privilegie')
    op.add_column('user', sa.Column('first_name', sa.String(length=100), nullable=False))
    op.add_column('user', sa.Column('last_name', sa.String(length=100), nullable=False))
    op.add_column('user', sa.Column('gender', sa.String(length=30), nullable=True))
    op.add_column('user', sa.Column('birthdate', sa.DateTime(), nullable=False))
    op.drop_column('userxrole', 'expiration')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('userxrole', sa.Column('expiration', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('user', 'birthdate')
    op.drop_column('user', 'gender')
    op.drop_column('user', 'last_name')
    op.drop_column('user', 'first_name')
    op.create_table('privilegie',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('privilegie_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('humanreadablename', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='privilegie_pkey'),
    sa.UniqueConstraint('humanreadablename', name='privilegie_humanreadablename_key'),
    sa.UniqueConstraint('name', name='privilegie_name_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('userxprivilegie',
    sa.Column('user', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('privilegie', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('expiration', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['privilegie'], ['privilegie.id'], name='userxprivilegie_privilegie_fkey'),
    sa.ForeignKeyConstraint(['user'], ['user.id'], name='userxprivilegie_user_fkey'),
    sa.PrimaryKeyConstraint('user', 'privilegie', name='userxprivilegie_pkey')
    )
    op.create_table('privilegiexrole',
    sa.Column('privilegie', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('role', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('expiration', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['privilegie'], ['privilegie.id'], name='privilegiexrole_privilegie_fkey'),
    sa.ForeignKeyConstraint(['role'], ['role.id'], name='privilegiexrole_role_fkey'),
    sa.PrimaryKeyConstraint('privilegie', 'role', name='privilegiexrole_pkey')
    )
    # ### end Alembic commands ###