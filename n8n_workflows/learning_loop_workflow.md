# Learning Loop Workflow for n8n

This document explains how to create an n8n workflow that receives conversation data from the Companion API, extracts new facts about John, and stores them in Qdrant for future memory retrieval.

---

## Part 1: Add the GET Conversation Endpoint (FastAPI)

Before setting up n8n, add this endpoint to your FastAPI backend to retrieve conversation transcripts.

Add to `companion-backend/routers/messages.py`:

```python
@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: int):
    """Get conversation details including transcript"""
    conn = get_db_connection()
    if not conn:
        return {"error": "Database not configured"}
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, started_at, ended_at, transcript, trigger_type
            FROM conversations WHERE id = %s
        """, (conversation_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            return {"error": "Conversation not found"}
        
        return {
            "id": row[0],
            "user_id": row[1],
            "started_at": row[2].isoformat() if row[2] else None,
            "ended_at": row[3].isoformat() if row[3] else None,
            "transcript": row[4],
            "trigger_type": row[5]
        }
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        if conn:
            conn.close()
        return {"error": str(e)}
```

After adding, rebuild and redeploy your backend.

---

## Part 2: Create n8n Workflow

### Step 1: Create new workflow
1. Open n8n
2. Click **Workflows** > **Add workflow**
3. Name it "Conversation Learning Loop"

### Step 2: Add Webhook (Node 1)
1. Click **+** on canvas
2. Search **Webhook** and select
3. Configure:
   - **HTTP Method**: POST
   - **Path**: `learning-loop`
   - **Response Mode**: Respond immediately
   - **Response Body**: `{"received": true}`
4. Rename to **Conversation Ended**
5. Click **Save**

### Step 3: Add HTTP Request for transcript (Node 2)
1. Click **+** after webhook
2. Search **HTTP Request**
3. Configure:
   - **Method**: GET
   - **URL**: `http://companion-api:8001/api/conversations/{{$json.conversation_id}}`
4. Rename to **Get Transcript**
5. Click **Save**

### Step 4: Add HTTP Request for AI extraction (Node 3)
1. Click **+** after Get Transcript
2. Search **HTTP Request**
3. Configure:
   - **Method**: POST
   - **URL**: `https://openrouter.ai/api/v1/chat/completions`
   - **Authentication**: Pre-defined Credential Type > Header Auth
     - Create a credential with:
       - **Header Name**: Authorization
       - **Header Value**: Bearer YOUR_OPENROUTER_API_KEY
   - **Body Content Type**: JSON
   - **Body**:
     ```json
     {
       "model": "mistralai/mistral-7b-instruct:free",
       "messages": [
         {"role": "system", "content": "Extract new facts about John from this conversation. Return ONLY a JSON array of strings, each string being one new fact. Example: [\"John mentioned his ship was called the SS Orion\", \"John said he likes custard creams\"]"},
         {"role": "user", "content": "Conversation transcript: {{$node['Get Transcript'].json.transcript}}"}
       ],
       "max_tokens": 500
     }
     ```
4. Rename to **Extract New Facts**
5. Click **Save**

### Step 5: Add Code node to parse facts (Node 4)
1. Click **+** after Extract New Facts
2. Search **Code** and select
3. Configure JavaScript:
   ```javascript
   const response = $json.choices[0].message.content;
   let facts = [];
   try {
     facts = JSON.parse(response);
   } catch (e) {
     const match = response.match(/\[[\s\S]*\]/);
     if (match) {
       try {
         facts = JSON.parse(match[0]);
       } catch (e2) {}
     }
   }
   return { facts: Array.isArray(facts) ? facts : [] };
   ```
4. Rename to **Parse Facts**
5. Click **Save**

### Step 6: Add SplitInBatches (Node 5)
1. Click **+** after Parse Facts
2. Search **Split In Batches** and select
3. Configure:
   - **Batch Size**: 1
   - **Options**: Leave defaults
4. Rename to **Process Each Fact**
5. Click **Save**

### Step 7: Add HTTP Request to store fact (Node 6)
1. Click **+** after Process Each Fact
2. Search **HTTP Request**
3. Configure:
   - **Method**: POST
   - **URL**: `http://companion-api:8001/api/carer/memories/upload`
   - **Authentication**: Add a new credential:
     - **Type**: Basic Auth
     - **Username**: carrier (or your configured carrier username)
     - **Password**: your-carer-password
   - **Body Content Type**: JSON
   - **Body**:
     ```json
     {
       "text": "{{$json.facts}}",
       "collection": "life_stories",
       "source": "learning_loop"
     }
     ```
4. Rename to **Store Fact**
5. Click **Save**

### Step 8: Connect nodes
The connections should be:
- Conversation Ended → Get Transcript
- Get Transcript → Extract New Facts
- Extract New Facts → Parse Facts
- Parse Facts → Process Each Fact
- Process Each Fact → Store Fact

### Step 9: Save and activate
1. Click **Save**
2. Toggle **Active** to ON

---

## Part 3: Credentials Setup

### OpenRouter API Key
1. Go to n8n **Settings** > **Credentials**
2. Add new credential
3. Select **Header Auth**
4. Name: "OpenRouter"
5. Header Name: `Authorization`
6. Header Value: `Bearer YOUR_OPENROUTER_API_KEY`

### Carer Credentials
1. Add another credential
2. Select **Basic Auth**
3. Name: "Carer API"
4. Username: `carer` (or your configured CARER_USERNAME)
5. Password: your-carer-password

---

## Part 4: Testing the Workflow

### Test the webhook manually

Get a conversation ID from your database:
```sql
SELECT id FROM conversations ORDER BY id DESC LIMIT 1;
```

Send a test to the webhook:
```bash
curl -X POST https://your-n8n-instance.com/webhook/learning-loop \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": 1, "user_id": 1}'
```

### View execution
1. Click **Executions** in n8n
2. Find your run
3. Click to see each node's input/output

### Check Qdrant
After the workflow runs, verify facts were stored:
```bash
curl http://companion-api:8001/api/carer/collections
```

Or query Qdrant directly to see new life_stories entries.

---

## Part 5: Workflow JSON Export

```json
{
  "name": "Conversation Learning Loop",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "learning-loop",
        "responseMode": "onReceived",
        "responseData": "json",
        "responseBody": "{\"received\": true}"
      },
      "id": "webhook",
      "name": "Conversation Ended",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [250, 300],
      "webhookId": "learning-loop"
    },
    {
      "parameters": {
        "method": "GET",
        "url": "http://companion-api:8001/api/conversations/{{$json.conversation_id}}"
      },
      "id": "get-transcript",
      "name": "Get Transcript",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [500, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "authentication": "headerAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "bodyParameters": {
          "parameters": [
            {
              "name": "model",
              "value": "mistralai/mistral-7b-instruct:free"
            },
            {
              "name": "messages",
              "value": [
                {"role": "system", "content": "Extract new facts about John from this conversation. Return ONLY a JSON array of strings."},
                {"role": "user", "content": "Conversation transcript: {{$node['Get Transcript'].json.transcript}}"}
              ]
            },
            {
              "name": "max_tokens",
              "value": 500
            }
          ]
        }
      },
      "id": "extract-facts",
      "name": "Extract New Facts",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [750, 300]
    },
    {
      "parameters": {
        "jsCode": "const response = $json.choices[0].message.content;\nlet facts = [];\ntry {\n  facts = JSON.parse(response);\n} catch (e) {\n  const match = response.match(/\\[[\\s\\S]*\\]/);\n  if (match) {\n    try {\n      facts = JSON.parse(match[0]);\n    } catch (e2) {}\n  }\n}\nreturn { facts: Array.isArray(facts) ? facts : [] };"
      },
      "id": "parse-facts",
      "name": "Parse Facts",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1000, 300]
    },
    {
      "parameters": {
        "batchSize": 1
      },
      "id": "split",
      "name": "Process Each Fact",
      "type": "n8n-nodes-base.splitInBatches",
      "typeVersion": 1,
      "position": [1250, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://companion-api:8001/api/carer/memories/upload",
        "authentication": "basicAuth",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {"name": "text", "value": "{{$json.facts}}"},
            {"name": "collection", "value": "life_stories"},
            {"name": "source", "value": "learning_loop"}
          ]
        }
      },
      "id": "store-fact",
      "name": "Store Fact",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1500, 300]
    }
  ],
  "connections": {
    "Conversation Ended": {
      "main": [[{"node": "Get Transcript", "type": "main", "index": 0}]]
    },
    "Get Transcript": {
      "main": [[{"node": "Extract New Facts", "type": "main", "index": 0}]]
    },
    "Extract New Facts": {
      "main": [[{"node": "Parse Facts", "type": "main", "index": 0}]]
    },
    "Parse Facts": {
      "main": [[{"node": "Process Each Fact", "type": "main", "index": 0}]]
    },
    "Process Each Fact": {
      "main": [[{"node": "Store Fact", "type": "main", "index": 0}]]
    }
  },
  "active": true,
  "settings": {},
  "tags": []
}
```

---

## How It Works

1. When a conversation becomes stale (10+ minutes), the backend fires a webhook to n8n
2. n8n fetches the full conversation transcript
3. OpenRouter AI analyses the conversation and extracts new facts about John
4. Each fact is stored in Qdrant under the "life_stories" collection
5. Future conversations can retrieve these newly learned memories

---

## Troubleshooting

### Webhook not triggering
- Ensure N8N_LEARNING_WEBHOOK_URL is set in your backend environment
- Check n8n webhook is active
- Verify firewall allows webhook connections

### No facts extracted
- Check the OpenRouter response in the execution log
- Verify the transcript is being passed correctly
- Ensure the model has enough context

### Facts not storing
- Verify carrier credentials are correct
- Check Qdrant is accessible from n8n
- Look for errors in API response