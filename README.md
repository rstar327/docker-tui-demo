# 🐳 Docker TUI Web

A modern web-based interface for managing Docker containers and images remotely.

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

## 🌐 Live Demo

**Frontend**: [https://docker-tui.vercel.app](https://docker-tui.vercel.app)

**Admin Panel**: [https://docker-tui-admin-panel.vercel.app](https://docker-tui-admin-panel.vercel.app)

**API Documentation**: [https://docker-tui.onrender.com/docs](https://docker-tui.onrender.com/docs)

## ✨ Features

- 🖥️ **Web-based Interface** - Manage Docker containers from anywhere
- 🤖 **Agent Architecture** - Sync local Docker to cloud backend
- 📊 **Real-time Updates** - See container status changes instantly
- 🎮 **Container Management** - Start, stop, restart, and delete containers
- 🖼️ **Image Management** - Pull and manage Docker images
- 👥 **Multi-user Support** - Each user manages their own containers
- 🔐 **Secure Authentication** - JWT-based user authentication
- 📱 **Responsive Design** - Works on desktop and mobile

## 🏗️ Architecture

```
┌──────────────────┐     ┌────────────────┐     ┌──────────────┐
│  Local Machine   │     │  Backend       │     │  Frontend    │
│  - Docker        │────▶│  - FastAPI     │◀────│  - Web UI    │
│  - Agent         │     │  - PostgreSQL  │     │  - Vercel    │
└──────────────────┘     └────────────────┘     └──────────────┘
```

**How it works:**
1. **Local Agent** runs on your machine and syncs Docker data
2. **Backend** stores data and manages users (hosted on Render)
3. **Frontend** displays your containers in a beautiful web UI (hosted on Vercel)

## 🚀 Quick Start

### 1. Register an Account

Visit [docker-tui.vercel.app](https://docker-tui.vercel.app) and create an account.

### 2. Install Agent

```bash
git clone https://github.com/rstar327/docker-tui.git
cd docker-tui/agent
pip install -r requirements.txt
```

### 3. Run Agent

Get your agent token from Settings tab in the web UI, then:

```bash
python agent.py --backend https://docker-tui.onrender.com --token YOUR_TOKEN
```

### 4. Manage Containers

Your local Docker containers will appear in the web interface within seconds!

## 📸 Screenshots

### Container Management
![Containers View](https://via.placeholder.com/800x400/1a1a1a/4ade80?text=Container+Management+View)

### Settings & Agent Registration
![Settings View](https://via.placeholder.com/800x400/1a1a1a/60a5fa?text=Settings+%26+Agent+Registration)

### Admin Panel
![Admin Panel](https://via.placeholder.com/800x400/1a1a1a/f59e0b?text=Admin+Panel+-+User+Management)

## 🛠️ Tech Stack

**Frontend:**
- HTML5, CSS3 (Tailwind CSS)
- Vanilla JavaScript
- Deployed on Vercel

**Backend:**
- Python 3.11
- FastAPI
- SQLAlchemy (async)
- PostgreSQL (Neon)
- Deployed on Render

**Agent:**
- Python Docker SDK
- Requests library
- Runs on your local machine

## 🌟 Key Capabilities

### For Users
- ✅ Manage Docker containers from anywhere
- ✅ No need to expose Docker socket to internet
- ✅ Secure token-based authentication
- ✅ Works behind firewalls and NAT
- ✅ Multiple machines support (multiple agents)

### For Admins
- ✅ User approval workflow
- ✅ Role-based access control
- ✅ Agent session management
- ✅ Audit logging

## 🔐 Security

- **No Docker socket exposure** - Agent connects outbound only
- **JWT authentication** - Secure token-based auth
- **HTTPS everywhere** - All connections encrypted
- **User isolation** - Each user sees only their containers
- **Admin approval** - Optional user approval workflow

## 📊 System Requirements

**For Agent:**
- Python 3.8 or higher
- Docker installed and running
- Internet connection

**For Web Access:**
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection

## 💡 Use Cases

- **Remote Docker Management** - Manage Docker on remote servers
- **Development Teams** - Share Docker environments
- **Learning Docker** - Visual interface for Docker beginners
- **Multi-machine Management** - Monitor Docker across multiple machines
- **Cloud-free Docker GUI** - Self-hosted Docker management

## 🤝 Contributing

This project is open source. Contributions are welcome!

## 📝 License

MIT License - feel free to use this project for any purpose.

## 🔗 Links

- **Live Application**: [docker-tui.vercel.app](https://docker-tui.vercel.app)
- **Source Code**: [github.com/rstar327/docker-tui](https://github.com/rstar327/docker-tui)
- **API Docs**: [docker-tui.onrender.com/docs](https://docker-tui.onrender.com/docs)

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ using FastAPI and Vercel**
