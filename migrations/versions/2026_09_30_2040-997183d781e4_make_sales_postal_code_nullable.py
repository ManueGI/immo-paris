"""make sales postal_code nullable

Revision ID: 997183d781e4
Revises: 88c790162a0f
Create Date: 2026-09-30 20:40:40.801490+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "997183d781e4"
down_revision: str | Sequence[str] | None = "88c790162a0f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # A few DVF sales have no postal code: keep them rather than drop valid sales
    op.alter_column("sales", "postal_code", existing_type=sa.VARCHAR(length=5), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Fails on purpose if sales without a postal code exist: deleting them silently would
    # lose data. Remove or fix those rows explicitly before downgrading.
    op.alter_column("sales", "postal_code", existing_type=sa.VARCHAR(length=5), nullable=False)
