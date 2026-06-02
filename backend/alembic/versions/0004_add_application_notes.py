"""add_application_notes

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-02 10:16:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40162200e499'
down_revision: Union[str, None] = '30162200e498'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('applications', sa.Column('admin_notes', sa.Text(), nullable=True))
    op.add_column('applications', sa.Column('student_reply', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('applications', 'student_reply')
    op.drop_column('applications', 'admin_notes')
