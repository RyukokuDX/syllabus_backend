"""講義時間と講義回数のテーブルを追加

Revision ID: 20240529_add_lecture_tables
Revises: 20240529_add_syllabus_study_system
Create Date: 2024-05-29 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240529_add_lecture_tables'
down_revision = '20240529_add_syllabus_study_system'
branch_labels = None
depends_on = None

def upgrade():
    # 講義時間テーブル
    op.create_table(
        'lecture_time',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('syllabus_id', sa.Integer(), nullable=False),
        sa.Column('day_of_week', sa.Text(), nullable=False),
        sa.Column('period', sa.SmallInteger(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['syllabus_id'], ['syllabus_master.syllabus_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_lecture_time_day_period', 'lecture_time', ['day_of_week', 'period'])
    op.create_index('idx_lecture_time_syllabus', 'lecture_time', ['syllabus_id'])

    # 講義回数テーブル
    op.create_table(
        'lecture_session',
        sa.Column('lecture_session_id', sa.Integer(), nullable=False),
        sa.Column('syllabus_id', sa.Integer(), nullable=False),
        sa.Column('session_number', sa.Integer(), nullable=False),
        sa.Column('contents', sa.Text(), nullable=True),
        sa.Column('other_info', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['syllabus_id'], ['syllabus_master.syllabus_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('lecture_session_id')
    )
    op.create_index('idx_lecture_session_syllabus', 'lecture_session', ['syllabus_id'])
    op.create_index('idx_lecture_session_number', 'lecture_session', ['session_number'])

    # 講義回数担当者テーブル
    op.create_table(
        'lecture_session_instructor',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lecture_session_id', sa.Integer(), nullable=False),
        sa.Column('instructor_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['instructor_id'], ['instructor.instructor_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['lecture_session_id'], ['lecture_session.lecture_session_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_lecture_session_instructor_session', 'lecture_session_instructor', ['lecture_session_id'])
    op.create_index('idx_lecture_session_instructor_instructor', 'lecture_session_instructor', ['instructor_id'])

def downgrade():
    op.drop_table('lecture_session_instructor')
    op.drop_table('lecture_session')
    op.drop_table('lecture_time') 