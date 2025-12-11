#!/bin/bash

# GCE Startup Script for SQL Generator Backend
# This script installs Docker, Ollama, and runs the application.

# 1. Update and Install Dependencies
echo "Updating system and installing dependencies..."
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common gnupg lsb-release git

# 2. Install Docker
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    sudo systemctl enable docker
    sudo systemctl start docker
else
    echo "Docker already installed."
fi

# 3. Install Ollama
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama already installed."
fi

# 4. Start Ollama Service
# We need to ensure Ollama listens on all interfaces or is accessible. 
# By default, it listens on localhost:11434.
# For simplicity in this setup, since we are running the app in a container, we can run the container with --network host to access localhost 
# OR configure Ollama to listen on 0.0.0.0.
echo "Configuring Ollama..."
sudo systemctl stop ollama
# Create systemd override to listen on 0.0.0.0 if not already present
sudo mkdir -p /etc/systemd/system/ollama.service.d
echo "[Service]
Environment=\"OLLAMA_HOST=0.0.0.0:11434\"" | sudo tee /etc/systemd/system/ollama.service.d/override.conf

sudo systemctl daemon-reload
sudo systemctl start ollama

# Wait for Ollama to start
sleep 5

# 5. Pull the Llama 3.2 model
echo "Pulling Llama 3.2 model..."
ollama pull llama3.2

# 6. Setup Application
APP_DIR="/opt/sql-backend"

# NOTE: You need to decide how code gets here. 
# Option A: Git Clone (Uncomment and fill details)
# echo "Cloning repository..."
# sudo git clone https://github.com/winssoftdev-spec/SQL_Cloud.git $APP_DIR

# Option B: Assume files are uploaded via GCE Metadata or SCP.
# For this script, we'll assume the user might manually place files or use another method. 
# IF testing manually, just copy files to $APP_DIR.
# But to make this script robust for a demo, let's create the directory.
sudo mkdir -p $APP_DIR

# ------------------------------------------------------------------
# IMPORTANT: 
# Since I cannot know your Git repo URL, I am assuming you will 
# either upload the files or edit this script to clone your repo.
# 
# For now, I will assume the files are already in $APP_DIR or 
# you will run this script AFTER copying files.
# 
# IF YOU WANT THE SCRIPT TO RUN AUTOMATICALLY ON BOOT AND PULL CODE:
# Uncomment the git clone section above.
# ------------------------------------------------------------------

cd $APP_DIR

# Check if Dockerfile exists before building
if [ -f "Dockerfile" ]; then
    echo "Building Docker image..."
    sudo docker build -t sql-backend .

    echo "Running Application..."
    # Running with --network host so it can access Ollama on localhost:11434 easily
    # (Since we also bound Ollama to 0.0.0.0, we could use bridge networking too, but host is simplest here)
    sudo docker run -d \
        --name sql-backend-container \
        --network host \
        --restart always \
        sql-backend
else
    echo "Dockerfile not found in $APP_DIR. Please ensure code is deployed."
fi
