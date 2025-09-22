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
    __tablename__ = 'fact_activity_sleep'
    sleep_id: Mapped[str] = mapped_column(VARCHAR, primary_key=True)
    cycle_id: Mapped[int] = mapped_column(Integer, ForeignKey('fact_cycle.cycle_id'))
    v1_id: Mapped[int]
    user_id: Mapped[int]
    created_at: Mapped[DateTime]
    updated_at: Mapped[DateTime]
    start: Mapped[DateTime]
    end: Mapped[DateTime]
    timezone_offset: Mapped[int]
    nap: Mapped[bool]
    state: Mapped[str]
    total_in_bed_time_milli: Mapped[int]
    total_awake_time_milli: Mapped[int]
    total_no_data_time_milli: Mapped[int]
    total_light_sleep_time_milli: Mapped[int]
    total_slow_wave_sleep_time_milli: Mapped[int]
    total_rem_sleep_time_milli: Mapped[int]
    sleep_cycle_count: Mapped[int]
    disturbance_count: Mapped[int]
    sleep_needed_baseline_milli: Mapped[int]
    sleep_needed_need_from_sleep_debt_milli: Mapped[int]
    sleep_needed_need_from_recent_strain_milli: Mapped[int]
    sleep_needed_need_from_recent_nap_milli: Mapped[int]
    respiratory_rate: Mapped[float]
    sleep_performance_percentage: Mapped[float]
    sleep_consistency_percentage: Mapped[float]
    sleep_efficiency_percentage: Mapped[float]
    
    

class Recovery(Base):
    __tablename__ = 'fact_recovery'
    cycle_id: Mapped[int] = mapped_column(Integer, ForeignKey('fact_cycle.cycle_id'))
    sleep_id: Mapped[str] = mapped_column(VARCHAR, primary_key=True)
    user_id: Mapped[int]
    created_at: Mapped[DateTime]
    updated_at: Mapped[DateTime]
    state: Mapped[str]
    score_state: Mapped[str]
    user_calibrating: Mapped[bool]
    recovery_score: Mapped[int]
    resting_heart_rate: Mapped[int]
    hrv_rmssd_milli: Mapped[float]
    spo2_percentage: Mapped[float]
    skin_temp_celsius: Mapped[float]

 
class Workout(Base):
    __tablename__ = 'fact_workout'
    workout_id: Mapped[str] = mapped_column(VARCHAR, primary_key=True)
    v1_id: Mapped[int]
    user_id: Mapped[int]
    created_at: Mapped[DateTime]
    updated_at: Mapped[DateTime]
    start: Mapped[DateTime]
    end: Mapped[DateTime]
    timezone_offset: Mapped[DateTime]
    sport_name: Mapped[str]
    score_state: Mapped[str]
    sport_id: Mapped[int]
    strain: Mapped[float]
    average_hear_rate: Mapped[int]
    max_heart_rate: Mapped[int]
    kilojoule: Mapped[float]
    percent_recorded: Mapped[float]
    altitude_gain_meter: Mapped[float]
    altitude_change_meter: Mapped[float]
    zone_zero_milli: Mapped[int]
    zone_one_milli: Mapped[int]
    zone_two_milli: Mapped[int]
    zone_three_milli: Mapped[int]
    zone_four_milli: Mapped[int]
    zone_five_milli: Mapped[int]


class Cycles(Base):
    __tablename__ = 'fact_cycle'
    cycle_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int]
    user_id: Mapped[int]
    created_at: Mapped[DateTime]
    updated_at: Mapped[DateTime]
    start: Mapped[DateTime]
    end: Mapped[DateTime]
    timezone_offset: Mapped[int]
    state: Mapped[str]
    strain: Mapped[float]
    kilojoule: Mapped[float]
    average_heart_rate: Mapped[int]
    max_heart_rate: Mapped[int]


    sleep_id: Mapped[Optional[str]] = mapped_column(VARCHAR, ForeignKey('fact_activity_sleep.sleep_id'))
    recovery_id: Mapped[Optional[str]] = mapped_column(VARCHAR, ForeignKey('fact_recovery.sleep_id'))
    
    sleep: Mapped[Optional[Sleep]] = relationship("Sleep", backref="cycles")
    recovery: Mapped[Optional[Recovery]] = relationship("Recovery", backref="cycles")
