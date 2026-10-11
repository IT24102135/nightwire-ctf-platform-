#!/usr/bin/env python3
import requests
import sys

BASE_URL = "http://localhost:8000"
API_TOKEN = input("Paste your CTFd admin API token: ").strip()

HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json",
}

CHALLENGES = [
    {"name": "Stage 1 - First Contact", "category": "OSINT / Reconnaissance", "description": "Target: http://localhost:8082", "value": 100, "flags": ["NIGHTWIRE{f1rst_c0nt4ct_0s1nt_succ3ss}"]},
    {"name": "Stage 2 - Hidden in Plain Sight", "category": "Steganography", "description": "Target: http://localhost:8083", "value": 100, "flags": ["NIGHTWIRE{h1dd3n_1n_pl41n_s1ght}"]},
    {"name": "Stage 3 - Backdoor Portal", "category": "Web Security", "description": "Target: http://localhost:8081/search.php?q=", "value": 200, "flags": ["NIGHTWIRE{b4ckd00r_p0rt4l_sqli_m4st3r}"]},
    {"name": "Stage 4 - Recovered Backups", "category": "Cryptography", "description": "Target: http://localhost:8084", "value": 200, "flags": ["NIGHTWIRE{weak_rsa_factored}", "NIGHTWIRE{crypto_backup_recovered}"]},
    {"name": "Stage 5 - Packet Trail", "category": "Network Forensics", "description": "Target: http://localhost:8085", "value": 300, "flags": ["NIGHTWIRE{packet_trail_complete}"]},
    {"name": "Stage 6 - Root of Nightwire", "category": "Linux Security (Capstone)", "description": "Connect via VirtualBox VM", "value": 400, "flags": ["NIGHTWIRE{r00t_0f_n1ghtw1r3_c4pst0n3}"]},
]

def get_existing():
    r = requests.get(f"{BASE_URL}/api/v1/challenges?view=admin", headers=HEADERS)
    return {c["name"] for c in r.json()["data"]} if r.ok else set()

def create_challenge(chal):
    payload = {"name": chal["name"], "category": chal["category"], "description": chal["description"], "value": chal["value"], "state": "visible", "type": "standard"}
    r = requests.post(f"{BASE_URL}/api/v1/challenges", headers=HEADERS, json=payload)
    if not r.ok:
        print(f"✗ Failed to create {chal['name']}: {r.text}")
        return None
    chal_id = r.json()["data"]["id"]
    for flag in chal["flags"]:
        requests.post(f"{BASE_URL}/api/v1/flags", headers=HEADERS, json={"challenge_id": chal_id, "content": flag, "type": "static"})
    return chal_id

existing = get_existing()
for chal in CHALLENGES:
    if chal["name"] in existing:
        print(f"SKIP: {chal['name']}")
    else:
        chal_id = create_challenge(chal)
        print(f"CREATED [{chal_id}]: {chal['name']}")

print("\n✓ Done! Refresh http://localhost:8000/challenges")
