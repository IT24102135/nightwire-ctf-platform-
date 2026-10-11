FROM nginx:alpine
COPY ./index.html /usr/share/nginx/html/index.html
COPY ./artifacts/exfil_capture.pcapng /usr/share/nginx/html/exfil_capture.pcapng
COPY ./artifacts/sslkeylog.txt /usr/share/nginx/html/sslkeylog.txt
