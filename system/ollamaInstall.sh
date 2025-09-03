# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Add your user to the ollama group (may require logout/login)
sudo usermod -aG ollama $USER

# Start the Ollama service
sudo systemctl start ollama

# Enable Ollama to start on boot
sudo systemctl enable ollama

# Verify installation
ollama --version