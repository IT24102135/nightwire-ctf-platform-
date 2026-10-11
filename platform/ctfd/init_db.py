#!/usr/bin/env python3
import time
import sys
from werkzeug.security import generate_password_hash

print("[INIT] Waiting for database...")
for i in range(30):
    try:
        from CTFd.models import db, Users, Teams, TeamMembers, Challenges, Hints, Flags
        from CTFd import create_app
        app = create_app()
        with app.app_context():
            db.engine.execute("SELECT 1")
            print("[INIT] ✓ Database ready")
            break
    except Exception as e:
        print(f"[INIT] Waiting... ({i+1}/30)")
        time.sleep(1)
else:
    print("[INIT] ✗ Database timeout")
    sys.exit(1)

print("[INIT] Creating test data...")
try:
    from CTFd.models import db, Users, Teams, TeamMembers, Challenges, Hints, Flags
    from CTFd import create_app
    app = create_app()
    with app.app_context():
        admin = Users.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = Users(name='Administrator', email='admin@example.com', password=generate_password_hash('password123'), admin=True, verified=True, hidden=False, banned=False)
            db.session.add(admin)
            print("[INIT] ✓ Created admin")
        db.session.commit()
        test_team = Teams.query.filter_by(name='TestTeam').first()
        if not test_team:
            player = Users(name='Player', email='player@example.com', password=generate_password_hash('password123'), admin=False, verified=True, hidden=False, banned=False)
            db.session.add(player)
            db.session.flush()
            test_team = Teams(name='TestTeam', email='testteam@example.com', captain_id=player.id, banned=False)
            db.session.add(test_team)
            db.session.flush()
            team_member = TeamMembers(user_id=player.id, team_id=test_team.id)
            db.session.add(team_member)
            print("[INIT] ✓ Created team and player")
        db.session.commit()
        challenge = Challenges.query.filter_by(name='Test Challenge').first()
        if not challenge:
            challenge = Challenges(name='Test Challenge', description='Test challenge for hint penalty system', value=100, category='test', type='standard', state='visible', hidden=False, max_attempts=0)
            db.session.add(challenge)
            db.session.flush()
            flag = Flags(challenge_id=challenge.id, content='flag{test123}', type='static', data='')
            db.session.add(flag)
            print("[INIT] ✓ Created challenge")
        db.session.commit()
        hint1 = Hints.query.filter_by(challenge_id=challenge.id, content__startswith='This is hint 1').first() if challenge else None
        if not hint1:
            hint1 = Hints(challenge_id=challenge.id, content='This is hint 1: Look for patterns in the problem statement.', cost=5, requirements=None)
            db.session.add(hint1)
            hint2 = Hints(challenge_id=challenge.id, content='This is hint 2: The flag format is flag{...} - try common words.', cost=5, requirements=None)
            db.session.add(hint2)
            print("[INIT] ✓ Created hints")
        db.session.commit()
        print("\n" + "="*60)
        print("✓ INITIALIZATION COMPLETE")
        print("="*60)
        print("Admin:  admin@example.com / password123")
        print("Player: player@example.com / password123")
        print("Team:   TestTeam")
        print("Challenge: Test Challenge (100 pts, 2 hints @ 5 pts)")
        print("Flag: flag{test123}")
        print("="*60)
except Exception as e:
    print(f"[INIT] ✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
