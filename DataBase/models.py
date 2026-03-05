from datetime import date, datetime
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, create_engine, select, insert, delete, update, DateTime, func, Table, Column, Date, \
    UniqueConstraint
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


from uuid import UUID
import uuid
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class Base(DeclarativeBase):
    pass


class Habit(Base):
    __tablename__ = "habit"
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name: Mapped[str] = mapped_column()
    target_per_day: Mapped[int] = mapped_column(nullable = False, default = 1)
    is_activate: Mapped[bool] = mapped_column(default = True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    habit_log: Mapped[List["HabitLog"]] = relationship("HabitLog", back_populates="habit",  cascade="all, delete")

class HabitLog(Base):
    __tablename__ = "habit_log"
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    # uuid.uuid4 - автоматически генерирует новый uuid код
    habit_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True),ForeignKey("habit.id", ondelete="CASCADE"),nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    count: Mapped[int] = mapped_column(nullable=False, default = 1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    habit: Mapped["Habit"] = relationship("Habit", back_populates="habit_log")

    __table_args__ = (
        UniqueConstraint("habit_id", "date", name="uq_habit_date"),
    )