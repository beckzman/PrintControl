"""Add printer_web_crawls table

Revision ID: 7c1d99ea1593
Revises: 79c27a1b110d
Create Date: 2026-02-09 11:20:10.856978

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c1d99ea1593'
down_revision: Union[str, Sequence[str], None] = '79c27a1b110d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the printer_web_crawls table
    op.create_table('printer_web_crawls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('printer_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['printer_id'], ['printers.id'], name='fk_web_crawl_printer_id'),
        sa.PrimaryKeyConstraint('id', name='pk_printer_web_crawls'),
        sa.UniqueConstraint('printer_id', name='uq_printer_web_crawl_printer_id')
    )
    with op.batch_alter_table('printer_web_crawls', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_printer_web_crawls_id'), ['id'], unique=False)

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('printer_web_crawls')
