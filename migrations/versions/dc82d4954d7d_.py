"""empty message

Revision ID: dc82d4954d7d
Revises: 7d4111dbe579
Create Date: 2016-02-05 16:05:50.100601

"""

# revision identifiers, used by Alembic.
revision = 'dc82d4954d7d'
down_revision = '7d4111dbe579'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('articles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=64), nullable=True),
    sa.Column('url', sa.String(length=128), nullable=True),
    sa.Column('date', sa.Boolean(), nullable=True),
    sa.Column('feed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['feed_id'], ['feeds.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('articles')
    ### end Alembic commands ###