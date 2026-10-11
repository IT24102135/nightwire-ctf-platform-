#!/usr/bin/env python3
import requests
requests.packages.urllib3.disable_warnings()

session = requests.Session()

# Create challenges via API (simplified)
BASE = "http://localhost:8000/api/v1"

challenges = [
    {"name": "Stage 1 - First Contact", "category": "OSINT", "description": "http://localhost:8082", "value": 100, "flags": ["NIGHTWIRE{f1rst_c0nt4ct_0s1nt_succ3ss}"]},
    {"name": "Stage 2 - Hidden in Plain Sight", "category": "Steganography", "description": "http://localhost:8083", "value": 100, "flags": ["NIGHTWIRE{h1dd3n_1n_pl41n_s1ght}"]},
    {"name": "Stage 3 - Backdoor Portal", "category": "Web Security", "description": "http://localhost:8081/search.php", "value": 200, "flags": ["NIGHTWIRE{b4ckd00r_p0rt4l_sqli_m4st3r}"]},
    {"name": "Stage 4 - Recovered Backups", "category": "Cryptography", "description": "http://localhost:8084", "value": 200, "flags": ["NIGHTWIRE{weak_rsa_factored}", "NIGHTWIRE{crypto_backup_recovered}"]},
    {"name": "Stage 5 - Packet Trail", "category": "Network Forensics", "description": "http://localhost:8085", "value": 300, "flags": ["NIGHTWIRE{packet_trail_complete}"]},
    {"name": "Stage 6 - Root of Nightwire", "category": "Linux Security", "description": "VirtualBox", "value": 400, "flags": ["NIGHTWIRE{r00t_0f_n1ghtw1r3_c4pst0n3}"]},
]

token = input("Paste API token: ").strip()
headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}

for c in challenges:
    r = requests.get(f"{BASE}/challenges", headers=headers)
    if any(ch["name"] == c["name"] for ch in r.json().get("data", [])):
        print(f"[✓] {c['name']} exists")
        continue
    
    r = requests.post(f"{BASE}/challenges", json={
        "name": c["name"],
        "category": c["category"],
        "description": c["description"],
        "value": c["value"],
        "state": "visible",
        "type": "standard"
    }, headers=headers)
    
    if r.ok:
        cid = r.json()["data"]["id"]
        for flag in c["flags"]:
            requests.post(f"{BASE}/flags", json={"challenge_id": cid, "content": flag, "type": "static"}, headers=headers)
        print(f"[✓] Created {c['name']}")
    else:
        print(f"[✗] Failed: {c['name']}")

print("\nDone!")
