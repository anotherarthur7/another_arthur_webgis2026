#!/bin/bash
# setup.sh - Quick setup script for new development machines

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Installing system dependencies...${NC}"
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential git
sudo apt install -y postgresql postgresql-contrib postgresql-server-dev-all postgis
sudo apt install -y gdal-bin libgdal-dev libpq-dev libproj-dev 

echo -e "${GREEN}Starting PostgreSQL service...${NC}"
sudo systemctl start postgresql
sudo systemctl enable postgresql

echo -e "${GREEN}Setting up PostgreSQL user and database...${NC}"
sudo -u postgres psql -c "CREATE USER cim_user WITH PASSWORD 'cim_password';"
sudo -u postgres psql -c "CREATE DATABASE cim_db OWNER cim_user;"
sudo -u postgres psql -c "ALTER USER cim_user CREATEDB;"

echo -e "${GREEN}Creating Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

echo -e "${GREEN}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}Creating static directory...${NC}"
mkdir -p static

echo -e "${GREEN}Running migrations...${NC}"
python manage.py migrate

echo -e "${GREEN}Setup complete!${NC}"
echo -e "To start the server: source venv/bin/activate && python manage.py runserver"