# Morning Routine Workflow for n8n

This document explains how to create an n8n workflow that sends John his morning greeting at 7:30am every day.

---

## Step-by-step Instructions

### Step 1: Access n8n
1. Open your browser and go to your n8n instance (e.g., http://your-vps-ip:5678)
2. Log in with your credentials

### Step 2: Create a new workflow
1. Click the **"Workflows"** menu in the left sidebar
2. Click the **"Add workflow"** button (blue button, top right)
3. A new blank canvas will appear

### Step 3: Add the Schedule Trigger (Node 1)
1. Click the **"+"** button on the canvas to add a node
2. Search for "Schedule Trigger" and select it
3. Click the **"Cron Expression"** tab
4. In the "Cron Expression" field, enter: `0 30 7 * *`
5. This means: "At 07:30 every day"
6. Rename the node to "7:30am Daily" (click the node name at the top)
7. Click **"Save"** on the node

### Step 4: Add HTTP Request (Node 2)
1. Hover over the "7:30am Daily" node and click the **"+"** button that appears on the right
2. Search for "HTTP Request" and select it
3. Configure these settings:
   - **Method**: POST
   - **URL**: `http://companion-api:8001/api/routines/morning-greeting`
   - **Body Content Type**: JSON
   - **JSON**: `{"user_id": 1}`
   - **Timeout**: 30000 (ms)
4. Rename the node to "Send Morning Greeting"
5. Click **"Save"**

### Step 5: Add IF node (Node 3)
1. Hover over the "Send Morning Greeting" node and click the **"+"** button
2. Search for "IF" and select it
3. Configure the condition:
   - **Value 1**: `{{$node["Send Morning Greeting"].json["queued"]}}`
   - **Operation**: equals
   - **Value 2**: `true`
4. Rename the node to "Did it work?"
5. Click **"Save"**

### Step 6: Add Set node for True branch (Node 4)
1. Click the **"+"** on the right side of the "Did it work?" node under the **"true"** output
2. Search for "Set" and select it
3. In the "Properties" section, add:
   - **Name**: result
   - **Value**: `Morning greeting sent successfully`
4. Rename the node to "Log Success"
5. Click **"Save"**

### Step 7: Add Set node for False branch (Node 5)
1. Click the **"+"** on the right side of the "Did it work?" node under the **"false"** output
2. Search for "Set" and select it
3. In the "Properties" section, add:
   - **Name**: result
   - **Value**: `Morning greeting failed — check companion-api logs`
4. Rename the node to "Log Failure"
5. Click **"Save"**

### Step 8: Save and activate the workflow
1. Click the **"Save"** button (top left, grey button)
2. Give the workflow a name like "John's Morning Greeting"
3. Toggle the **"Active"** switch (top right) to turn it on
4. You should see a green "Active" indicator

---

## How to Test Manually

### Option 1: Execute Workflow button
1. Click the **"Execute Workflow"** button (play icon, top right of canvas)
2. Watch the execution progress - nodes will light up green as they complete
3. Check the output of each node by clicking on it

### Option 2: Test with curl
On your VPS, run:
```bash
curl -X POST http://companion-api:8001/api/routines/morning-greeting \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

Expected response:
```json
{"queued": true, "preview": "Good morning John! It's Friday, 10th April..."}
```

---

## How to View Execution Logs

1. In n8n, click the **"Executions"** tab (left sidebar, looks like a clock icon)
2. You will see a list of past workflow runs
3. Click on any execution to see:
   - Which nodes ran
   - What data passed between nodes
   - Any errors that occurred

---

## How to Check the Message in Postgres

Connect to your Postgres database and run:
```sql
SELECT id, content, message_type, created_at 
FROM messages 
WHERE user_id = 1 
ORDER BY created_at DESC 
LIMIT 5;
```

You should see a new row with:
- `message_type` = 'greeting'
- `content` = the AI-generated morning greeting

---

## JSON Import

You can import this workflow directly into n8n instead of building it manually:

1. In n8n, click the menu (three lines, top left)
2. Select **"Import from File"**
3. Upload the JSON file below

Or use the API endpoint to import:
```
POST /api/v1/workflows/import
```

---

## Workflow JSON Export

```json
{
  "name": "John's Morning Greeting",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 30 7 * *"
            }
          ]
        }
      },
      "id": "schedule-trigger",
      "name": "7:30am Daily",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://companion-api:8001/api/routines/morning-greeting",
        "bodyParameters": {
          "parameters": [
            {
              "name": "user_id",
              "value": "1"
            }
          ]
        },
        "timeout": 30000
      },
      "id": "http-request",
      "name": "Send Morning Greeting",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [500, 300]
    },
    {
      "parameters": {
        "conditions": {
          "options": {
            "caseSensitive": true,
            "leftValue": "",
            "rightValue": ""
          },
          "conditions": [
            {
              "leftValue": "={{$node[\"Send Morning Greeting\"].json[\"queued\"]}}",
              "rightValue": "true",
              "operator": {
                "type": "equals",
                "operator": "="
              }
            }
          ],
          "combinator": "and"
        },
        "fallbackOutput": "none"
      },
      "id": "if",
      "name": "Did it work?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [750, 300]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "result",
              "name": "result",
              "value": "Morning greeting sent successfully",
              "type": "string"
            }
          ]
        },
        "includeOtherFields": false
      },
      "id": "set-true",
      "name": "Log Success",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3,
      "position": [1000, 150]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "result",
              "name": "result",
              "value": "Morning greeting failed — check companion-api logs",
              "type": "string"
            }
          ]
        },
        "includeOtherFields": false
      },
      "id": "set-false",
      "name": "Log Failure",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3,
      "position": [1000, 450]
    }
  ],
  "connections": {
    "7:30am Daily": {
      "main": [
        [
          {
            "node": "Send Morning Greeting",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Send Morning Greeting": {
      "main": [
        [
          {
            "node": "Did it work?",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Did it work?": {
      "main": [
        [
          {
            "node": "Log Success",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Log Failure",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "active": true,
  "settings": {},
  "tags": []
}
```

---

## Troubleshooting

### Workflow not triggering
- Make sure the "Active" toggle is on (green)
- Check the Schedule Trigger node shows "Next run: [date]"

### HTTP request failing
- Verify the container names are correct on your Docker network
- Check companion-api is running: `docker-compose ps`
- Test the API directly: `curl http://companion-api:8001/health`

### Message not appearing
- Check Postgres is running and DATABASE_URL is set
- Look at companion-api logs: `docker-compose logs companion-api`
- Query messages table directly to see if insert happened