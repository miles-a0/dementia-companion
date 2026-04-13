# Medication Reminder Workflows for n8n

This document explains how to create two n8n workflows that send John medication reminders at 08:00 and 20:00 every day.

---

## WORKFLOW 1: Morning Medication Reminder (08:00)

### Step-by-step Instructions

#### Step 1: Create a new workflow
1. Open your n8n instance
2. Click **Workflows** in the left sidebar
3. Click **Add workflow** (blue button, top right)
4. Name it "Morning Medication Reminder"

#### Step 2: Add Schedule Trigger (Node 1)
1. Click the **+** button on the canvas
2. Search for **Schedule Trigger** and select it
3. Click the **Cron Expression** tab
4. In "Cron Expression" enter: `0 0 8 * *`
5. This means: 08:00 every day
6. Rename to **Morning Reminder (8am)**
7. Click **Save**

#### Step 3: Add HTTP Request to get schedule (Node 2)
1. Hover over the trigger node and click **+**
2. Search for **HTTP Request** and select it
3. Configure:
   - **Method**: GET
   - **URL**: `http://companion-api:8001/api/medication/schedule?user_id=1`
4. Rename to **Get Medication Schedule**
5. Click **Save**

#### Step 4: Add IF node (Node 3)
1. Click **+** after the HTTP Request
2. Search for **IF** and select it
3. Configure condition:
   - **Value 1**: `{{$node["Get Medication Schedule"].json["medications"]}}`
   - **Operation**: is not empty
4. Rename to **Any Medications Due?**
5. Click **Save**

#### Step 5: Add HTTP Request for medication message (Node 4)
1. Click **+** on the **true** output of the IF node
2. Search for **HTTP Request** and select it
3. Configure:
   - **Method**: POST
   - **URL**: `http://companion-api:8001/api/messages/queue`
   - **Body Content Type**: JSON
   - **Body**:
     ```json
     {
       "user_id": 1,
       "content": "Good morning John, it's time to take your morning tablets. Your Donepezil is a small white tablet — take it with your breakfast.",
       "message_type": "medication"
     }
     ```
4. Rename to **Send Medication Reminder**
5. Click **Save**

#### Step 6: Add Wait node (Node 5)
1. Click **+** after the Send Medication Reminder node
2. Search for **Wait** and select it
3. Configure:
   - **Amount**: 15
   - **Unit**: minutes
4. Rename to **Wait 15 Minutes**
5. Click **Save**

#### Step 7: Add HTTP Request to check pending (Node 6)
1. Click **+** after the Wait node
2. Search for **HTTP Request** and select it
3. Configure:
   - **Method**: GET
   - **URL**: `http://companion-api:8001/api/medication/pending?user_id=1`
4. Rename to **Check Pending**
5. Click **Save**

#### Step 8: Add IF node for pending (Node 7)
1. Click **+** after the Check Pending node
2. Search for **IF** and select it
3. Configure:
   - **Value 1**: `{{$node["Check Pending"].json["pending"]}}`
   - **Operation**: is not empty
4. Rename to **Any Unconfirmed?**
5. Click **Save**

#### Step 9: Add HTTP Request for follow-up (Node 8)
1. Click **+** on the **true** output of the IF node
2. Search for **HTTP Request** and select it
3. Configure:
   - **Method**: POST
   - **URL**: `http://companion-api:8001/api/messages/queue`
   - **Body Content Type**: JSON
   - **Body**:
     ```json
     {
       "user_id": 1,
       "content": "John, just a gentle reminder — have you taken your tablets this morning? It's important not to forget.",
       "message_type": "medication"
     }
     ```
4. Rename to **Send Follow-up Reminder**
5. Click **Save**

#### Step 10: Save and activate
1. Click **Save** (grey button, top left)
2. Toggle **Active** to on (top right)

---

## WORKFLOW 2: Evening Medication Reminder (20:00)

### Step-by-step Instructions

Follow the same steps as Morning Medication Reminder, but with these changes:

#### Step 1: Schedule Trigger
- Cron Expression: `0 0 20 * *` (20:00 every day)
- Rename to **Evening Reminder (8pm)**

#### Step 2: Medication Message (Node 4)
- Change the **Body** to:
  ```json
  {
    "user_id": 1,
    "content": "Good evening John, it's time to take your evening tablets. Remember to take your Donepezil before bed.",
    "message_type": "medication"
  }
  ```

#### Step 3: Follow-up Message (Node 8)
- Change the **Body** to:
  ```json
  {
    "user_id": 1,
    "content": "John, don't forget — it's time to take your evening tablets before you go to sleep.",
    "message_type": "medication"
  }
  ```

---

## How to Customise

### Changing Medication Name and Time

To use a different medication or time:

1. **Change the time**: Edit the Cron Expression:
   - 07:00 = `0 0 7 * *`
   - 09:00 = `0 0 9 * *`
   - 21:00 = `0 0 21 * *`

2. **Change the medication**: Edit the message content in the HTTP Request nodes.

### Adding Additional Medication Times

To add a third medication time (e.g., 14:00):

1. Create a new workflow (copy one of the existing ones)
2. Change the Cron Expression to `0 0 14 * *`
3. Update the message content for afternoon

---

## How to Test

### Test the schedule endpoint:
```bash
curl http://companion-api:8001/api/medication/schedule?user_id=1
```

### Test manually triggering a reminder:
```bash
curl -X POST http://companion-api:8001/api/messages/queue \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"content":"Test medication reminder","message_type":"medication"}'
```

### Test the pending endpoint:
```bash
curl http://companion-api:8001/api/medication/pending?user_id=1
```

---

## British Summer Time (BST) Notes

n8n uses server time. If your n8n server is in a different timezone than John:

- **Winter (GMT)**: The cron expressions above work as written
- **Summer (BST, UTC+1)**: You may need to adjust by 1 hour:
  - For 08:00 BST use: `0 0 7 * *` (server in UTC)
  - Or ensure your server timezone is set to Europe/London

To check your n8n server timezone:
- Go to **Settings** > **Environment Variables**
- Look for `TZ` or check the system time

---

## JSON Import

### Morning Medication Reminder

```json
{
  "name": "Morning Medication Reminder",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 0 8 * *"
            }
          ]
        }
      },
      "id": "schedule-morning",
      "name": "Morning Reminder (8am)",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "http://companion-api:8001/api/medication/schedule?user_id=1"
      },
      "id": "get-schedule",
      "name": "Get Medication Schedule",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [500, 300]
    },
    {
      "parameters": {
        "conditions": {
          "options": {
            "leftValue": "",
            "rightValue": ""
          },
          "conditions": [
            {
              "leftValue": "={{$node[\"Get Medication Schedule\"].json[\"medications\"]}}",
              "rightValue": "[]",
              "operator": {
                "type": "array",
                "operator": "notEqual"
              }
            }
          ]
        }
      },
      "id": "if-due",
      "name": "Any Medications Due?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [750, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://companion-api:8001/api/messages/queue",
        "bodyParameters": {
          "parameters": [
            {"name": "user_id", "value": "1"},
            {"name": "content", "value": "Good morning John, it's time to take your morning tablets. Your Donepezil is a small white tablet — take it with your breakfast."},
            {"name": "message_type", "value": "medication"}
          ]
        }
      },
      "id": "send-reminder",
      "name": "Send Medication Reminder",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1000, 150]
    },
    {
      "parameters": {
        "amount": 15,
        "unit": "minutes"
      },
      "id": "wait",
      "name": "Wait 15 Minutes",
      "type": "n8n-nodes-base.wait",
      "typeVersion": 1,
      "position": [1000, 300]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "http://companion-api:8001/api/medication/pending?user_id=1"
      },
      "id": "check-pending",
      "name": "Check Pending",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1250, 300]
    },
    {
      "parameters": {
        "conditions": {
          "options": {
            "leftValue": "",
            "rightValue": ""
          },
          "conditions": [
            {
              "leftValue": "={{$node[\"Check Pending\"].json[\"pending\"]}}",
              "rightValue": "[]",
              "operator": {
                "type": "array",
                "operator": "notEqual"
              }
            }
          ]
        }
      },
      "id": "if-pending",
      "name": "Any Unconfirmed?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [1500, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://companion-api:8001/api/messages/queue",
        "bodyParameters": {
          "parameters": [
            {"name": "user_id", "value": "1"},
            {"name": "content", "value": "John, just a gentle reminder — have you taken your tablets this morning? It's important not to forget."},
            {"name": "message_type", "value": "medication"}
          ]
        }
      },
      "id": "send-followup",
      "name": "Send Follow-up Reminder",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1750, 150]
    }
  ],
  "connections": {
    "Morning Reminder (8am)": {
      "main": [[{"node": "Get Medication Schedule", "type": "main", "index": 0}]]
    },
    "Get Medication Schedule": {
      "main": [[{"node": "Any Medications Due?", "type": "main", "index": 0}]]
    },
    "Any Medications Due?": {
      "main": [
        [{"node": "Send Medication Reminder", "type": "main", "index": 0}],
        [{"node": "Wait 15 Minutes", "type": "main", "index": 0}]
      ]
    },
    "Send Medication Reminder": {
      "main": [[{"node": "Wait 15 Minutes", "type": "main", "index": 0}]]
    },
    "Wait 15 Minutes": {
      "main": [[{"node": "Check Pending", "type": "main", "index": 0}]]
    },
    "Check Pending": {
      "main": [[{"node": "Any Unconfirmed?", "type": "main", "index": 0}]]
    },
    "Any Unconfirmed?": {
      "main": [
        [{"node": "Send Follow-up Reminder", "type": "main", "index": 0}]
      ]
    }
  },
  "active": true,
  "settings": {},
  "tags": []
}
```

### Evening Medication Reminder

(Same JSON, but change Cron Expression to `0 0 20 * *` and update message content)

---

## Troubleshooting

### Reminders not sending
- Check that the companion-api is running: `docker-compose ps`
- Test the API directly: `curl http://companion-api:8001/api/messages/queue`

### Messages not appearing on John's device
- Check the messages table in Postgres
- Verify the polling is working on the frontend

### Time is wrong
- Check your n8n server timezone
- Adjust Cron Expression accordingly