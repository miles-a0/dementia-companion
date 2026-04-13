import os
import httpx
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def get_todays_appointments(user_id=1):
    vikunja_url = os.environ.get("VIKUNJA_URL", "http://vikunja:3456")
    api_key = os.environ.get("VIKUNJA_API_KEY")

    if not api_key:
        logger.warning("VIKUNJA_API_KEY not configured")
        return []

    today = datetime.utcnow()
    date_from = today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
    date_to = today.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat() + "Z"

    url = "{}/api/v1/tasks/all".format(vikunja_url)
    headers = {
        "Authorization": "Bearer {}".format(api_key)
    }
    params = {
        "due_date_from": date_from,
        "due_date_to": date_to,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            tasks = response.json()

        appointments = []
        for task in tasks:
            if task.get("done") is False:
                due_date = task.get("due_date")
                title = task.get("title", "")

                if due_date:
                    try:
                        due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                        time_str = due_dt.strftime("%-I:%M%p")
                        if time_str.startswith("0"):
                            time_str = time_str[1:]
                        appointment_str = "You have an appointment at {} - {}".format(time_str.lower(), title)
                    except Exception:
                        appointment_str = "You have an appointment - {}".format(title)
                else:
                    appointment_str = "You have a task - {}".format(title)

                appointments.append(appointment_str)

        return appointments

    except Exception as e:
        logger.warning("Error fetching Vikunja tasks: {}".format(e))
        return []