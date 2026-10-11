#!/bin/bash
set -e

mkdir -p /run/mysqld
chown mysql:mysql /run/mysqld

echo "[*] Starting MariaDB..."
service mariadb start

echo "[*] Waiting for MariaDB to be ready..."
for i in $(seq 1 30); do
  if mysqladmin ping >/dev/null 2>&1; then
    echo "[+] MariaDB is up."
    break
  fi
  sleep 1
done

echo "[*] Seeding database..."
mysql -u root < /tmp/seed.sql

echo "[*] Starting Apache in foreground..."
exec apache2ctl -D FOREGROUND
