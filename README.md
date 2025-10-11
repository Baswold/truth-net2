# 🌐 Truth Net - The Internet of Verified Knowledge

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/Platform-Cross%20Platform-blue" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

> **"In a world drowning in misinformation, Truth Net emerges as a beacon of verified knowledge, where every fact is scrutinized, every source is validated, and every voice contributes to collective wisdom."**

---

## 📋 Table of Contents

- [✨ What is Truth Net?](#-what-is-truth-net)
- [🚀 Key Features](#-key-features)
- [🏗️ Architecture](#️-architecture)
- [🛠️ Quick Start](#️-quick-start)
- [📁 Project Structure](#-project-structure)
- [🔧 Development](#-development)
- [🚢 Deployment](#-deployment)
- [👥 Contributing](#-contributing)
- [📜 License](#-license)

---

## ✨ What is Truth Net?

**Truth Net** is a revolutionary platform that reimagines how we consume and share information online. Born from the urgent need for a **truth-centered internet alternative**, it creates a curated ecosystem where:

- ✅ **Every piece of content is fact-checked** by dual AI systems and community verification
- 🛡️ **Misinformation is actively prevented** through transparent moderation processes
- 👥 **Community governance** ensures accountability and trust
- 🌐 **Your own "internet"** - a private, verified network you control

### 🎯 Mission Statement

> "To establish a corner of the digital world that puts truth at its center, where scams and falsehoods are systematically eliminated, and genuine knowledge flourishes through collective verification and accountability."

---

## 🚀 Key Features

### 🔐 **Secure Authentication**
- Email/username/password registration
- JWT-based secure sessions
- Role-based access control (Member, Curator, Admin)

### 📚 **Content Management**
- **Site Builder**: WYSIWYG editor with TipTap integration
- **Dynamic Layouts**: Flexible block-based content system
- **Version Control**: Full revision history with rollback capabilities
- **Rich Media Support**: Images, documents, embedded content

### 🤖 **Advanced Fact-Checking**
- **Dual-AI Verification**: Two independent AI systems cross-validate claims
- **Web Search Integration**: Real-time evidence gathering from trusted sources
- **Community Validation**: Human curators provide final oversight
- **Trust Scoring**: Dynamic scoring based on verification history

### 👥 **Social Features**
- **Discussion Threads**: Nested conversations around content
- **Reaction System**: Verified, helpful, disputed classifications
- **Member Profiles**: Trust scores, contribution history, specializations
- **Follow System**: Connect with verified experts and contributors

### 🔍 **Powerful Search**
- **Full-Text Search**: Across all sites and content
- **Advanced Filters**: By trust score, topic, author, date
- **Semantic Search**: Understanding context and intent
- **Instant Results**: Real-time search with highlighting

### ⚙️ **Extensive Customization**
- **Feature Toggles**: 10+ optional features you can enable/disable
- **Theme System**: Multiple visual themes (Clarity, Midnight, Sage)
- **Parental Controls**: Content filtering and age-appropriate restrictions
- **Reading Modes**: Distraction-free, audio narration, annotation layers

### 📱 **Cross-Platform Desktop App**
- **Native Performance**: Built with Tauri (Rust + WebView)
- **Offline Support**: Cached content for offline reading
- **Auto-Updates**: Seamless updates without interruption
- **System Integration**: Notifications, shortcuts, native menus

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Truth Net Platform                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Frontend   │  │   Backend   │  │  Services   │              │
│  │   (React)   │◄►│  (FastAPI)  │◄►│             │              │
│  │             │  │             │  │  • Search   │              │
│  │ • Desktop   │  │ • Auth      │  │  • AI Check │              │
│  │ • Web UI    │  │ • API       │  │  • Storage  │              │
│  └─────────────┘  │ • Database  │  │  • Cache    │              │
│                   └─────────────┘  └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ PostgreSQL  │  │   Redis     │  │ MeiliSearch │              │
│  │             │  │             │  │             │              │
│  │ • Content   │  │ • Sessions  │  │ • Full-Text │              │
│  │ • Users     │  │ • Cache     │  │ • Search    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### 🛠️ **Technology Stack**

**Backend:**
- **FastAPI** - High-performance async web framework
- **SQLAlchemy** - ORM with comprehensive model relationships
- **PostgreSQL** - Robust relational database
- **Redis** - Caching and session management
- **MeiliSearch** - Advanced search capabilities

**Frontend:**
- **React 18** - Modern component-based UI
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **TanStack Query** - Server state management

**Desktop:**
- **Tauri** - Cross-platform desktop framework
- **Rust** - High-performance system integration

**DevOps:**
- **Docker Compose** - Complete development environment
- **Poetry** - Python dependency management
- **Alembic** - Database migrations

---

## 🛠️ Quick Start

### 📋 **Prerequisites**

- **Docker & Docker Compose** (for services)
- **Python 3.11+** (for backend development)
- **Node.js 18+** (for frontend development)
- **Rust** (for Tauri desktop app)

### 🚀 **One-Command Setup**

```bash
# 1. Clone the repository
git clone <repository-url>
cd truth-net

# 2. Start all services
cd server && docker compose up -d

# 3. Set up the backend
poetry install
cp .env.example .env  # Edit with your settings
poetry run alembic upgrade head

# 4. Create your admin account
python scripts/create_admin.py

# 5. Load demo content
python scripts/load_demo_content.py

# 6. Start the API server
poetry run uvicorn app.main:app --reload

# 7. Set up the desktop app (new terminal)
cd ../client
npm install
npm run tauri dev
```

**🎉 Access your Truth Net:**
- **Server API**: http://localhost:8000
- **Desktop App**: Launches automatically
- **Site Builder**: http://localhost:8000/site-builder

### 🔑 **First Steps**

1. **Create Admin Account**: Run the setup script and follow prompts
2. **Explore Demo Sites**: Three sample sites are pre-loaded
3. **Customize Settings**: Use the Settings panel in the desktop app
4. **Start Creating**: Use the Site Builder to add your own content

---

## 📁 Project Structure

```
truth-net/
├── 📁 server/                 # Backend API (FastAPI)
│   ├── 📁 app/
│   │   ├── 📁 auth/          # Authentication & JWT
│   │   ├── 📁 models/        # Database models
│   │   ├── 📁 routes/        # API endpoints
│   │   ├── 📁 services/      # Business logic
│   │   ├── 📁 tasks/         # Async workers
│   │   └── 📁 site_builder/  # WYSIWYG editor
│   ├── 📁 scripts/           # Setup & utilities
│   ├── 📁 alembic/          # Database migrations
│   └── 📁 tests/            # Test suite
│
├── 📁 client/                # Desktop application
│   ├── 📁 src/
│   │   ├── 📁 pages/        # React components
│   │   ├── 📁 components/   # Reusable UI
│   │   └── 📁 services/     # API clients
│   ├── 📁 src-tauri/        # Rust desktop backend
│   └── 📁 public/           # Static assets
│
├── 📁 docs/                  # Documentation
│   ├── 📁 architecture.md   # Technical docs
│   ├── 📁 demo-content/     # Sample sites
│   └── 📁 api/              # API documentation
│
└── 📁 .github/              # CI/CD workflows
```

---

## 🔧 Development

### 🖥️ **Backend Development**

```bash
cd server

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Lint code
poetry run ruff check .

# Format code
poetry run black .

# Run with auto-reload
poetry run uvicorn app.main:app --reload
```

### 💻 **Frontend Development**

```bash
cd client

# Install dependencies
npm install

# Run development server (web)
npm run dev

# Run desktop app
npm run tauri dev

# Build for production
npm run build && npm run tauri build
```

### 🗄️ **Database Management**

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1
```

### 🧪 **Testing**

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test file
poetry run pytest tests/test_auth.py
```

---

## 🚢 Deployment

### 🐳 **Docker Deployment**

```bash
# Build and run with Docker Compose
docker compose up -d

# View logs
docker compose logs -f

# Update containers
docker compose pull && docker compose up -d
```

### ☁️ **Cloud Deployment**

**Recommended Stack:**
- **Compute**: Railway, Render, or DigitalOcean App Platform
- **Database**: Supabase (PostgreSQL) or AWS RDS
- **Search**: MeiliSearch Cloud or self-hosted
- **Storage**: AWS S3 or CloudFlare R2
- **CDN**: CloudFlare for static assets

**Environment Variables:**
```bash
TRUTHNET_ENVIRONMENT=production
TRUTHNET_DATABASE_URL=postgresql://...
TRUTHNET_REDIS_URL=redis://...
TRUTHNET_SEARCH_URL=https://...
TRUTHNET_JWT_SECRET=your-secret-key
```

### 📦 **Desktop App Distribution**

```bash
# Build for all platforms
npm run tauri build -- --target all

# Build for specific platform
npm run tauri build -- --target x86_64-apple-darwin  # macOS Intel
npm run tauri build -- --target aarch64-apple-darwin # macOS Apple Silicon
npm run tauri build -- --target x86_64-pc-windows-msvc # Windows
npm run tauri build -- --target x86_64-unknown-linux-gnu # Linux
```

---

## 👥 Contributing

We welcome contributions from the community! Here's how you can help:

### 🚀 **Getting Started**

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### 📝 **Guidelines**

- **Code Style**: Follow PEP 8 for Python, ESLint for JavaScript/TypeScript
- **Tests**: Add tests for new features (aim for >80% coverage)
- **Documentation**: Update docs for API changes and new features
- **Security**: Be mindful of data validation and authentication
- **Performance**: Consider the impact on large-scale usage

### 🔍 **Areas for Contribution**

- **AI Integration**: Enhance fact-checking with better AI models
- **Mobile App**: React Native companion app
- **Browser Extension**: Chrome/Firefox extension for web content
- **Internationalization**: Multi-language support
- **Accessibility**: WCAG compliance improvements
- **Performance**: Caching strategies and optimization

### 🐛 **Reporting Issues**

- **Bug Reports**: Use the GitHub issue tracker with reproduction steps
- **Feature Requests**: Create issues with detailed specifications
- **Security Issues**: Email security@truthnet.dev directly

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Inspiration**: The original letter calling for a truth-centered web platform
- **Community**: All contributors and believers in verified information
- **Open Source**: The amazing ecosystem that makes this possible

---

<div align="center">

**Made with ❤️ for a more truthful internet**

[⭐ Star us on GitHub](https://github.com/truthnet/platform) • [🐛 Report Issues](https://github.com/truthnet/platform/issues) • [💬 Join Discussion](https://github.com/truthnet/platform/discussions)

</div>
