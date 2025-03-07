"""Change photo column type to JSON

Revision ID: 2eff6fd9a63d
Revises: 
Create Date: 2025-02-24 15:06:43.410982

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2eff6fd9a63d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('ALTER TABLE items ALTER COLUMN photo TYPE JSON USING photo::json')
    op.drop_table('item_photos')
    op.alter_column('items', 'photo',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.JSON(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('ALTER TABLE items ALTER COLUMN photo TYPE VARCHAR(255) USING photo::text')
    op.alter_column('items', 'photo',
               existing_type=sa.JSON(),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)
    op.create_table('item_photos',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('item_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('photo', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['item_id'], ['items.id'], name='item_photos_item_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='item_photos_pkey')
    )
    # ### end Alembic commands ###
