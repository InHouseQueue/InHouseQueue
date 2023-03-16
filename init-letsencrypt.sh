#!/bin/bash

domains=(dozzle.inhousequeue.xyz)
rsa_key_size=4096
data_path="./certbot"
email="hello@inhousequeue.xyz"
staging=0

if [ "$staging" != "0" ]; then
  staging_arg="--staging"
fi

for domain in "${domains[@]}"; do
  echo "### Creating dummy certificate for $domain..."
  path="/etc/letsencrypt/live/$domain"
  mkdir -p "$data_path/conf/live/$domain"
  docker-compose run --rm --entrypoint "\
    openssl req -x509 -nodes -newkey rsa:1024 -days 1\
      -keyout '$path/privkey.pem' \
      -out '$path/fullchain.pem' \
      -subj '/CN=localhost'" certbot
done

echo "### Starting nginx..."
docker-compose up --force-recreate -d nginx
echo "### Deleting dummy certificate for $domain..."
docker-compose run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/$domain && \
  rm -Rf /etc/letsencrypt/archive/$domain && \
  rm -Rf /etc/letsencrypt/renewal/$domain.conf" certbot

echo "### Requesting Let's Encrypt certificate for $domain..."
docker-compose run --rm --entrypoint "\
  certbot certonly --webroot -w /var/lib/letsencrypt/ \
    -d $domain \
    --email $email --rsa-key-size $rsa_key_size --agree-tos --force-renewal \
    $staging_arg" certbot

echo "### Reloading nginx..."
docker-compose exec nginx nginx -s reload
