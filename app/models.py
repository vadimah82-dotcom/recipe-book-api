from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Recipe(Base):
    __tablename__ = "recipes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    cook_time: Mapped[int] = mapped_column(Integer, nullable=False)
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ingredients: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
