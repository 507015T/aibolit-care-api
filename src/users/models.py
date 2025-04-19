from sqlalchemy.orm import relationship, Mapped
from database import Base, intpk


class User(Base):
    __tablename__ = "users"
    policy_number: Mapped[intpk]
    schedules: Mapped[list["MedicationSchedule"]] = relationship(
        "MedicationSchedule", back_populates="user"
    )
