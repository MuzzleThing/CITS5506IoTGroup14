from app import db
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Date
import datetime

class Item(db.Model):
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(primary_key=True) # Generated automatically

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    date: Mapped[datetime.date] = mapped_column(nullable=False)
    expiry_date: Mapped[datetime.date] = mapped_column(nullable=False) 

class ExpiryTable(db.Model):
    __tablename__ = "expiry_table"

    id: Mapped[int] = mapped_column(primary_key=True) # Generated automatically

    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    expiry_days: Mapped[int] = mapped_column(nullable=False) # Unit is day(s)