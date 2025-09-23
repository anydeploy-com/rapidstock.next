# RapidStock.next

A modern inventory management system built with a microservices architecture.

## Project Structure

This monorepo contains three main components:

### 🔧 `/api` - FastAPI Backend
- **Framework**: FastAPI 0.117.1 (latest)
- **Purpose**: RESTful API backend for inventory management
- **Port**: 8000
- **Features**: 
  - Modern async Python API
  - Automatic API documentation with Swagger UI
  - High-performance JSON API

#### Quick Start:
```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 👨‍💼 `/admin` - Vue.js 3 Admin Panel
- **Framework**: Vue.js 3 with Vite
- **Purpose**: Administrative interface for managing inventory
- **Port**: 3001
- **Features**:
  - Modern Vue.js 3 with Options API
  - Fast development with Vite
  - Responsive admin dashboard

#### Quick Start:
```bash
cd admin
npm install
npm run dev
```

### 🌐 `/frontend` - Nuxt 4 Frontend
- **Framework**: Nuxt 4.1.2 (latest)
- **Purpose**: Customer-facing web application
- **Port**: 3000
- **Features**:
  - Server-side rendering (SSR)
  - Modern Vue.js 3 with Nuxt 4
  - SEO-optimized

#### Quick Start:
```bash
cd frontend
npm install
npm run dev
```

## Development Workflow

1. **API First**: Start the FastAPI backend for data services
2. **Admin Panel**: Use the Vue.js admin panel for content management
3. **Frontend**: The Nuxt frontend consumes the API for public-facing features

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Admin Panel   │    │   API Backend   │
│   (Nuxt 4)      │────│   (Vue.js 3)    │────│   (FastAPI)     │
│   Port: 3000    │    │   Port: 3001    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Technology Stack

- **Backend**: Python 3.12 + FastAPI 0.117.1
- **Admin**: Vue.js 3 + Vite
- **Frontend**: Nuxt 4.1.2 + Vue.js 3
- **Development**: Node.js 20.19.5, npm 10.8.2