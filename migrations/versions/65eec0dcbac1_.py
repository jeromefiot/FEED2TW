"""empty message

Revision ID: 65eec0dcbac1
Revises: 044b32c8e3c5
Create Date: 2016-02-05 21:33:01.911882

"""

# revision identifiers, used by Alembic.
revision = '65eec0dcbac1'
down_revision = '044b32c8e3c5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('articles', sa.Column('tweeted', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('articles', 'tweeted')
    ### end Alembic commands ###
