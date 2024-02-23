from typing import List

from sqlalchemy import CHAR, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Race(Base):
    __tablename__ = "races"

    id: Mapped[int] = mapped_column(primary_key=True)
    datasport_race_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(String(100))
    distance: Mapped[float | None] = mapped_column(nullable=True)

    participants: Mapped[List["Participant"]] = relationship(back_populates="race")

    def __init__(
        self, datasport_race_id: int, name: str, distance: float | None
    ) -> None:
        self.datasport_race_id = datasport_race_id
        self.name = name
        self.distance = distance

    def __repr__(self) -> str:
        return f"Race(id={self.id}, datasport_race_id={self.datasport_race_id}, name={self.name}, distance={self.distance})"  # noqa: E501

    def to_dict_without_participants(self) -> dict:
        return {
            "id": self.id,
            "datasport_race_id": self.datasport_race_id,
            "name": self.name,
            "distance": self.distance,
        }

    def to_dict(self) -> dict:
        return self.to_dict_without_participants() | {
            "participants": [participant.to_dict() for participant in self.participants]
        }


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    age: Mapped[int]
    gender: Mapped[str | None] = mapped_column(CHAR(1), nullable=True)
    finish_time: Mapped[int | None] = mapped_column(nullable=True)
    finished: Mapped[bool]
    started: Mapped[bool]
    disqualified: Mapped[bool]
    datasport_race_id: Mapped[int] = mapped_column(
        ForeignKey("races.datasport_race_id")
    )

    race: Mapped[Race] = relationship(back_populates="participants")

    def __init__(
        self,
        name: str,
        age: int,
        gender: str | None,
        finish_time: int | None,
        finished: bool,
        started: bool,
        disqualified: bool,
        datasport_race_id: int,
    ) -> None:
        self.name = name
        self.age = age
        self.gender = gender
        self.finish_time = finish_time
        self.finished = finished
        self.started = started
        self.disqualified = disqualified
        self.datasport_race_id = datasport_race_id

    def __repr__(self) -> str:
        return f"Participant(id={self.id}, name={self.name} age={self.age} gender={self.gender} finish_time={self.finish_time} finished={self.finished} started={self.started} datasport_race_id={self.datasport_race_id})"  # noqa: E501

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "finish_time": self.finish_time,
            "finished": self.finished,
            "started": self.started,
            "disqualified": self.disqualified,
            "datasport_race_id": self.datasport_race_id,
        }
