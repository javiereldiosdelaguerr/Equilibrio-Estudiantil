FROM nginx:alpine

# Elimina archivos por defecto de nginx
RUN rm -rf /usr/share/nginx/html/*

# Copia tu frontend al servidor nginx
COPY . /usr/share/nginx/html

# Expone el puerto 80
EXPOSE 80