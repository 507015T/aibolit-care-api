from typing import Optional
from sqlalchemy import Column, Integer, String, SmallInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from datetime import date


class MedicationSchedule(Base):
    __tablename__ = "schedules"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    medication_name: Mapped[str] = mapped_column(
        String(255), index=True, nullable=False
    )
    frequency: Mapped[int] = mapped_column(SmallInteger, index=True, nullable=False)
    duration_days: Mapped[Optional[int]] = mapped_column(SmallInteger)
    start_date: Mapped[date] = mapped_column(default=date.today(), nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(nullable=True, default=None)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
