"""adding string constraints to some column in users table

Revision ID: 71fc9535a771
Revises: 9fcdcaf06d83
Create Date: 2024-09-11 10:23:43.688828

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71fc9535a771'
down_revision: Union[str, None] = '9fcdcaf06d83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
