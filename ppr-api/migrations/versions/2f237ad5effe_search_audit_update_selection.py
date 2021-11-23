"""search audit update selection

Revision ID: 2f237ad5effe
Revises: 8fb9d269a9d4
Create Date: 2021-11-17 19:50:31.592562

"""
from alembic import op
import sqlalchemy as sa
from alembic_utils.pg_function import PGFunction
from sqlalchemy import text as sql_text

# revision identifiers, used by Alembic.
revision = '2f237ad5effe'
down_revision = '8fb9d269a9d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('search_requests', sa.Column('updated_selection', sa.JSON(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('search_requests', 'updated_selection')

    # ### end Alembic commands ###