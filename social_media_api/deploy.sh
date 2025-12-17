#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting deployment..."

# Update code from repository
echo "📥 Updating code..."
git pull origin main

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Apply database migrations
echo "🗄️ Running migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Check production settings
echo "🔍 Checking production settings..."
python manage.py check_production

# Restart Gunicorn
echo "🔄 Restarting Gunicorn..."
sudo systemctl restart gunicorn

# Restart Nginx
echo "🔄 Restarting Nginx..."
sudo systemctl restart nginx

echo "✅ Deployment completed successfully!"