from __future__ import annotations

from sqlalchemy.orm import Mapped, relationship

from database import Base, intpk


class User(Base):
    __tablename__ = "users"
    policy_number: Mapped[intpk]
    schedules: Mapped[list[MedicationSchedule]] = relationship("MedicationSchedule", back_populates="user")
