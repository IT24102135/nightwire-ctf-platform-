$challenges = @(
    @{name="Stage 1: OSINT"; desc="Open Source Intelligence - Find hidden information"; pts=100; flag="flag{osint_recon}"; cat="OSINT"},
    @{name="Stage 2: Steganography"; desc="Extract hidden message from image"; pts=150; flag="flag{stego_hidden}"; cat="Steganography"},
    @{name="Stage 3: Database"; desc="SQL Injection and database exploitation"; pts=200; flag="flag{sql_pwned}"; cat="Database"},
    @{name="Stage 4: Cryptography"; desc="Decrypt the message"; pts=250; flag="flag{crypto_solved}"; cat="Cryptography"},
    @{name="Stage 5: Forensics"; desc="Digital forensics and data recovery"; pts=300; flag="flag{forensics_found}"; cat="Forensics"},
    @{name="Stage 6: Final Challenge"; desc="Combine all previous skills"; pts=500; flag="flag{nightwire_complete}"; cat="Final"}
)

Write-Host "Creating challenges..." -ForegroundColor Cyan

foreach ($challenge in $challenges) {
    $sql = "INSERT IGNORE INTO challenges (name, description, value, category, type, state, max_attempts) VALUES ('$($challenge.name)', '$($challenge.desc)', $($challenge.pts), '$($challenge.cat)', 'standard', 'visible', 0);"
    
    docker exec ctfd-db-1 mysql -u ctfd -pctfd -D ctfd -e $sql
    
    $idQuery = "SELECT id FROM challenges WHERE name = '$($challenge.name)' LIMIT 1;"
    $challengeId = docker exec ctfd-db-1 mysql -u ctfd -pctfd -D ctfd -N -e $idQuery
    
    if ($challengeId) {
        $flagSql = "INSERT IGNORE INTO flags (challenge_id, content, type, data) VALUES ($challengeId, '$($challenge.flag)', 'static', '');"
        docker exec ctfd-db-1 mysql -u ctfd -pctfd -D ctfd -e $flagSql
        
        $hint1Sql = "INSERT IGNORE INTO hints (challenge_id, content, cost, requirements) VALUES ($challengeId, 'Hint 1: Look for patterns', 5, NULL);"
        $hint2Sql = "INSERT IGNORE INTO hints (challenge_id, content, cost, requirements) VALUES ($challengeId, 'Hint 2: Check the source', 5, NULL);"
        
        docker exec ctfd-db-1 mysql -u ctfd -pctfd -D ctfd -e $hint1Sql
        docker exec ctfd-db-1 mysql -u ctfd -pctfd -D ctfd -e $hint2Sql
        
        Write-Host "✓ $($challenge.name) - ID: $challengeId" -ForegroundColor Green
    }
}

Write-Host "`n✅ Done! Refresh http://localhost:8000/admin/challenges`n" -ForegroundColor Green
