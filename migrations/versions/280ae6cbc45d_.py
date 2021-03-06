"""empty message

Revision ID: 280ae6cbc45d
Revises: bf86e89a659c
Create Date: 2020-07-17 01:40:13.510438

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '280ae6cbc45d'
down_revision = 'bf86e89a659c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('venues', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('venues', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'website')
    op.drop_column('venues', 'seeking_venue')
    op.drop_column('venues', 'seeking_description')
    # ### end Alembic commands ###
