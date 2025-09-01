from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column, Relationship, DeclarativeBase
from sqlalchemy.dialects.postgresql import TEXT, VARCHAR, INTEGER, FLOAT, DATE, TIMESTAMP
from typing import List
from typing import Optional

class Base(DeclarativeBase):
    type_annotation_map={
        int: INTEGER,
        str: VARCHAR,
        float: FLOAT,
        Date: DATE,
        DateTime: TIMESTAMP
    }

class Sleep(Base):
    __tablename__ = 'fact_sleep'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cycle_id: Mapped[int]
    v1_id: Mapped[int]
    user_id: Mapped[int]
    created_at: Mapped[DateTime]
    updated_at: Mapped[DateTime]
    start: Mapped[DateTime]
    end: Mapped[DateTime]
    timezone_offset: Mapped[str]
    nap: Mapped[bool]
    score_state: Mapped[str]
    score_stage_summary_total_in_bed_time_milli: Mapped[int]
    score_stage_summary_total_awake_time_milli: Mapped[int]
    score_stage_summary_total_no_data_time_milli: Mapped[int]
    score_stage_summary_total_light_sleep_time_milli: Mapped[int]
    score_stage_summary_total_slow_wave_sleep_time_milli: Mapped[int]
    score_stage_summary_total_rem_sleep_time_milli: Mapped[int]
    score_stage_summary_sleep_cycle_count: Mapped[int]
    score_stage_summary_disturbance_count: Mapped[int]
    score_sleep_needed_baseline_milli: Mapped[int]
    score_sleep_needed_need_from_sleep_debt_milli: Mapped[int]
    score_sleep_needed_need_from_recent_strain_milli: Mapped[int]
    score_sleep_needed_need_from_recent_nap_milli: Mapped[int]
    score_respiratory_rate: Mapped[float]
    score_sleep_performance_percentage: Mapped[float]
    score_sleep_consistency_percentage: Mapped[float]
    score_sleep_efficiency_percentage: Mapped[float]
    
    

# class Recovery(Base):
#     __tablename__ = 'fact_recovery'

 

# class Workout(Base):
#     __tablename__ = 'fact_workout'

