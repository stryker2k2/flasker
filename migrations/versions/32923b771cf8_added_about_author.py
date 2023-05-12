"""Added about_author

Revision ID: 32923b771cf8
Revises: a9f19c2e76fc
Create Date: 2023-05-12 13:41:43.930130

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32923b771cf8'
down_revision = 'a9f19c2e76fc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('about_author', sa.Text(length=500), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('about_author')

    # ### end Alembic commands ###
