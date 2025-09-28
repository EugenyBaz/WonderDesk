FROM nginx:1.25-alpine

# Удаляем дефолтные конфиги, чтобы не мешали
RUN rm -f /etc/nginx/conf.d/default.conf

# Копируем наш конфиг nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Копируем папку для certbot (чтобы Let’s Encrypt мог проверить домен)
RUN mkdir -p /var/www/certbot