import os
import random

import smtplib


from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.sessions import SessionMiddleware

from DataBase.models import Habit, HabitLog
from schemas import HabitCreate, HabitUpdate

load_dotenv()

import uvicorn
from fastapi import FastAPI, Query, HTTPException
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, insert, or_, and_, update, delete, func, desc
from sqlalchemy.orm import joinedload, selectinload
from datetime import date

from DataBase.session import SessionLocal


app = FastAPI(title="Simple FastAPI App")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(SessionMiddleware, secret_key="super-secret-key")









@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/habits")
def homes(data: HabitCreate):
    with SessionLocal() as session:
        stmt = select(Habit).where(Habit.name == data.name)
        habit = session.execute(stmt).scalar_one_or_none()

        if habit:
            return {"error": "Такая привычка уже есть"}

        stmt = insert(Habit).values(name = data.name, target_per_day = data.target_per_day)
        session.execute(stmt)
        session.commit()
    return {"status" : "Добавлена новая привычка"}

@app.get("/habits")
def homes():
    with SessionLocal() as session:
        stmt = select(Habit).where(Habit.is_activate == True)
        all_active_habits = session.execute(stmt).scalars().all()

    return all_active_habits


@app.get("/habits/{id}")
def homes(id: int):
    with SessionLocal() as session:
        stmt = select(Habit).where(Habit.id == id)
        one_habit = session.execute(stmt).scalar_one_or_none()

        if one_habit is None:
            raise HTTPException(
                status_code=404,
                detail="Такой привычки не существует в базе данных"
            )
    return one_habit

@app.patch("/habits/{id}")
def homes(id: int, data: HabitUpdate):
    with SessionLocal() as session:
        stmt = update(Habit).where(Habit.id == id).values(name = data.name, is_activate = data.is_activate, target_per_day = data.target_per_day)
        one_change_habit = session.execute(stmt)
        session.commit()

        if one_change_habit.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Такой привычки не существует в базе данных"
            )

    return {"status": "Привычка обновлена"}

@app.delete("/habits/{id}")
def homes(id: int):
    with SessionLocal() as session:
        stmt = delete(Habit).where(Habit.id == id)
        one_delete_habit = session.execute(stmt)
        session.commit()

        if one_delete_habit.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Такой привычки не существует в базе данных"
            )


    return {"status": "Привычка удалена!"}



today = date.today()
@app.post("/habits/{habit_id}/logs")
def homes(habit_id: int):
    with SessionLocal() as session:
        stmt = select(HabitLog).where(and_(HabitLog.habit_id == habit_id, HabitLog.date == today))
        plus_one_target_today = session.execute(stmt).scalar_one_or_none()


        if plus_one_target_today:
            stmt = update(HabitLog).where(and_(HabitLog.habit_id == habit_id, HabitLog.date == today)).values(count = HabitLog.count + 1)
            session.execute(stmt)


        else:
            stmt = insert(HabitLog).values(habit_id = habit_id, count = 1, date = today)
            session.execute(stmt)
            session.commit()
            return {"message" : "Ты сегодня впервые начал заниматься этой привычкой. Поздравляю!"}
        session.commit()

    return {"message" : "Единичка цели сегодня выполнена!"}


@app.get("/habits/{habit_id}/logs/date_to/date_from")
def homes(habit_id: int, date_from: date = Query(description="от этой даты"), date_to: date = Query(description="до этой даты включительно")):

    with SessionLocal() as session:

        stmt = select(HabitLog).where((and_(HabitLog.habit_id == habit_id, HabitLog.date >= date_from, HabitLog.date <= date_to))).order_by(desc(HabitLog.date))
        choose_habits = session.execute(stmt).scalars().all()
        # Нужно преобразовать объекты choose_habits в словари
        history = [{"date": log.date.isoformat(), "count": log.count} for log in choose_habits]

        return {"habit_id": habit_id, "history": history}

@app.delete("/logs/{id}")
def homes(id : int):
    with SessionLocal() as session:
        try:
            stmt = delete(HabitLog).where(HabitLog.id == id)
            session.execute(stmt)
            session.commit()

        except SQLAlchemyError:
            return {"message" : "Не удалось удалить отметку"}

    return {"message" : "Отметка была успешна удалена"}



if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # название файла (main.py) и объекта app
        host="0.0.0.0",
        port=8000,
        reload=True
    )
