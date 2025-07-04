"""Add program table

Revision ID: add_program_table
Revises: 9f0c9cd09105
Create Date: 2025-01-27 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

revision = "add_program_table"
down_revision = "9f0c9cd09105"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "program",
        sa.Column("id", sa.Text(), nullable=False, primary_key=True, unique=True),
        sa.Column("user_id", sa.Text(), nullable=True),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=True, default="active"),
        sa.Column("properties", sa.JSON(), nullable=True),
        sa.Column("summary_format", sa.JSON(), nullable=True),
        sa.Column("access_control", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.BigInteger(), nullable=True),
    )


def downgrade():
    op.drop_table("program") 