# Docker Desktop 500 Internal Server Error Troubleshooting

## Current Error:
```
request returned 500 Internal Server Error for API route and version
http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.52/version
```

## Problem:
Docker Desktop API is not responding correctly. This affects:
1. Docker Compose builds
2. Minikube Docker driver
3. All Docker operations from Windows terminal

## Solutions (Try in Order):

### 1. Full Docker Desktop Restart
```powershell
# 1. Exit Docker Desktop completely
#    - Right-click Docker tray icon → Exit
#    - Wait 30 seconds

# 2. Open PowerShell as Administrator
# 3. Stop Docker services
net stop com.docker.service
net stop Docker

# 4. Restart Docker Desktop
#    - Start Docker Desktop app
#    - Wait for green indicator in tray
```

### 2. Reset Docker Desktop to Factory Defaults
If restart doesn't work:
1. Open Docker Desktop
2. Go to **Troubleshoot** → **Reset to factory defaults**
3. Click **Reset**
4. Restart Docker Desktop

### 3. Repair Docker Desktop Installation
1. Go to Windows **Settings** → **Apps** → **Apps & features**
2. Find **Docker Desktop**
3. Click **Modify** → **Repair**
4. Restart computer

### 4. Check WSL Integration
In PowerShell:
```powershell
# Check WSL 2 is default
wsl --set-default-version 2

# Check if Docker Desktop WSL integration is enabled
# In Docker Desktop: Settings → Resources → WSL Integration
# Make sure your Ubuntu distribution is checked
```

### 5. Test Docker After Each Step
```bash
docker version
docker ps
```

## Alternative: Use Docker Engine in WSL (Fallback)
If Docker Desktop cannot be fixed:

### In WSL Terminal:
```bash
# Install Docker Engine directly in WSL
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Log out and back in
exit
# Reopen WSL terminal

# Test
docker version

# For Minikube, use 'none' driver
minikube delete
sudo minikube start --driver=none --memory=1536mb --cpus=1
```

## Priority Order:
1. **Restart Docker Desktop** (simplest)
2. **Factory Reset Docker Desktop** (if restart fails)
3. **Repair Installation** (if factory reset fails)
4. **Use Docker Engine in WSL** (fallback option)

## Notes:
- **Minikube Docker driver** requires healthy Docker
- **Docker Compose** requires healthy Docker
- **Google OAuth testing** can wait until Docker is fixed
- **Phase 4 completion** requires either Docker Desktop or Docker Engine working