from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String(300), index=True)
    elevators = relationship("Elevator", back_populates="building")

class Elevator(Base):
    __tablename__ = "elevators"

    id: Mapped[int] = mapped_column(primary_key=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"))
    entrance: Mapped[int] = mapped_column()
    serial_number: Mapped[str] = mapped_column(String(50), unique=True)
    model: Mapped[str | None] = mapped_column(String(100))
    building = relationship("Building", back_populates="elevators")
