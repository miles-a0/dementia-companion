import os
import logging
import asyncio
from datetime import datetime
from fastapi import APIRouter, Body
from services.weather import get_weather_description
from services.vikunja import get_todays_appointments
from services.qdrant_client import search_memories
from services.openrouter import get_ai_response
from routers.messages import queue_message, get_db_connection

logger = logging.getLogger(__name__)
router = APIRouter(tags=["routines"])


def get_ordinal_suffix(day):
    if 11 <= day <= 13:
        return "th"
    last_digit = day % 10
    if last_digit == 1:
        return "st"
    elif last_digit == 2:
        return "nd"
    elif last_digit == 3:
        return "rd"
    return "th"


def format_friendly_date():
    now = datetime.utcnow()
    day = now.day
    suffix = get_ordinal_suffix(day)
    month_name = now.strftime("%B")
    year = now.year
    weekday = now.strftime("%A")
    return "{}, {}{} {}".format(weekday, day, suffix, month_name, year)


@router.post("/routines/morning-greeting")
async def trigger_morning_greeting(user_id: int = Body(default=1)):
    try:
        weather, appointments, memories = await asyncio.gather(
            get_weather_description(),
            get_todays_appointments(user_id),
            search_memories("morning routine breakfast", ["routines", "preferences"], limit=2)
        )

        date_str = format_friendly_date()

        if appointments:
            appointments_str = ", ".join(appointments)
        else:
            appointments_str = "No appointments today"

        memory_texts = []
        for m in memories:
            if m.get("text"):
                memory_texts.append(m.get("text"))
        memories_str = ", ".join(memory_texts) if memory_texts else "a nice cup of tea"

        system_prompt = """You are John's warm and friendly companion. John is 80 years old and lives at home in Barrowford, Lancashire. He has some memory difficulties. Speak to him warmly, simply, and in short sentences. Today you are giving him his morning greeting."""

        user_message = """Give John his morning greeting. Here is the information to include naturally:
- Today is {}
- He is at home in Barrowford, Lancashire
- Weather today: {}
- Appointments today: {}
- Things John likes in the morning: {}
End with one gentle encouraging suggestion like suggesting a cup of tea or a stretch.
Keep the whole greeting under 5 sentences.""".format(date_str, weather, appointments_str, memories_str)

        ai_response = await get_ai_response(system_prompt, user_message)

        await queue_message(user_id, ai_response, "greeting")

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO intervention_log (user_id, triggered_at, trigger_type, message_sent)
                    VALUES (%s, NOW(), %s, %s)
                """, (user_id, "morning_greeting", ai_response))
                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                logger.warning("Could not log intervention: {}".format(e))

        return {"queued": True, "preview": ai_response}

    except Exception as e:
        logger.error("Error in morning_greeting: {}".format(e))
        return {"queued": False, "error": str(e)}