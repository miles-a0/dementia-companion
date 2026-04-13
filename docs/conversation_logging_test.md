# Testing Conversation Logging

## Overview

This document explains how to test the conversation logging feature implemented in Phase 10.

## What Was Added

- `get_or_create_conversation()` - Gets existing open conversation or creates new one
- `append_to_transcript()` - Appends user/assistant messages to transcript
- `check_and_close_stale_conversations()` - Closes conversations older than 10 minutes and triggers learning webhook
- Updated `POST /messages/respond` to use these helpers

## Testing Steps

### Step 1: Test the /messages/respond endpoint

Send a chat message to trigger a new conversation:

```bash
curl -X POST http://173.249.40.161:8001/api/messages/respond \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello John, how are you today?", "user_id": 1}'
```

Expected response:
```json
{
  "response": "I'm here to help you, John.",
  "conversation_id": 1
}
```

### Step 2: Verify conversation was created

Connect to your Postgres database and run:

```sql
SELECT id, user_id, started_at, ended_at, trigger_type 
FROM conversations 
ORDER BY id DESC LIMIT 5;
```

You should see a new row with:
- `user_id` = 1
- `started_at` = current timestamp
- `ended_at` = NULL (still open)

### Step 3: Verify transcript was populated

```sql
SELECT transcript FROM conversations ORDER BY id DESC LIMIT 1;
```

The transcript should contain JSON like:
```json
[
  {"role": "user", "text": "Hello John, how are you today?", "time": "2026-04-13T..."},
  {"role": "assistant", "text": "I'm here to help you, John.", "time": "2026-04-13T..."}
]
```

### Step 4: Send another message in the same conversation

```bash
curl -X POST http://173.249.40.161:8001/api/messages/respond \
  -H "Content-Type: application/json" \
  -d '{"text": "What is the date today?", "user_id": 1}'
```

The `conversation_id` in the response should be the same as the previous request.

### Step 5: Verify transcript was appended

```sql
SELECT transcript FROM conversations WHERE id = 1;
```

Should now have 4 entries (2 user, 2 assistant).

### Step 6: Test stale conversation closure

Wait 10 minutes, then send another request. The old conversation should be closed and a new one started.

Alternatively, manually close a conversation:

```sql
UPDATE conversations SET ended_at = NOW() WHERE id = 1;
```

Then send a new request - it should create a new conversation (id will be different).

### Step 7: Test learning webhook (optional)

Set the environment variable `N8N_LEARNING_WEBHOOK_URL` in your docker-compose or .env file:

```
N8N_LEARNING_WEBHOOK_URL=https://your-n8n-instance.com/webhook/learning
```

When a conversation is closed (after 10 minutes of inactivity), it will POST to this webhook with:
```json
{
  "conversation_id": 1,
  "user_id": 1
}
```

## Troubleshooting

### No conversations being created
- Check DATABASE_URL is set in environment
- Check Postgres is running: `docker-compose ps`

### transcript field is empty
- Verify the conversations table has JSONB column for transcript
- Check API logs: `docker-compose logs companion-api`

### conversation_id always null in response
- Ensure get_or_create_conversation is returning the ID
- Check for errors in the try/except block