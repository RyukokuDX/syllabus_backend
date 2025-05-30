"""add syllabus study system

Revision ID: 20240529_add_syllabus_study_system
Revises: 20240529_add_syllabus_master
Create Date: 2024-05-29 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240529_add_syllabus_study_system'
down_revision = '20240529_add_syllabus_master'
branch_labels = None
depends_on = None

def upgrade():
    # syllabus_study_systemテーブルの作成
    op.create_table(
        'syllabus_study_system',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_syllabus_id', sa.Integer(), nullable=False),
        sa.Column('target_syllabus_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['source_syllabus_id'], ['syllabus_master.syllabus_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_syllabus_id'], ['syllabus_master.syllabus_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_syllabus_id', 'target_syllabus_id', name='uix_syllabus_study_system_unique')
    )

    # インデックスの作成
    op.create_index('idx_syllabus_study_system_source', 'syllabus_study_system', ['source_syllabus_id'])
    op.create_index('idx_syllabus_study_system_target', 'syllabus_study_system', ['target_syllabus_id'])

def downgrade():
    # インデックスの削除
    op.drop_index('idx_syllabus_study_system_target', table_name='syllabus_study_system')
    op.drop_index('idx_syllabus_study_system_source', table_name='syllabus_study_system')

    # syllabus_study_systemテーブルの削除
    op.drop_table('syllabus_study_system') 