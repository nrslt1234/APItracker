from typing import List

from pydantic import BaseModel, Field


class HabitBase(BaseModel):
    target_per_day : int = Field()
    name :str = Field()

class HabitCreate(HabitBase):
    pass


class HabitUpdateBase(BaseModel):
    target_per_day : int = Field()
    name :str = Field()
    is_activate: bool = Field()

class HabitUpdate(HabitUpdateBase):
    pass

