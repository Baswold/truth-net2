# Truth Net Desktop Client

Cross-platform desktop application built with Tauri and React.

## Features

- **Secure Authentication**: JWT-based auth with token refresh
- **Content Discovery**: Browse verified sites and pages
- **Search**: Full-text search with MeiliSearch integration
- **Social Features**: Posts, threads, and community discussions
- **Offline Support**: Cached content for offline reading

## Quick Start

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Build for production
npm run build
```

## Generating API Client

The frontend uses a generated TypeScript client from the OpenAPI spec:

```bash
# Start the backend server first
cd ../server
poetry run uvicorn app.main:app --reload

# In another terminal, generate the client
cd ../client
npm run generate-client
```

This will fetch the OpenAPI schema from `http://localhost:8000/openapi.json` and generate TypeScript types and API client code in `src/api/generated/`.

## Project Structure

```
client/
├── src/
│   ├── api/          # API client and types
│   ├── components/   # Reusable UI components
│   ├── pages/        # Page components
│   ├── hooks/        # Custom React hooks
│   ├── store/        # Zustand state management
│   └── utils/        # Utility functions
├── src-tauri/        # Rust/Tauri backend
└── public/           # Static assets
```

## Development

- **React 18**: Modern component-based UI
- **TypeScript**: Type-safe development
- **TanStack Query**: Server state management with caching
- **Zustand**: Client state management
- **Tauri**: Cross-platform desktop framework

## Building

```bash
# Build desktop app for current platform
npm run tauri build

# Build for specific platform
npm run tauri build -- --target <target>
```

Supported targets:
- `x86_64-apple-darwin` - macOS Intel
- `aarch64-apple-darwin` - macOS Apple Silicon
- `x86_64-pc-windows-msvc` - Windows
- `x86_64-unknown-linux-gnu` - Linux
