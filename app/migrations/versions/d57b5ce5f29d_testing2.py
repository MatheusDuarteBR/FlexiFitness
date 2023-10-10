"""testing2

Revision ID: d57b5ce5f29d
Revises: bc527bfc5897
Create Date: 2023-10-03 09:06:27.390822

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd57b5ce5f29d'
down_revision = 'bc527bfc5897'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('receita', schema=None) as batch_op:
        batch_op.add_column(sa.Column('modo_de_preparo', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('receita', schema=None) as batch_op:
        batch_op.drop_column('modo_de_preparo')

    # ### end Alembic commands ###