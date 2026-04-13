# iOS Shortcut Setup for John's Health Monitoring

---

## SECTION 1: What This Does

This iOS Shortcut automatically reads John's heart rate and step count from his Apple Watch and iPhone, then sends this information to his Companion app every 30 minutes. If his heart rate stays elevated for too long while he's not moving much, the system will automatically send him a gentle check-in message.

---

## SECTION 2: Creating the Shortcut

Follow these steps exactly. The buttons you need to tap are shown in **bold**.

### Step 1: Open the Shortcuts App
1. Find the **Shortcuts** app on John's iPhone (it looks like a silver puzzle piece icon)
2. Tap to open it

### Step 2: Create a New Shortcut
1. At the bottom of the screen, tap the **+** (plus sign) button
2. You will see "New Shortcut" at the top

### Step 3: Add Heart Rate Action
1. Tap **Add Action** (a blue button)
2. In the search bar at the top, type **Health**
3. Tap on **Health** in the results
4. Tap **Heart Rate**
5. Tap **Most Recent** (it will already be selected)
6. Tap the blue arrow **Next** at the top right

### Step 4: Add Step Count Action
1. Tap **Add Action** again
2. Type **Health** in the search bar
3. Tap **Health**
4. Tap **Step Count**
5. Tap **Cumulative**
6. Tap **Start Date** and select **Current Date**
7. Tap **End Date** and select **Current Date**
8. Tap the blue arrow **Next** at the top right

### Step 5: Add Current Date Action
1. Tap **Add Action**
2. Type **Date** in the search bar
3. Tap **Date**
4. Tap **Date** (the default action)
5. Tap the blue arrow **Next** at the top right

### Step 6: Add URL Request (POST to Backend)
1. Tap **Add Action**
2. Type **URL** in the search bar
3. Tap **URL**
4. In the **URL** field, type exactly:
   ```
   http://173.249.40.161:8001/api/health/biometrics
   ```
5. Tap **Method** and select **POST**
6. Tap **Add Field** and select **Body**
7. Tap **JSON**
8. Tap **Add Item** and type these lines exactly:

   - Key: `user_id` | Value: `1`
   - Key: `heart_rate` | Tap and select **Heart Rate** from the list
   - Key: `steps_last_hour` | Tap and select **Step Count** from the list
   - Key: `timestamp` | Tap and select **Date** from the list

9. Tap **Done**
10. Tap the blue arrow **Next** at the top right

### Step 7: Add Notification
1. Tap **Add Action**
2. Type **Notification** in the search bar
3. Tap **Notification**
4. In the **Title** field, type: `Health Data Sent`
5. In the **Body** field, type: `John's health data has been sent to Companion`
6. Tap **Done**

### Step 8: Name the Shortcut
1. At the top where it says "New Shortcut", tap the text
2. Delete it and type: `Send Health Data`
3. Tap **Done** (top right)

### Step 9: Save the Shortcut
1. Tap the **checkmark** at the top right
2. You should now see "Send Health Data" in your shortcuts list

---

## SECTION 3: Setting Up the Automation

Now we'll make this run automatically every 30 minutes without asking.

### Step 1: Create an Automation
1. In the Shortcuts app, tap the **Automation** tab at the bottom (looks like a clock)
2. Tap **Create Personal Automation** (the blue button)

### Step 2: Set the Time Trigger
1. Tap **Time of Day**
2. Tap **Morning**, **Afternoon**, or **Evening** to select the general time
3. Under "Repeat", tap **Every 30 minutes**
4. Set the **Start Time** to 07:00
5. Set the **End Time** to 22:00
6. Tap **Next**

### Step 3: Select the Shortcut
1. Tap **Add Action**
2. Type **Shortcuts** in the search bar
3. Tap **Run Shortcut**
4. Tap the **Shortcut** field
5. Select **Send Health Data**
6. Tap **Next**

### Step 4: Turn Off Ask Before Running
1. Look for the toggle called **Ask Before Running**
2. **Flip it OFF** (it should be grey, not green)
   - This is very important — it makes the shortcut run silently in the background

### Step 5: Finish
1. Tap **Done** at the top right
2. The automation should now show in your list with a clock icon

---

## SECTION 4: Testing the Shortcut

### How to Test Manually

1. Open the Shortcuts app
2. Find **Send Health Data** in your shortcuts list
3. Tap it once
4. You should see a notification that says "Health Data Sent"
5. Wait about 1 minute, then check your Postgres database to see if the data was received

### How to Verify It Worked

In your Postgres database, run this query:
```sql
SELECT * FROM biometrics ORDER BY recorded_at DESC LIMIT 5;
```

You should see a new row with:
- `user_id` = 1
- `heart_rate` = some number (likely between 60-100)
- `steps_last_hour` = some number
- `recorded_at` = the current time

### If No Heart Rate Data Appears

This means the Apple Watch hasn't sent heart rate data to the iPhone yet. Make sure:
1. John is wearing his Apple Watch
2. The Watch is connected to the iPhone (look for the green icon on Watch)
3. The Watch has sent at least one heart rate reading to the Health app

To check:
- Open the **Health** app on iPhone
- Tap **Heart Rate** — you should see recent readings

---

## SECTION 5: Troubleshooting

### Problem: Shortcut asks for permission every time

**Solution:**
1. Go to **Settings** > **Shortcuts** > **Privacy**
2. Make sure **Health** is allowed
3. Also check **Notifications** are allowed
4. When you run the shortcut, tap **Allow** and check "Don't Ask Again"

### Problem: No heart rate data available

**Solution:**
1. Make sure the Apple Watch is paired with the iPhone
2. Make sure the Watch is being worn
3. Open the Health app and check the Heart Rate section
4. If still nothing, try opening the Heart Rate app on the Watch and taking a reading

### Problem: Network error when sending data

**Solution:**
1. Make sure the iPhone has internet (try opening a website)
2. Check that your VPS firewall allows incoming connections on port 8001
3. Try the URL in a browser: `http://173.249.40.161:8001/api/health/biometrics`
   - You should see: `{"received": true}`

### Problem: Automation doesn't run

**Solution:**
1. Go to **Settings** > **Shortcuts** > **Automation**
2. Make sure your automation is turned ON
3. Check that "Time of Day" automation is allowed
4. Try turning it off and back on again

---

## Important Notes

- The shortcut will run automatically from 07:00 to 22:00 every day
- It will run every 30 minutes during that time
- John's iPhone must be turned on and have internet connection
- If the iPhone is in Low Power Mode, automations may not run