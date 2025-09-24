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
    total_in_bed_time_milli: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_awake_time_milli: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_no_data_time_milli: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_light_sleep_time_milli: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_slow_wave_sleep_time_milli: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_rem_sleep_time_milli: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sleep_cycle_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    disturbance_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sleep_needed_baseline_milli: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sleep_needed_need_from_sleep_debt_milli: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sleep_needed_need_from_recent_strain_milli: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sleep_needed_need_from_recent_nap_milli: Mapped[int | None] = mapped_column(Integer, nullable=True)
    respiratory_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    sleep_performance_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    sleep_consistency_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    sleep_efficiency_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    

class Recovery(Base):
    __tablename__ = 'fact_recovery'
    cycle_id: Mapped[int] = mapped_column(Integer, ForeignKey('fact_cycle.cycle_id'))
    sleep_id: Mapped[str] = mapped_column(VARCHAR, primary_key=True)
    user_id: Mapped[int]
    created_at: Mapped[DateTime]
    updated_at: Mapped[DateTime]
    state: Mapped[str]
    user_calibrating: Mapped[bool]
    recovery_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resting_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hrv_rmssd_milli: Mapped[float | None] = mapped_column(Float, nullable=True)
    spo2_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    skin_temp_celsius: Mapped[float | None] = mapped_column(Float, nullable=True)

 
class Workout(Base):
    __tablename__ = 'fact_workout'
    workout_id: Mapped[str] = mapped_column(VARCHAR, primary_key=True)
    v1_id: Mapped[int]
    user_id: Mapped[int]
    created_at: Mapped[DateTime]
    updated_at: Mapped[DateTime]
    start: Mapped[DateTime]
    end: Mapped[DateTime]
    timezone_offset: Mapped[int]
    sport_name: Mapped[str]
    state: Mapped[str]
    sport_id: Mapped[int]
    strain: Mapped[float | None] = mapped_column(Float, nullable=True)
    average_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    kilojoule: Mapped[float | None] = mapped_column(Float, nullable=True)
    percent_recorded: Mapped[float | None] = mapped_column(Float, nullable=True)
    distance_meter: Mapped[float | None] = mapped_column(Float, nullable=True)
    altitude_gain_meter: Mapped[float | None] = mapped_column(Float, nullable=True)
    altitude_change_meter: Mapped[float | None] = mapped_column(Float, nullable=True)
    zone_zero_milli: Mapped[int | None] = mapped_column(Integer, nullable=True)
    zone_one_milli: Mapped[int | None] = mapped_column(Integer, nullable=True)
    zone_two_milli: Mapped[int | None] = mapped_column(Integer, nullable=True)
    zone_three_milli: Mapped[int | None] = mapped_column(Integer, nullable=True)
    zone_four_milli: Mapped[int | None] = mapped_column(Integer, nullable=True)
    zone_five_milli: Mapped[int | None] = mapped_column(Integer, nullable=True)


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
    strain: Mapped[float | None] = mapped_column(Float, nullable=True)
    kilojoule: Mapped[float | None] = mapped_column(Float, nullable=True)
    average_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)


    sleep_id: Mapped[Optional[str]] = mapped_column(VARCHAR, ForeignKey('fact_activity_sleep.sleep_id'))
    recovery_id: Mapped[Optional[str]] = mapped_column(VARCHAR, ForeignKey('fact_recovery.sleep_id'))
    
    sleep: Mapped[Optional[Sleep]] = relationship("Sleep", backref="cycles")
    recovery: Mapped[Optional[Recovery]] = relationship("Recovery", backref="cycles")
