# Complete Deployment Guide for Dementia Companion App

This guide walks you through deploying the complete dementia companion system on your VPS using Portainer.

---

## What We'll Deploy

The system has 5 main parts:

1. **Companion API** - The backend FastAPI server
2. **Companion Frontend** - The React PWA that runs on John's iPhone
3. **PostgreSQL** - Database to store messages, conversations, medications
4. **Qdrant** - Vector database for storing and searching memories
5. **n8n** - Automation workflow engine (runs the reminders, learning loop)

---

## Prerequisites

- A VPS with Docker installed
- Portainer already set up on your VPS
- A domain name (optional, but recommended)

---

## Step 1: Prepare the Docker Environment

### 1.1 Create a Docker Network

In Portainer:
1. Go to **Networks** (left menu)
2. Click **Add Network**
3. Name: `companion-network`
4. Driver: `bridge`
5. Click **Create**

---

## Step 2: Deploy PostgreSQL Database

### 2.1 Create the Container

In Portainer:
1. Go to **Containers** (left menu)
2. Click **Add Container**
3. Configure:
   - **Name**: `companion-db`
   - **Image**: `postgres:15`
   - **Network**: Select `companion-network`
4. Click **Publish a new network port**:
   - Host: `5466`
   - Container: `5432`
5. Scroll down to **Env** (environment variables) and add:
   - `POSTGRES_DB`: `companion`
   - `POSTGRES_USER`: `companion`
   - `POSTGRES_PASSWORD`: `Choose a strong password here`
6. Scroll to **Volumes** and add:
   - Type: **Bind**
   - Host path: `/opt/companion/postgres` (create this folder on your VPS first)
   - Container path: `/var/lib/postgresql/data`
7. Click **Deploy the container**

### 2.2 Create the Database Tables

Connect to the database using a tool like DBeaver or via command line:

```bash
docker exec -it companion-db psql -U companion -d companion
```

Run this SQL to create all the tables:

```sql
-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    read_at TIMESTAMP,
    spoken_at TIMESTAMP
);

-- Biometrics table
CREATE TABLE IF NOT EXISTS biometrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    heart_rate INTEGER,
    steps_last_hour INTEGER DEFAULT 0,
    recorded_at TIMESTAMP DEFAULT NOW(),
    intervention_triggered BOOLEAN DEFAULT FALSE
);

-- Medications table
CREATE TABLE IF NOT EXISTS medications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    dose VARCHAR(100),
    times_of_day TEXT[],
    instructions TEXT,
    active BOOLEAN DEFAULT TRUE
);

-- Medication log table
CREATE TABLE IF NOT EXISTS medication_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    medication_id INTEGER,
    scheduled_at TIMESTAMP,
    confirmed_at TIMESTAMP,
    reminder_sent_at TIMESTAMP
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    transcript JSONB DEFAULT '[]'::jsonb,
    summary TEXT,
    trigger_type VARCHAR(50)
);

-- Intervention log table
CREATE TABLE IF NOT EXISTS intervention_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    triggered_at TIMESTAMP DEFAULT NOW(),
    trigger_type VARCHAR(50),
    message_sent TEXT,
    conversation_id INTEGER,
    duration_seconds INTEGER
);

-- Game log table
CREATE TABLE IF NOT EXISTS game_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    game_type VARCHAR(50),
    correct BOOLEAN,
    topic VARCHAR(100),
    played_at TIMESTAMP DEFAULT NOW()
);
```

---

## Step 3: Deploy Qdrant (Vector Database)

In Portainer:
1. Go to **Containers** > **Add Container**
2. Configure:
   - **Name**: `companion-qdrant`
   - **Image**: `qdrant/qdrant:latest`
   - **Network**: `companion-network`
3. Publish port:
   - Host: `6333`
   - Container: `6333`
4. Add another port:
   - Host: `6334`
   - Container: `6334`
5. Volumes:
   - Host path: `/opt/companion/qdrant`
   - Container path: `/qdrant/storage`
6. Click **Deploy**

---

## Step 4: Deploy n8n (Automation)

In Portainer:
1. Go to **Containers** > **Add Container**
2. Configure:
   - **Name**: `companion-n8n`
   - **Image**: `n8nio/n8n:latest`
   - **Network**: `companion-network`
3. Publish port:
   - Host: `5678`
   - Container: `5678`
4. Environment variables:
   - `N8N_BASIC_AUTH_ACTIVE`: `true`
   - `N8N_BASIC_AUTH_USER`: `admin`
   - `N8N_BASIC_AUTH_PASSWORD`: `Choose a password`
   - `WEBHOOK_URL`: `http://your-vps-ip:5678`
5. Volumes:
   - Host path: `/opt/companion/n8n`
   - Container path: `/home/node/.n8n`
6. Click **Deploy**

---

## Step 5: Deploy Companion API (Backend)

In Portainer:
1. Go to **Containers** > **Add Container**
2. Configure:
   - **Name**: `companion-api`
   - **Image**: `python:3.12-slim`
   - **Network**: `companion-network`
3. We'll build the image from your GitHub repo instead. Click **Create Build** instead:
   - Build context: `companion-backend`
   - Build method: `Git repository`
   - URL: `https://github.com/miles-a0/dementia-companion`
   - Dockerfile: `companion-backend/Dockerfile`

**OR** simpler method - create a Stack instead. See Step 8.

---

## Step 6: Deploy Companion Frontend

The frontend will be built into the API container and served from there, or we can deploy it separately. For simplicity, let's use a Stack to deploy everything together.

---

## Step 7: Create Docker Compose Stack (Recommended)

Instead of deploying containers one by one, let's use Docker Compose. This handles everything automatically.

Create a file called `docker-compose.companion.yml` in Portainer's Stacks:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15
    container_name: companion-db
    environment:
      POSTGRES_DB: companion
      POSTGRES_USER: companion
      POSTGRES_PASSWORD: your_secure_password_here
    volumes:
      - /opt/companion/postgres:/var/lib/postgresql/data
    networks:
      - companion-network
    restart: unless-stopped

  # Qdrant Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    container_name: companion-qdrant
    volumes:
      - /opt/companion/qdrant:/qdrant/storage
    ports:
      - "6333:6333"
      - "6334:6334"
    networks:
      - companion-network
    restart: unless-stopped

  # n8n Automation
  n8n:
    image: n8nio/n8n:latest
    container_name: companion-n8n
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your_n8n_password
      - WEBHOOK_URL=http://localhost:5678
    volumes:
      - /opt/companion/n8n:/home/node/.n8n
    ports:
      - "5678:5678"
    networks:
      - companion-network
    restart: unless-stopped

  # Companion Backend API
  api:
    build:
      context: ./companion-backend
      dockerfile: Dockerfile
    container_name: companion-api
    environment:
      - DATABASE_URL=postgresql://companion:your_secure_password_here@db:5432/companion
      - QDRANT_URL=http://qdrant:6333
      - JWT_SECRET=change_this_to_a_secure_random_string
      - CARER_USERNAME=carer
      - CARER_PASSWORD=your_carer_password
      - N8N_LEARNING_WEBHOOK_URL=http://n8n:5678/webhook/learning-loop
      - OPENROUTER_API_KEY=your_openrouter_api_key_here
    ports:
      - "8001:8000"
    depends_on:
      - db
      - qdrant
    networks:
      - companion-network
    restart: unless-stopped

networks:
  companion-network:
    driver: bridge
```

### Deploy the Stack

1. In Portainer, go to **Stacks** (left menu)
2. Click **Add Stack**
3. Name: `companion-app`
4. Paste the docker-compose code above
5. Scroll to bottom and click **Deploy the stack**

---

## Step 8: Configure Environment Variables

After the stack deploys, you need to set these important variables:

### 8.1 CARER_PASSWORD
This is the password you'll use to log into the Carer Dashboard.
- In the stack, edit the `api` service
- Change `your_carer_password` to something secure

### 8.2 JWT_SECRET
A random string that protects the carrier login. Generate one at: https://randomkeygen.com/

### 8.3 OPENROUTER_API_KEY
Get a free key from https://openrouter.ai/ for AI responses.

### 8.4 Recreate containers after changes
After changing environment variables, go to the container and click **Recreate**.

---

## Step 9: Set Up n8n Workflows

Now that n8n is running, let's add the automation workflows.

### 9.1 Access n8n
1. Go to `http://your-vps-ip:5678`
2. Log in with username: `admin` and password you set in Step 7

### 9.2 Import Morning Routine Workflow
1. Go to your GitHub repo: `n8n_workflows/morning_routine_workflow.md`
2. Copy the JSON part at the bottom
3. In n8n, click the menu (top left) > **Import from File**
4. Paste the JSON and click **Import**
5. Click **Save** and turn **Active** on

### 9.3 Import Medication Reminder Workflow
1. Go to `n8n_workflows/medication_reminder_workflow.md`
2. Import the JSON the same way

### 9.4 Import Learning Loop Workflow
1. Go to `n8n_workflows/learning_loop_workflow.md`
2. Import the JSON
3. Set up the OpenRouter credential (see the guide)

### 9.5 Import Biometric Workflow (Optional)
1. Go to `n8n_workflows/biometric_intervention_workflow.md`
2. Import the JSON

---

## Step 10: Initialise the Database

Once the API is running, run the database migrations:

```bash
docker exec -it companion-api python db/migrations/run_migrations.py
```

Or if the migration script doesn't exist, create the tables manually as shown in Step 2.2.

---

## Step 11: Test the System

### 11.1 Test the API
```bash
curl http://your-vps-ip:8001/api/health
```
Should return: `{"status": "ok", "service": "companion-api"}`

### 11.2 Test the Frontend
Open in browser: `http://your-vps-ip:8001`

### 11.3 Test Carrier Login
1. Click "Carrier" link in bottom right
2. Login with username: `carrier` and password you set
3. You should see the Carrier Dashboard

### 11.4 Test a Morning Greeting
```bash
curl -X POST http://your-vps-ip:8001/api/routines/morning-greeting \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

### 11.5 Check the Database
```bash
docker exec -it companion-db psql -U companion -d companion -c "SELECT * FROM messages;"
```

---

## Step 12: Set Up John's iPhone

### 12.1 Open the App
On John's iPhone, open Safari and go to: `http://your-vps-ip:8001`

### 12.2 Add to Home Screen
1. Tap the Share button
2. Scroll down and tap **Add to Home Screen**
3. Name it "John's Companion"

### 12.3 Set Up iOS Shortcut (for biometric data)
Follow the guide in `docs/ios_shortcut_setup.md`

---

## Important URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | `http://your-vps-ip:8001` | John's app |
| Carrier Dashboard | `http://your-vps-ip:8001/carer` | For you to manage |
| n8n | `http://your-vps-ip:5678` | Automation workflows |
| API Health | `http://your-vps-ip:8001/api/health` | Check if API is running |

---

## Troubleshooting

### "Database not configured" error
- Check DATABASE_URL environment variable is correct
- Verify the db container is running

### "Connection refused" errors
- Make sure all containers are on the same network (`companion-network`)
- Check container logs in Portainer

### n8n workflows not triggering
- Make sure workflow is "Active" (toggle switch)
- Check the webhook URL matches what's in the backend env

### Frontend not loading
- Check the API is running: `curl http://your-vps-ip:8001/api/health`
- Check browser console for errors

---

## Security Notes

1. **Change all default passwords** - The ones I set as placeholders
2. **Use HTTPS** - Consider setting up nginx with SSL
3. **Keep backups** - Regularly backup `/opt/companion/`
4. **Update regularly** - Pull new images periodically

---

## Quick Command Reference

```bash
# View all containers
docker ps

# View logs
docker logs companion-api

# Restart a container
docker restart companion-api

# Access database
docker exec -it companion-db psql -U companion -d companion

# Rebuild after code changes
cd companion-backend
docker build -t companion-api .
docker rm -f companion-api
docker run -d --name companion-api ...
```

---

## Need Help?

If something goes wrong:
1. Check container logs in Portainer
2. Verify environment variables are correct
3. Make sure all containers are running
4. Check the database tables exist