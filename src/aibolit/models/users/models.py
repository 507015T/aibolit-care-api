from __future__ import annotations
from typing import List

from sqlalchemy.orm import Mapped, relationship

from aibolit.core.database import Base, intpk


class UserOrm(Base):
    __tablename__ = "users"
    id: Mapped[intpk]
    schedules: Mapped[List["MedicationScheduleOrm"]] = relationship("MedicationScheduleOrm", back_populates="user")
