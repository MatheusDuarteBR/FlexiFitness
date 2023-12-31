"""newer updates

Revision ID: d87391667701
Revises: 4d5dc3580b54
Create Date: 2023-09-20 16:02:35.920985

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd87391667701'
down_revision = '4d5dc3580b54'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('perfil', schema=None) as batch_op:
        batch_op.add_column(sa.Column('altura', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('perfil', schema=None) as batch_op:
        batch_op.drop_column('altura')

    # ### end Alembic commands ###
