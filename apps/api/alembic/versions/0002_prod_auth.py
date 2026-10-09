"""production auth and feedback
Revision ID: 0002_prod_auth
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa
revision='0002_prod_auth'; down_revision='0001_initial'; branch_labels=None; depends_on=None

def upgrade():
    op.create_table('users',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('email',sa.String(320),nullable=False),sa.Column('password_hash',sa.String(512),nullable=False),sa.Column('display_name',sa.String(120)),sa.Column('is_active',sa.Boolean(),nullable=False,server_default=sa.text('true')),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.func.now()))
    op.create_index('ix_users_email','users',['email'],unique=True)
    op.create_table('refresh_sessions',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('token_hash',sa.String(128),nullable=False),sa.Column('user_id',sa.Integer(),sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),sa.Column('expires_at',sa.DateTime(timezone=True),nullable=False),sa.Column('revoked_at',sa.DateTime(timezone=True)),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()))
    op.create_index('ix_refresh_sessions_token_hash','refresh_sessions',['token_hash'],unique=True); op.create_index('ix_refresh_sessions_user_id','refresh_sessions',['user_id']); op.create_index('ix_refresh_sessions_expires_at','refresh_sessions',['expires_at'])
    op.add_column('scan_events',sa.Column('cloud_used',sa.Boolean(),nullable=False,server_default=sa.text('false')))
    op.add_column('scan_events',sa.Column('user_id',sa.Integer(),sa.ForeignKey('users.id',ondelete='SET NULL')))
    op.create_index('ix_scan_events_user_id','scan_events',['user_id'])
    op.create_table('feedback',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('scan_id',sa.Integer(),sa.ForeignKey('scan_events.id',ondelete='SET NULL')),sa.Column('verdict',sa.String(32),nullable=False),sa.Column('reason',sa.Text()),sa.Column('user_id',sa.Integer(),sa.ForeignKey('users.id',ondelete='SET NULL')),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()))

def downgrade():
    op.drop_table('feedback'); op.drop_index('ix_scan_events_user_id',table_name='scan_events'); op.drop_column('scan_events','user_id'); op.drop_column('scan_events','cloud_used'); op.drop_index('ix_refresh_sessions_expires_at',table_name='refresh_sessions'); op.drop_index('ix_refresh_sessions_user_id',table_name='refresh_sessions'); op.drop_index('ix_refresh_sessions_token_hash',table_name='refresh_sessions'); op.drop_table('refresh_sessions'); op.drop_index('ix_users_email',table_name='users'); op.drop_table('users')
