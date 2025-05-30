"""update syllabus study system

Revision ID: 20240529_update_syllabus_study_system
Revises: 20240529_add_syllabus_study_system
Create Date: 2024-05-29 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240529_update_syllabus_study_system'
down_revision = '20240529_add_syllabus_study_system'
branch_labels = None
depends_on = None

def upgrade():
    # 既存のインデックスと制約を削除
    op.drop_index('idx_syllabus_study_system_target', table_name='syllabus_study_system')
    op.drop_index('idx_syllabus_study_system_source', table_name='syllabus_study_system')
    op.drop_constraint('uix_syllabus_study_system_unique', 'syllabus_study_system', type_='unique')
    op.drop_constraint('syllabus_study_system_target_syllabus_id_fkey', 'syllabus_study_system', type_='foreignkey')

    # target_syllabus_idカラムをtargetカラムに変更
    op.alter_column('syllabus_study_system', 'target_syllabus_id',
                    new_column_name='target',
                    type_=sa.Text(),
                    existing_type=sa.Integer(),
                    existing_nullable=False)

    # 新しいインデックスを作成
    op.create_index('idx_syllabus_study_system_source', 'syllabus_study_system', ['source_syllabus_id'])
    op.create_index('idx_syllabus_study_system_target', 'syllabus_study_system', ['target'])

def downgrade():
    # 新しいインデックスを削除
    op.drop_index('idx_syllabus_study_system_target', table_name='syllabus_study_system')
    op.drop_index('idx_syllabus_study_system_source', table_name='syllabus_study_system')

    # targetカラムをtarget_syllabus_idカラムに戻す
    op.alter_column('syllabus_study_system', 'target',
                    new_column_name='target_syllabus_id',
                    type_=sa.Integer(),
                    existing_type=sa.Text(),
                    existing_nullable=False)

    # 外部キー制約を再作成
    op.create_foreign_key('syllabus_study_system_target_syllabus_id_fkey',
                         'syllabus_study_system', 'syllabus_master',
                         ['target_syllabus_id'], ['syllabus_id'],
                         ondelete='CASCADE')

    # 一意制約を再作成
    op.create_unique_constraint('uix_syllabus_study_system_unique',
                              'syllabus_study_system',
                              ['source_syllabus_id', 'target_syllabus_id'])

    # インデックスを再作成
    op.create_index('idx_syllabus_study_system_source', 'syllabus_study_system', ['source_syllabus_id'])
    op.create_index('idx_syllabus_study_system_target', 'syllabus_study_system', ['target_syllabus_id']) 