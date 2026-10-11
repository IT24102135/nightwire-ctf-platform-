FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    apache2 \
    php8.2 \
    libapache2-mod-php8.2 \
    php8.2-mysqli \
    mariadb-server \
    && rm -rf /var/lib/apt/lists/*

COPY ./src/html/ /var/www/html/
COPY ./src/db/seed.sql /tmp/seed.sql
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80
CMD ["/entrypoint.sh"]
