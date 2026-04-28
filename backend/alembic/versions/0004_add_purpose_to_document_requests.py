"""add purpose column to document_requests

Revision ID: 0004_add_purpose_to_document_requests
Revises: 0003_fix_refresh_tokens
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_add_doc_request_purpose"
down_revision = "0003_fix_refresh_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "document_requests",
        sa.Column("purpose", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("document_requests", "purpose")
