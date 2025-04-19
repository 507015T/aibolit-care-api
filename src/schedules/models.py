from typing import Optional
from sqlalchemy import String, SmallInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base, intpk
from datetime import date


class MedicationSchedule(Base):
    __tablename__ = "schedules"
    id: Mapped[intpk]
    medication_name: Mapped[str] = mapped_column(
        String(255), index=True, nullable=False
    )
    frequency: Mapped[int] = mapped_column(SmallInteger, index=True, nullable=False)
    duration_days: Mapped[Optional[int]] = mapped_column(SmallInteger)
    start_date: Mapped[date] = mapped_column(default=date.today(), nullable=False)
    end_date: Mapped[Optional[date]]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.policy_number", ondelete="CASCADE"), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="schedules")



