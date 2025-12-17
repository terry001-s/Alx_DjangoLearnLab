#!/bin/bash

# Exit on error
set -e

echo "🛠️ Setting up production server..."

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and pip
sudo apt-get install -y python3-pip python3-dev python3-venv

# Install PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib libpq-dev

# Install Nginx
sudo apt-get install -y nginx

# Install Gunicorn
pip3 install gunicorn

# Create PostgreSQL database and user
sudo -u postgres psql -c "CREATE DATABASE social_media_db;"
sudo -u postgres psql -c "CREATE USER social_media_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "ALTER ROLE social_media_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE social_media_user SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE social_media_user SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE social_media_db TO social_media_user;"

# Create systemd service for Gunicorn
sudo tee /etc/systemd/system/gunicorn.service << EOF
[Unit]
Description=gunicorn daemon for social media API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/social_media_api
ExecStart=/usr/local/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/social_media_api/social_media_api.sock social_media_api.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
sudo tee /etc/nginx/sites-available/social_media_api << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/social_media_api;
    }
    
    location /media/ {
        root /var/www/social_media_api;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/social_media_api/social_media_api.sock;
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/social_media_api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

echo "✅ Server setup completed!"