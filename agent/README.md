# Docker TUI Agent

The Docker TUI Agent runs on your local machine to sync your Docker containers and images with the remote backend, allowing you to manage them through the web interface.

## 🎯 What It Does

- **Syncs** your local Docker containers and images to the backend every 5 seconds
- **Executes** actions (start/stop/restart/delete) requested from the web interface
- **Reports** results back to the backend
- Runs continuously in the background

## 📋 Prerequisites

- Python 3.8 or higher
- Docker installed and running on your local machine
- Account on the Docker TUI web application
- Agent token (obtained from the web interface)

## 🚀 Installation

### 1. Install Dependencies

```bash
cd agent
pip install -r requirements.txt
```

Or install globally:

```bash
pip install docker requests
```

### 2. Get Your Agent Token

1. Go to the Docker TUI web application
2. Login with your account
3. Navigate to **Settings** → **Agent Registration**
4. Click **"Register New Agent"**
5. Copy the generated agent token

## 🏃 Running the Agent

### Basic Usage

```bash
python agent.py --backend <BACKEND_URL> --token <YOUR_TOKEN>
```

### Example

```bash
# For local backend
python agent.py --backend http://localhost:8000 --token eyJhbGc...

# For production backend (Render)
python agent.py --backend https://docker-tui-backend.onrender.com --token eyJhbGc...
```

### Options

- `--backend` (required): Backend API URL
- `--token` (required): Your agent authentication token
- `--interval` (optional): Sync interval in seconds (default: 5)

### Custom Sync Interval

```bash
# Sync every 10 seconds instead of 5
python agent.py --backend https://your-backend.com --token YOUR_TOKEN --interval 10
```

## 🔄 Running as a Background Service

### Linux/macOS (systemd)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/docker-tui-agent.service
```

Add:

```ini
[Unit]
Description=Docker TUI Agent
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/docker-tui/agent
ExecStart=/usr/bin/python3 /path/to/docker-tui/agent/agent.py --backend https://your-backend.com --token YOUR_TOKEN
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable docker-tui-agent
sudo systemctl start docker-tui-agent
sudo systemctl status docker-tui-agent
```

View logs:

```bash
sudo journalctl -u docker-tui-agent -f
```

### macOS (launchd)

Create a plist file:

```bash
nano ~/Library/LaunchAgents/com.dockertui.agent.plist
```

Add:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dockertui.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/docker-tui/agent/agent.py</string>
        <string>--backend</string>
        <string>https://your-backend.com</string>
        <string>--token</string>
        <string>YOUR_TOKEN</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/docker-tui-agent.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/docker-tui-agent-error.log</string>
</dict>
</plist>
```

Load and start:

```bash
launchctl load ~/Library/LaunchAgents/com.dockertui.agent.plist
launchctl start com.dockertui.agent
```

View logs:

```bash
tail -f /tmp/docker-tui-agent.log
```

### Windows (Task Scheduler or NSSM)

**Option 1: Using NSSM (Non-Sucking Service Manager)**

1. Download NSSM from https://nssm.cc/download
2. Install the service:

```cmd
nssm install DockerTUIAgent "C:\Python39\python.exe" "C:\path\to\docker-tui\agent\agent.py --backend https://your-backend.com --token YOUR_TOKEN"
nssm start DockerTUIAgent
```

**Option 2: Task Scheduler**

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start a program
5. Program: `python.exe`
6. Arguments: `C:\path\to\agent.py --backend https://your-backend.com --token YOUR_TOKEN`

## 📊 Output

When running, the agent logs:

```
2026-02-02 10:30:00 - __main__ - INFO - ============================================================
2026-02-02 10:30:00 - __main__ - INFO - Docker TUI Agent Started
2026-02-02 10:30:00 - __main__ - INFO - Backend: https://docker-tui-backend.onrender.com
2026-02-02 10:30:00 - __main__ - INFO - Sync Interval: 5s
2026-02-02 10:30:00 - __main__ - INFO - ============================================================
2026-02-02 10:30:00 - __main__ - INFO - ✓ Connected to Docker
2026-02-02 10:30:01 - __main__ - INFO - ✓ Synced: 5 containers, 12 images
2026-02-02 10:30:15 - __main__ - INFO - → Executing: start container abc123
2026-02-02 10:30:15 - __main__ - INFO - ✓ Action completed: Container started
2026-02-02 10:30:16 - __main__ - INFO - ✓ Synced: 5 containers, 12 images
```

## 🔧 Troubleshooting

### "Failed to connect to Docker"

- Make sure Docker is running: `docker ps`
- Check Docker socket permissions: `ls -l /var/run/docker.sock`
- On Linux, add user to docker group: `sudo usermod -aG docker $USER`

### "Sync failed: 401"

- Your agent token is invalid or expired
- Register a new agent token from the web interface

### "Network error during sync"

- Check your backend URL is correct
- Ensure you have internet connectivity
- Verify the backend is running: visit the URL in a browser

### "Container not found" errors

- The container may have been deleted locally
- Refresh will happen on next sync cycle

## 🔒 Security

- **Token Storage**: Keep your agent token secure. It provides full access to your Docker environment.
- **HTTPS**: Always use HTTPS for production backends
- **Permissions**: The agent needs Docker socket access (same as `docker` CLI)

## 🛑 Stopping the Agent

### Running in Terminal

Press `Ctrl+C` to stop gracefully.

### Running as Service

```bash
# Linux
sudo systemctl stop docker-tui-agent

# macOS
launchctl stop com.dockertui.agent

# Windows (NSSM)
nssm stop DockerTUIAgent
```

## 📝 Environment Variables (Alternative)

Instead of command-line arguments, you can use environment variables:

```bash
export DOCKER_TUI_BACKEND=https://your-backend.com
export DOCKER_TUI_TOKEN=YOUR_TOKEN
export DOCKER_TUI_INTERVAL=5

python agent.py
```

## 🔄 Updates

To update the agent:

```bash
cd /path/to/docker-tui
git pull origin master
sudo systemctl restart docker-tui-agent  # if running as service
```

## 💡 Tips

- Use a longer `--interval` (e.g., 10-30 seconds) to reduce API calls and bandwidth
- The agent automatically syncs after executing any action
- Multiple machines can run agents with the same account (each needs its own token)
- Check agent status on the web interface under **Settings** → **Active Agents**

## 🆘 Need Help?

- Check logs for error messages
- Ensure Docker and backend are both accessible
- Verify your token is valid
- Report issues at: https://github.com/rstar327/docker-tui/issues
