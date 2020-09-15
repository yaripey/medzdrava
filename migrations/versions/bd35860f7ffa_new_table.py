"""new table

Revision ID: bd35860f7ffa
Revises: 7abf0a24b153
Create Date: 2020-08-17 20:51:01.870110

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd35860f7ffa'
down_revision = '7abf0a24b153'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blogpost',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('main_image_path', sa.String(length=300), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blogpost')
    # ### end Alembic commands ###
