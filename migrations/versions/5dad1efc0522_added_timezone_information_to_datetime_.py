"""added timezone information to datetime fields

Revision ID: 5dad1efc0522
Revises: af73fc7b0056
Create Date: 2023-12-25 21:33:11.119205

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "5dad1efc0522"
down_revision = "af73fc7b0056"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("comments", schema=None) as batch_op:
        batch_op.alter_column(
            "created_on",
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
        )

    with op.batch_alter_table("post", schema=None) as batch_op:
        batch_op.alter_column(
            "created_on",
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
        )

    with op.batch_alter_table("subreddit", schema=None) as batch_op:
        batch_op.alter_column(
            "created_on",
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
        )

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column(
            "cake_day",
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
        )

    with op.batch_alter_table("user_subreddit", schema=None) as batch_op:
        batch_op.alter_column(
            "date_of_joining",
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user_subreddit", schema=None) as batch_op:
        batch_op.alter_column(
            "date_of_joining",
            existing_type=sa.DateTime(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column(
            "cake_day",
            existing_type=sa.DateTime(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )

    with op.batch_alter_table("subreddit", schema=None) as batch_op:
        batch_op.alter_column(
            "created_on",
            existing_type=sa.DateTime(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )

    with op.batch_alter_table("post", schema=None) as batch_op:
        batch_op.alter_column(
            "created_on",
            existing_type=sa.DateTime(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )

    with op.batch_alter_table("comments", schema=None) as batch_op:
        batch_op.alter_column(
            "created_on",
            existing_type=sa.DateTime(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )

    # ### end Alembic commands ###
