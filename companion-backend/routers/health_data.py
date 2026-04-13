import os
import logging
from datetime import datetime
from fastapi import APIRouter, Body

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


def get_db_connection():
    """Get synchronous database connection using psycopg2"""
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        logger.warning("DATABASE_URL not configured")
        return None
    try:
        import psycopg2
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        logger.warning(f"Database connection failed: {e}")
        return None


@router.post("/health/biometrics")
async def receive_biometrics(
    user_id: int = Body(default=1),
    heart_rate: int = Body(...),
    steps_last_hour: int = Body(default=0),
    timestamp: str = Body(default=None)
):
    try:
        import psycopg2
        
        conn = get_db_connection()
        if not conn:
            return {"received": True, "error": "Database not configured"}

        try:
            cursor = conn.cursor()
            
            if timestamp:
                cursor.execute("""
                    INSERT INTO biometrics (user_id, heart_rate, steps_last_hour, recorded_at)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (user_id, heart_rate, steps_last_hour, timestamp))
            else:
                cursor.execute("""
                    INSERT INTO biometrics (user_id, heart_rate, steps_last_hour, recorded_at)
                    VALUES (%s, %s, %s, NOW())
                    RETURNING id
                """, (user_id, heart_rate, steps_last_hour))
            
            inserted_id = cursor.fetchone()[0]
            conn.commit()

            cursor.execute("""
                SELECT heart_rate FROM biometrics
                WHERE user_id = %s ORDER BY recorded_at DESC LIMIT 3
            """, (user_id,))
            recent_readings = cursor.fetchall()
            
            hr_values = [r[0] for r in recent_readings]
            
            sustained_high_hr = len(hr_values) >= 3 and all(hr > 88 for hr in hr_values)
            low_activity = steps_last_hour < 20
            current_hour = datetime.now().hour
            active_hours = 7 <= current_hour <= 22
            
            should_trigger = sustained_high_hr and low_activity and active_hours

            if should_trigger:
                cursor.execute("""
                    UPDATE biometrics SET intervention_triggered = TRUE WHERE id = %s
                """, (inserted_id,))
                conn.commit()
                
                try:
                    import threading
                    def trigger_intervention():
                        try:
                            import requests
                            requests.post(
                                "http://localhost:8001/api/interventions/trigger",
                                json={"user_id": user_id, "trigger_type": "biometric"},
                                timeout=5
                            )
                        except Exception:
                            pass
                    threading.Thread(target=trigger_intervention).start()
                except Exception as e:
                    logger.warning(f"Could not trigger intervention: {e}")

                cursor.close()
                conn.close()
                return {
                    "received": True,
                    "intervention_triggered": True,
                    "reason": "sustained_high_hr"
                }
            else:
                cursor.close()
                conn.close()
                return {
                    "received": True,
                    "intervention_triggered": False,
                    "readings": hr_values,
                    "threshold_met": False
                }

        except Exception as e:
            logger.error(f"Error in receive_biometrics: {e}")
            if conn:
                conn.close()
            return {"received": True, "error": str(e)}

    except Exception as e:
        logger.error(f"Unexpected error in receive_biometrics: {e}")
        return {"received": False, "error": str(e)}