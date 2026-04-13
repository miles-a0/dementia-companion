# Quick Deploy Guide for Dementia Companion

This guide gets the app running in about 30 minutes.

---

## What You Need

- Portainer access
- Your existing n8n at https://n8n.zu-auto.co.uk/ (already working)
- Your existing Qdrant at 173.249.40.161:5467 (already working)

---

## Step 1: Update the .env File

The `.env` file is already in the repo but you need to update it with your passwords.

1. In the project folder, open: `companion-backend/.env`
2. Update these values with real passwords:

```
DATABASE_URL=postgresql://companion:YOUR_POSTGRES_PASSWORD@db:5432/companion

CARER_USERNAME=carer
CARER_PASSWORD=YOUR_CARER_PASSWORD
```

Save the file.

---

## Step 2: Create the Stack in Portainer

1. Go to **Stacks** in Portainer
2. Click **Add Stack**
3. Name: `companion-app`
4. Copy the content from `docker-compose.companion.yml` in this repo
5. Click **Deploy the stack**

Wait 2-3 minutes for it to build and start.

---

## Step 3: Add n8n to the Network (Optional - for faster webhooks)

If you want n8n to receive webhooks from the API:

1. Go to **Containers** in Portainer
2. Find your n8n container
3. Click **Edit**
4. Under **Networks**, add `companion-net`
5. Click **Update**

---

## Step 4: Test It Works

### Test API is running:
```bash
curl http://your-server-ip:8001/api/health
```
Should return: `{"status": "ok", "service": "companion-api"}`

### Test Carrier Login:
1. Go to `http://your-server-ip:8001`
2. Click "Carrier" in bottom right
3. Login with username: `carer` and password you set in .env

---

## Step 5: Import n8n Workflows

Go to https://n8n.zu-auto.co.uk/ and import these workflows from the repo:

1. **Morning Routine**: `n8n_workflows/morning_routine_workflow.md` → Copy JSON at bottom → Import
2. **Medication Reminders**: `n8n_workflows/medication_reminder_workflow.md` → Import
3. **Learning Loop**: `n8n_workflows/learning_loop_workflow.md` → Import

For each workflow:
- Click **Save**
- Toggle **Active** to ON

---

## Step 6: Test on John's iPhone

1. Open Safari on John's iPhone
2. Go to `http://your-server-ip:8001`
3. Tap **Share** → **Add to Home Screen**
4. Name it "John's Companion"

---

## Need Help?

If something doesn't work:

1. **Check API logs**: Portainer → Containers → companion-api → Logs
2. **Check database**: Make sure PostgreSQL container is running
3. **Check ports**: 8001 (API), 5466 (Postgres external), 5467 (Qdrant external)

---

## Quick Command to Test Everything

```bash
# Is API running?
curl http://your-server-ip:8001/api/health

# Is it connecting to database?
curl http://your-server-ip:8001/api/messages/pending?user_id=1

# Can it reach n8n?
curl -X POST https://n8n.zu-auto.co.uk/webhook/learning-loop -H "Content-Type: application/json" -d '{"conversation_id":1,"user_id":1}'
```