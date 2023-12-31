"""New row of receipe table

Revision ID: bef2fbabd465
Revises: 855228c2ea41
Create Date: 2023-10-02 20:45:24.452308

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bef2fbabd465'
down_revision = '855228c2ea41'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('receita', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tempo_de_preparo', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('receita', schema=None) as batch_op:
        batch_op.drop_column('tempo_de_preparo')

    # ### end Alembic commands ###
