from __future__ import annotations

from sqlalchemy.orm import Mapped, relationship

from database import Base, intpk


class UserOrm(Base):
    __tablename__ = "users"
    id: Mapped[intpk]
    schedules: Mapped[list["MedicationScheduleOrm"]] = relationship("MedicationScheduleOrm", back_populates="user")
