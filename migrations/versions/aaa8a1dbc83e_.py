"""empty message

Revision ID: aaa8a1dbc83e
Revises: cc11541b02d2
Create Date: 2016-02-09 10:44:48.479959

"""

# revision identifiers, used by Alembic.
revision = 'aaa8a1dbc83e'
down_revision = 'cc11541b02d2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('articles', sa.Column('date_collected', sa.DateTime(), nullable=True))
    op.add_column('articles', sa.Column('date_tweeted', sa.DateTime(), nullable=True))
    op.drop_column('articles', 'date')
    op.add_column('feeds', sa.Column('tweet_actif', sa.Boolean(), nullable=True))
    op.drop_column('feeds', 'Tweet_actif')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('feeds', sa.Column('Tweet_actif', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.drop_column('feeds', 'tweet_actif')
    op.add_column('articles', sa.Column('date', sa.DATE(), nullable=True))
    op.drop_column('articles', 'date_tweeted')
    op.drop_column('articles', 'date_collected')
    ### end Alembic commands ###
