"""add user table

Revision ID: 5a14422ab356
Revises: dbe594ba1d73
Create Date: 2021-07-26 23:28:47.845935

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a14422ab356'
down_revision = 'dbe594ba1d73'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('room_code', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['room_code'], ['room.code'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
