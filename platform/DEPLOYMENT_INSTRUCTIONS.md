# NIGHTWIRE CTF Hints System Deployment

## What Changed

This deployment adds the hint score deduction system to CTFd. When players view hints, points are automatically deducted from their scores and shown in real-time on the scoreboard.

### Files Modified/Added:
- `scores-init.py` - Updated CTFd scoring engine with hint deduction logic
- `hint-score-adjuster.py` - Background service that monitors hint views
- `docker-compose.yml` - Updated to mount the new scoring code

## Deployment Steps

### Step 1: Restart Docker Containers

Navigate to the platform/ctfd directory and restart the containers:

```bash
cd platform/ctfd
docker-compose down
docker-compose up -d
```

Wait 30 seconds for the containers to start. Then verify:

```bash
docker ps
```

You should see three running containers: ctfd, db (mariadb), and cache (redis).

### Step 2: Start the Background Service

The background service monitors hint views and records point deductions. Run it with Python:

```bash
cd platform
python3 hint-score-adjuster.py
```

The service will:
- Monitor the database for new hint views every 5 seconds
- Automatically create the hint_deductions table if needed
- Log all deductions with timestamps
- Continue running until you press Ctrl+C

**For production deployment**, use a process manager like:

```bash
# Using nohup (simple, logs to file)
nohup python3 hint-score-adjuster.py > hint-adjuster.log 2>&1 &

# Using screen (can reconnect to terminal)
screen -S hint-adjuster python3 hint-score-adjuster.py

# Or as a systemd service (most robust)
# Create /etc/systemd/system/hint-adjuster.service
```

### Step 3: Test the System

1. Create a test challenge and solve it (admin panel)
2. View a hint for the solved challenge
3. Check the scoreboard - the player's score should decrease by 5 points
4. Verify logs in the hint-score-adjuster terminal show the deduction

## How It Works

1. **Player views a hint** → Recorded in CTFd's `unlocks` table
2. **Background service detects** → Creates entry in `hint_deductions` table with cost
3. **Scoreboard recalculates** → New scoring engine subtracts deductions from total
4. **Score updates in real-time** → Players see reduced score immediately

## Configuration

To change the points deducted per hint, edit:

```python
# In hint-score-adjuster.py
HINT_COST = 5  # Change this value
```

## Rollback (if needed)

If something breaks:

1. Revert docker-compose.yml to original (remove the volumes line)
2. Run `docker-compose restart ctfd`
3. Stop the hint-score-adjuster service

## Troubleshooting

- **Scoreboard shows "Scoreboard is empty"** → This is normal if no challenges have been solved
- **"Cannot connect to database"** → Wait for containers to fully start (may take 30+ seconds)
- **Points not deducting** → Check hint-score-adjuster logs for errors
- **500 errors** → Check Docker logs: `docker logs ctfd`

## Database Tables

The system uses two tables:

1. **hint_deductions** (created automatically)
   - Stores each hint view and its cost
   - User must exist in users table
   - Prevents duplicate deductions

2. **unlocks** (existing CTFd table)
   - Standard CTFd table where hints are recorded when viewed

