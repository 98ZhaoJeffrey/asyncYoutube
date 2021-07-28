"""Change name to username

Revision ID: dbe594ba1d73
Revises: 5ce1dcf8d1ca
Create Date: 2021-07-26 23:26:16.349918

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'dbe594ba1d73'
down_revision = '5ce1dcf8d1ca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('username', sa.String(length=64), nullable=False))
    op.drop_column('user', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('name', mysql.VARCHAR(length=64), nullable=False))
    op.drop_column('user', 'username')
    # ### end Alembic commands ###