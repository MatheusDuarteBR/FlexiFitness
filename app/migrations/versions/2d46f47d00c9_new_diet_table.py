"""new diet table

Revision ID: 2d46f47d00c9
Revises: 4d99dc740109
Create Date: 2023-10-09 13:51:34.116069

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d46f47d00c9'
down_revision = '4d99dc740109'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dashboard_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(length=50), nullable=False),
    sa.Column('idade', sa.Integer(), nullable=False),
    sa.Column('genero', sa.String(length=10), nullable=False),
    sa.Column('nivel_atividade', sa.String(length=20), nullable=False),
    sa.Column('objetivo', sa.String(length=10), nullable=False),
    sa.Column('tipo_atividade', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('dieta', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cafe_manha', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('lanche_manha', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('almoco', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('cafe_tarde', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('janta', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('ceia', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('data_criacao', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('usuario_id', sa.Integer(), nullable=False))
        batch_op.alter_column('nome',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=50),
               existing_nullable=False)
        batch_op.drop_constraint('dieta_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'dashboard_user', ['usuario_id'], ['id'])
        batch_op.drop_column('idade')
        batch_op.drop_column('tmb')
        batch_op.drop_column('tipo_atividade')
        batch_op.drop_column('nivel_atividade')
        batch_op.drop_column('user_id')
        batch_op.drop_column('objetivo')
        batch_op.drop_column('genero')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('dieta', schema=None) as batch_op:
        batch_op.add_column(sa.Column('genero', sa.VARCHAR(length=10), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('objetivo', sa.VARCHAR(length=10), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('nivel_atividade', sa.VARCHAR(length=20), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('tipo_atividade', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('tmb', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('idade', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('dieta_user_id_fkey', 'usuario', ['user_id'], ['id'])
        batch_op.alter_column('nome',
               existing_type=sa.String(length=50),
               type_=sa.VARCHAR(length=100),
               existing_nullable=False)
        batch_op.drop_column('usuario_id')
        batch_op.drop_column('data_criacao')
        batch_op.drop_column('ceia')
        batch_op.drop_column('janta')
        batch_op.drop_column('cafe_tarde')
        batch_op.drop_column('almoco')
        batch_op.drop_column('lanche_manha')
        batch_op.drop_column('cafe_manha')

    op.drop_table('dashboard_user')
    # ### end Alembic commands ###