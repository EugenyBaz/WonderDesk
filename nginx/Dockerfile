FROM nginx:1.25-alpine

# Удаляем дефолтный конфиг
RUN rm -f /etc/nginx/conf.d/default.conf

# Копируем основной nginx.conf (глобальный)
COPY nginx.conf /etc/nginx/nginx.conf

# Копируем server-конфиги
COPY conf.d/ /etc/nginx/conf.d/

# Папка для certbot
RUN mkdir -p /var/www/certbot