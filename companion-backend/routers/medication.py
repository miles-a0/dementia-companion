import os
import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Query, Body
import psycopg2

logger = logging.getLogger(__name__)
router = APIRouter(tags=["medication"])


def get_db_connection():
    """Get synchronous database connection using psycopg2"""
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        logger.warning("DATABASE_URL not configured")
        return None
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        logger.warning(f"Database connection failed: {e}")
        return None


def parse_time_string(time_str):
    """Parse HH:MM time string to datetime object for today"""
    try:
        parts = time_str.split(":")
        hour = int(parts[0])
        minute = int(parts[1])
        now = datetime.now()
        dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if dt < now:
            dt += timedelta(days=1)
        return dt
    except Exception:
        return None


def is_due_now(times_of_day):
    """Check if current time is within 30 minutes of any scheduled time"""
    now = datetime.now()
    for time_str in times_of_day:
        scheduled = parse_time_string(time_str)
        if scheduled:
            diff = abs((now - scheduled).total_seconds())
            if diff <= 1800:
                return True
    return False


def get_next_due_time(times_of_day):
    """Get the next scheduled time in HH:MM format"""
    now = datetime.now()
    next_time = None
    for time_str in times_of_day:
        scheduled = parse_time_string(time_str)
        if scheduled and scheduled > now:
            if next_time is None or scheduled < next_time:
                next_time = scheduled
    if next_time:
        return next_time.strftime("%-I:%M%p")
    return None


@router.get("/medication/schedule")
async def get_medication_schedule(user_id: int = Query(default=1)):
    conn = get_db_connection()
    if not conn:
        return {"medications": []}
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, dose, times_of_day, instructions
            FROM medications
            WHERE user_id = %s AND active = TRUE
        """, (user_id,))
        rows = cursor.fetchall()
        
        medications = []
        for row in rows:
            med_id, name, dose, times_raw, instructions = row
            times_of_day = times_raw if times_raw else []
            
            due_now = is_due_now(times_of_day)
            next_due = get_next_due_time(times_of_day)
            
            medications.append({
                "id": med_id,
                "name": name,
                "dose": dose,
                "instructions": instructions or "",
                "due_now": due_now,
                "next_due": next_due
            })
        
        cursor.close()
        conn.close()
        return {"medications": medications}
    
    except Exception as e:
        logger.error(f"Error in get_medication_schedule: {e}")
        conn.close()
        return {"medications": []}


@router.post("/medication/confirm")
async def confirm_medication(
    user_id: int = Body(...),
    medication_id: int = Body(...)
):
    conn = get_db_connection()
    if not conn:
        return {"confirmed": False, "error": "Database not configured"}
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE medication_log 
            SET confirmed_at = NOW()
            WHERE user_id = %s AND medication_id = %s AND confirmed_at IS NULL
            ORDER BY scheduled_at DESC LIMIT 1
        """, (user_id, medication_id))
        
        if cursor.rowcount == 0:
            cursor.execute("""
                INSERT INTO medication_log (user_id, medication_id, scheduled_at, confirmed_at)
                VALUES (%s, %s, NOW(), NOW())
            """, (user_id, medication_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return {"confirmed": True}
    
    except Exception as e:
        logger.error(f"Error in confirm_medication: {e}")
        conn.close()
        return {"confirmed": False, "error": str(e)}


@router.get("/medication/pending")
async def get_pending_medications(user_id: int = Query(default=1)):
    conn = get_db_connection()
    if not conn:
        return {"pending": []}
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ml.medication_id, m.name, m.dose, ml.scheduled_at
            FROM medication_log ml
            JOIN medications m ON ml.medication_id = m.id
            WHERE ml.user_id = %s 
              AND ml.confirmed_at IS NULL
              AND ml.scheduled_at < NOW()
              AND ml.scheduled_at > NOW() - INTERVAL '2 hours'
            ORDER BY ml.scheduled_at ASC
        """, (user_id,))
        rows = cursor.fetchall()
        
        pending = []
        for row in rows:
            med_id, name, dose, scheduled_at = row
            pending.append({
                "medication_id": med_id,
                "name": name,
                "dose": dose,
                "scheduled_at": scheduled_at.isoformat() if scheduled_at else None
            })
        
        cursor.close()
        conn.close()
        return {"pending": pending}
    
    except Exception as e:
        logger.error(f"Error in get_pending_medications: {e}")
        conn.close()
        return {"pending": []}


@router.post("/medication")
async def add_medication(
    user_id: int = Body(...),
    name: str = Body(...),
    dose: str = Body(...),
    times_of_day: list = Body(...),
    instructions: str = Body(default="")
):
    conn = get_db_connection()
    if not conn:
        return {"created": False, "error": "Database not configured"}
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO medications (user_id, name, dose, times_of_day, instructions, active)
            VALUES (%s, %s, %s, %s, %s, TRUE)
            RETURNING id
        """, (user_id, name, dose, times_of_day, instructions))
        
        new_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return {"created": True, "medication_id": new_id}
    
    except Exception as e:
        logger.error(f"Error in add_medication: {e}")
        conn.close()
        return {"created": False, "error": str(e)}