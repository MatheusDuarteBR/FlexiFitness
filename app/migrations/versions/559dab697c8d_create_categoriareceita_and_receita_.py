"""Create CategoriaReceita and Receita models

Revision ID: 559dab697c8d
Revises: d87391667701
Create Date: 2023-10-01 10:17:49.977599

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '559dab697c8d'
down_revision = 'd87391667701'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categoria_receita',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nome')
    )
    op.create_table('receita',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(length=100), nullable=False),
    sa.Column('kcal', sa.Integer(), nullable=False),
    sa.Column('categoria_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['categoria_id'], ['categoria_receita.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('receita')
    op.drop_table('categoria_receita')
    # ### end Alembic commands ###