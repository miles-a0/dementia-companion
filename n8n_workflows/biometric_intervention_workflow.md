# Biometric Intervention Workflow for n8n

This document explains how to create an n8n workflow that receives biometric data from John's iOS Shortcut and triggers an intervention if certain thresholds are met.

---

## Step-by-step Instructions

### Step 1: Create a new workflow
1. Open your n8n instance
2. Click **Workflows** in the left sidebar
3. Click **Add workflow** (blue button, top right)
4. You will see a blank canvas

### Step 2: Add the Webhook (Node 1)
1. Click the **+** button on the canvas
2. Search for **Webhook** and select it
3. Configure these settings:
   - **HTTP Method**: POST
   - **Path**: `health-check`
   - **Response Mode**: Respond immediately
   - **Response Body**: `{"received": true}`
4. Rename the node to **Receive Health Data**
5. Click **Save**

> **Important:** Note the full webhook URL. It will look like:
> `https://your-n8n-domain.com/webhook/health-check`
> You will use this URL in your iOS Shortcut instead of the direct API URL.

### Step 3: Add the IF node (Node 2)
1. Hover over the **Receive Health Data** node and click the **+** button
2. Search for **IF** and select it
3. Configure the condition:
   - **Value 1**: `{{$node["Receive Health Data"].json["heart_rate"]}}`
   - **Operation**: greater than
   - **Value 2**: `88`
4. Click **Add Condition**
   - **Value 1**: `{{$node["Receive Health Data"].json["steps_last_hour"]}}`
   - **Operation**: less than
   - **Value 2**: `20`
5. Make sure the dropdown says **AND** between the two conditions
6. Rename the node to **High HR + Low Activity?**
7. Click **Save**

### Step 4: Add HTTP Request for True branch (Node 3)
1. Click the **+** on the right side of **High HR + Low Activity?** under the **true** output
2. Search for **HTTP Request** and select it
3. Configure these settings:
   - **Method**: POST
   - **URL**: `http://companion-api:8001/api/interventions/trigger`
   - **Body Content Type**: JSON
   - **Body**: `{"user_id": {{$node["Receive Health Data"].json["user_id"]}}, "trigger_type": "biometric"}`
4. Rename the node to **Fire Intervention**
5. Click **Save**

### Step 5: Add No Operation for False branch (Node 4)
1. Click the **+** on the right side of **High HR + Low Activity?** under the **false** output
2. Search for **No Operation** and select it
3. Rename the node to **No action needed**
4. Click **Save**

### Step 6: Save and activate
1. Click the **Save** button (grey, top left)
2. Give the workflow a name like "Biometric Intervention Check"
3. Toggle the **Active** switch (top right) to turn it on

---

## Webhook URL for iOS Shortcut

Your n8n webhook URL will be:
```
https://your-n8n-domain.com/webhook/health-check
```

Replace the URL in your iOS Shortcut with this n8n webhook URL instead of the direct API URL.

---

## How to Test the Workflow

### Option 1: Using the Test Button in n8n
1. Click on the **Receive Health Data** webhook node
2. Click **Test Workflow** (red button)
3. In another tab or using curl, send a test request (see below)
4. The workflow should execute and show green checkmarks

### Option 2: Using curl

Send a test request with elevated heart rate and low steps:
```bash
curl -X POST https://your-n8n-domain.com/webhook/health-check \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"heart_rate":95,"steps_last_hour":5}'
```

Expected response: `{"received": true}`

The workflow should:
- Detect heart_rate > 88 and steps < 20
- Trigger the intervention via HTTP Request
- Show the "Fire Intervention" node lighting up

### Option 3: Using curl with normal values (should not trigger)

```bash
curl -X POST https://your-n8n-domain.com/webhook/health-check \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"heart_rate":72,"steps_last_hour":500}'
```

Expected: The "No action needed" branch should execute instead.

---

## JSON Import

You can import this workflow directly into n8n:

1. Click the menu (three lines, top left)
2. Select **Import from File**
3. Upload this JSON file

Or use the API to import.

```json
{
  "name": "Biometric Intervention Check",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "health-check",
        "responseMode": "onReceived",
        "responseData": "json",
        "options": {
          "rawBody": false
        },
        "responseBody": "{\"received\": true}"
      },
      "id": "webhook",
      "name": "Receive Health Data",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [250, 300],
      "webhookId": "health-check"
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
              "leftValue": "={{$node[\"Receive Health Data\"].json[\"heart_rate\"]}}",
              "rightValue": "88",
              "operator": {
                "type": "number",
                "operator": "gt"
              }
            },
            {
              "leftValue": "={{$node[\"Receive Health Data\"].json[\"steps_last_hour\"]}}",
              "rightValue": "20",
              "operator": {
                "type": "number",
                "operator": "lt"
              }
            }
          ],
          "combinator": "and"
        },
        "fallbackOutput": "none"
      },
      "id": "if",
      "name": "High HR + Low Activity?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [500, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://companion-api:8001/api/interventions/trigger",
        "bodyParameters": {
          "parameters": [
            {
              "name": "user_id",
              "value": "={{$node[\"Receive Health Data\"].json[\"user_id\"]}}"
            },
            {
              "name": "trigger_type",
              "value": "biometric"
            }
          ]
        },
        "options": {}
      },
      "id": "http-request",
      "name": "Fire Intervention",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [750, 150]
    },
    {
      "parameters": {},
      "id": "no-op",
      "name": "No action needed",
      "type": "n8n-nodes-base.noOp",
      "typeVersion": 1,
      "position": [750, 450]
    }
  ],
  "connections": {
    "Receive Health Data": {
      "main": [
        [
          {
            "node": "High HR + Low Activity?",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "High HR + Low Activity?": {
      "main": [
        [
          {
            "node": "Fire Intervention",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "No action needed",
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

## Notes

- This workflow is an **alternative** to the FastAPI's built-in threshold logic
- The FastAPI endpoint already handles the logic (sustained high HR + low activity + active hours)
- Use this n8n workflow if you want n8n to own the threshold decision instead
- You only need ONE of these approaches, not both