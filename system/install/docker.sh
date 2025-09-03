# Update package list
sudo apt update

# Install required dependencies
sudo apt install apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package list again
sudo apt update

# Install Docker Engine
sudo apt install docker-ce docker-ce-cli containerd.io

# Install Docker Compose (standalone version)
sudo apt install docker-compose-plugin

# user change 
sudo usermod -aG docker $USER
# Verify installation
docker --version
docker compose version