"""user to user rework

Revision ID: 47149badfccb
Revises: f6dfe7b00ce7
Create Date: 2022-05-04 00:13:21.987788

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '47149badfccb'
down_revision = 'f6dfe7b00ce7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subscribes',
    sa.Column('subscriber_id', sa.Integer(), nullable=True),
    sa.Column('subscribed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['subscribed_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['subscriber_id'], ['users.id'], )
    )
    op.create_index(op.f('ix_subscribes_subscribed_id'), 'subscribes', ['subscribed_id'], unique=False)
    op.create_index(op.f('ix_subscribes_subscriber_id'), 'subscribes', ['subscriber_id'], unique=False)
    op.drop_table('user_to_user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_to_user',
    sa.Column('subscriber_id', sa.INTEGER(), nullable=False),
    sa.Column('creator_id', sa.INTEGER(), nullable=False),
    sa.Column('status', sa.VARCHAR(), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['subscriber_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('subscriber_id', 'creator_id')
    )
    op.drop_index(op.f('ix_subscribes_subscriber_id'), table_name='subscribes')
    op.drop_index(op.f('ix_subscribes_subscribed_id'), table_name='subscribes')
    op.drop_table('subscribes')
    # ### end Alembic commands ###
