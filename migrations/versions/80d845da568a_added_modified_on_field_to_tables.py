"""Added modified_on field to tables

Revision ID: 80d845da568a
Revises: 5dad1efc0522
Create Date: 2024-01-03 10:55:54.914386

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80d845da568a'
down_revision = '5dad1efc0522'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('modified_on', sa.DateTime(timezone=True), nullable=False))

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('modified_on', sa.DateTime(timezone=True), nullable=False))

    with op.batch_alter_table('subreddit', schema=None) as batch_op:
        batch_op.add_column(sa.Column('modified_on', sa.DateTime(timezone=True), nullable=False))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('modified_on', sa.DateTime(timezone=True), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('modified_on')

    with op.batch_alter_table('subreddit', schema=None) as batch_op:
        batch_op.drop_column('modified_on')

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('modified_on')

    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_column('modified_on')

    # ### end Alembic commands ###