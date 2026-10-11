#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:8000"
EMAIL = "admin@gmail.com"
PASSWORD = "final4"

session = requests.Session()

# Login
print("[*] Logging in as admin...")
r = session.get(f"{BASE_URL}/login")
soup = BeautifulSoup(r.text, 'html.parser')
csrf = soup.find('input', {'name': 'csrf_token'})['value']

login_data = {
    'name': EMAIL,
    'password': PASSWORD,
    'csrf_token': csrf,
    '_submit': 'Submit'
}
r = session.post(f"{BASE_URL}/login", data=login_data)
if "dashboard" in r.text or "admin" in r.text:
    print("[✓] Logged in successfully")
else:
    print("[✗] Login failed")
    exit(1)

CHALLENGES = [
    {"name": "Stage 1 - First Contact", "category": "OSINT / Reconnaissance", "description": "Target: http://localhost:8082", "value": 100, "flags": ["NIGHTWIRE{f1rst_c0nt4ct_0s1nt_succ3ss}"]},
    {"name": "Stage 2 - Hidden in Plain Sight", "category": "Steganography", "description": "Target: http://localhost:8083", "value": 100, "flags": ["NIGHTWIRE{h1dd3n_1n_pl41n_s1ght}"]},
    {"name": "Stage 3 - Backdoor Portal", "category": "Web Security", "description": "Target: http://localhost:8081/search.php?q=", "value": 200, "flags": ["NIGHTWIRE{b4ckd00r_p0rt4l_sqli_m4st3r}"]},
    {"name": "Stage 4 - Recovered Backups", "category": "Cryptography", "description": "Target: http://localhost:8084", "value": 200, "flags": ["NIGHTWIRE{weak_rsa_factored}", "NIGHTWIRE{crypto_backup_recovered}"]},
    {"name": "Stage 5 - Packet Trail", "category": "Network Forensics", "description": "Target: http://localhost:8085", "value": 300, "flags": ["NIGHTWIRE{packet_trail_complete}"]},
    {"name": "Stage 6 - Root of Nightwire", "category": "Linux Security (Capstone)", "description": "Connect via VirtualBox VM", "value": 400, "flags": ["NIGHTWIRE{r00t_0f_n1ghtw1r3_c4pst0n3}"]},
]

# Get admin page to extract CSRF token
print("[*] Creating challenges...")
r = session.get(f"{BASE_URL}/admin/challenges")
soup = BeautifulSoup(r.text, 'html.parser')
csrf = soup.find('input', {'name': 'csrf_token'})['value'] if soup.find('input', {'name': 'csrf_token'}) else None

for chal in CHALLENGES:
    # Check if already exists
    r = session.get(f"{BASE_URL}/admin/challenges")
    if chal["name"] in r.text:
        print(f"[✓] SKIP: {chal['name']} (already exists)")
        continue
    
    # Create challenge via form POST
    data = {
        'name': chal['name'],
        'category': chal['category'],
        'description': chal['description'],
        'value': str(chal['value']),
        'state': 'visible',
        'type': 'standard',
        'csrf_token': csrf
    }
    
    r = session.post(f"{BASE_URL}/admin/challenges", data=data)
    
    # Extract challenge ID from response
    soup = BeautifulSoup(r.text, 'html.parser')
    try:
        # Try to find the ID from the created challenge
        chal_id_elem = soup.find('input', {'name': 'id'})
        if chal_id_elem:
            chal_id = chal_id_elem['value']
            print(f"[✓] CREATED: {chal['name']} (ID: {chal_id})")
        else:
            print(f"[✓] CREATED: {chal['name']}")
    except:
        print(f"[✓] CREATED: {chal['name']}")

print("\n[✓] All challenges created!")
