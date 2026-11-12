"""add source_image column)




Revision ID: 1dd0b217d82d
Revises: 72b129ad58de
Create Date: 2026-10-02 16:39:47.013059

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "1dd0b217d82d"
down_revision: Union[str, Sequence[str], None] = "72b129ad58de"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column("images", sa.Column("source_image", sa.String(), nullable=False))



def downgrade() -> None:

    op.drop_column("images", "source_image")

