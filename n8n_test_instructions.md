# Testing the polling loop with n8n

## Step 1: Manually insert a test message into Postgres
Run this SQL on your VPS Postgres database:
INSERT INTO messages (user_id, content, message_type)
VALUES (1, 'Good morning John! It is a lovely day today.', 'greeting');

## Step 2: Trigger an immediate poll
In the browser console on the Companion app, run:
import('/src/services/polling.js').then(p => p.pollNow(console.log, 1))

## Step 3: Expected behaviour
- The greeting message should appear in the GreetingBanner within 60 seconds
  (or immediately if pollNow is used)
- The message should be spoken aloud by the TTS
- After 30 seconds the banner should fade out

## Step 4: Build n8n test workflow
In your n8n instance, create a new workflow:
- Trigger: Manual trigger
- Node: HTTP Request
  - Method: POST
  - URL: http://companion-api:8001/api/messages/queue
  - Body (JSON): {"user_id": 1, "content": "Hello John, this is a test message.", "message_type": "greeting"}
- Execute the workflow
- The message should appear on John's device within 60 seconds