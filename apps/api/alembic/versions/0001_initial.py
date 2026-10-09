from alembic import op
import sqlalchemy as sa
revision='0001_initial'; down_revision=None; branch_labels=None; depends_on=None

def upgrade():
    op.create_table('scan_events', sa.Column('id',sa.Integer(),primary_key=True), sa.Column('severity',sa.String(length=32),nullable=False), sa.Column('category',sa.String(length=64),nullable=False), sa.Column('language',sa.String(length=16),nullable=False), sa.Column('score',sa.Integer(),nullable=False), sa.Column('engine_version',sa.String(length=32),nullable=False), sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=True))
    op.create_index('ix_scan_events_severity','scan_events',['severity'])
    op.create_index('ix_scan_events_category','scan_events',['category'])

def downgrade():
    op.drop_index('ix_scan_events_category', table_name='scan_events'); op.drop_index('ix_scan_events_severity', table_name='scan_events'); op.drop_table('scan_events')
