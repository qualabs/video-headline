#Web Build
FROM node:10 as web

RUN mkdir /code/
WORKDIR /code

COPY web/package-lock.json package-lock.json
COPY web/package.json package.json
RUN npm install

COPY web/ .
RUN npm run build

# Core Build

FROM python:3.7-slim-stretch
MAINTAINER Qualabs <support@qualabs.com>

EXPOSE 80 443
ENV PYTHONUNBUFFERED 1
ENV APP_WSGI_MODULE="video_hub.wsgi"

# Install NGINX
RUN sed -i -e 's/deb.debian.org/archive.debian.org/g' \
    -e 's|security.debian.org|archive.debian.org/|g' \
    -e '/stretch-updates/d' /etc/apt/sources.list
RUN apt-get update && apt-get install -y curl gnupg gnupg2 gnupg1 gcc
RUN curl http://nginx.org/packages/keys/nginx_signing.key | apt-key add - \
    && echo "deb http://nginx.org/packages/mainline/debian/ stretch nginx" >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y ca-certificates nginx gettext-base \
    && rm -rf /var/lib/apt/lists/*

# Replace the default Nginx config with the app config
RUN rm /etc/nginx/conf.d/default.conf
COPY conf.nginx /etc/nginx/conf.d/app.conf

# Copy the uWSGI config
COPY uwsgi.ini /etc/uwsgi/uwsgi.ini

# Copy the start_app scripts
COPY ./docker-commands/* /
RUN chmod +x /*.sh
CMD ["/start_app.sh"]

# Prepare the app
RUN mkdir /code/
WORKDIR /code/

# Install PipEnv
RUN pip3 install pipenv
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

# Install requirements
RUN pipenv install --deploy --system

# Create folders for log and media
RUN mkdir -p log media static && chown -R www-data:www-data log

# Copy the main website
COPY --from=web /code/build web/build

# Copy the css and js of the react player
# COPY --from=player /code/build/static/ player/static/player/

# Copy all source code
COPY --chown=www-data:www-data . . 

# Collect static
RUN python manage.py collectstatic --noinput && chown -R www-data:www-data /code/

COPY infrastructure/create_super_user.sh /code/
RUN chmod +x /code/create_super_user.sh