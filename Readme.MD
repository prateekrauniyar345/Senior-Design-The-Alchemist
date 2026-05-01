# 🧪 The Alchemist - AI-Powered Mineral Data Explorer

**The Alchemist** is a sophisticated full-stack AI application that transforms mineral data exploration through intelligent multi-agent workflows. It combines cutting-edge LLM technology with specialized tools to enable users to query, analyze, and visualize mineral data from the Mindat.org database in natural language.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [Project Architecture](#-project-architecture)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Multi-Agent System](#-multi-agent-system)
- [Deployment](#-deployment)
- [Development](#-development)

---

## 🎯 Overview

**The Alchemist** leverages **LangChain**, **LangGraph**, **LangSmith**, and **Azure OpenAI** to build an intelligent multi-agent system that understands natural language queries and routes them to specialized agents for mineral data collection, analysis, and visualization. The system integrates seamlessly with the Mindat.org API to provide comprehensive mineral information.

### Core Capabilities
- 🤖 **Multi-Agent Intelligence**: Supervisor-based routing architecture that intelligently delegates tasks
- 🔍 **Advanced Mineral Queries**: Query 40+ endpoints from Mindat.org API with complex filtering
- 📊 **Interactive Visualizations**: Generate Vega-Lite charts, histograms, heatmaps, and network diagrams
- 💾 **Session Management**: Persistent chat history and user profiles
- 🔐 **Secure Authentication**: OAuth and email/password via Supabase
- 📤 **Export Capabilities**: Download plots or email visualizations directly

---

## ✨ Key Features

### 1. **Multi-Agent System**
- **Supervisor Node**: Analyzes queries and routes to appropriate agents
- **General Agent**: Handles greetings, FAQs, and conversational queries
- **Geomaterial Collector**: Queries mineral properties, crystal systems, density, hardness
- **Locality Collector**: Finds mineral locations worldwide
- **Vega Plot Generator**: Creates interactive visualizations
- **Tool Integration**: Model Context Protocol (MCP) for tool management

### 2. **Authentication & Authorization**
- Supabase Auth with OAuth providers (Google, GitHub, etc.)
- Email/password authentication
- Session management with HTTP-only cookies
- Automatic user synchronization to PostgreSQL
- Role-based access control

### 3. **Data Collection & Processing**
- **Mindat API Integration**: Access to comprehensive mineral database
- **Query Parameters**: Filter by element, crystal system, hardness, density, optical properties, etc.
- **Data Profiling**: Automated schema introspection for visualization planning
- **Real-time Processing**: Instant query results with streaming capability (planned)

### 4. **Chat Interface & Session Management**
- Create, read, update, delete chat sessions
- Persistent message history with full context
- Multiple output formats: text, JSON, tables, interactive charts
- Search and filter chat history

### 5. **Advanced Visualizations**
- **Vega-Lite Integration**: Interactive, responsive charts
- **Chart Types**: Histograms, heatmaps, network graphs, scatter plots
- **Customization**: Adjust colors, aggregations, and axes
- **Export**: Download as PNG/PDF or email visualizations

### 6. **Responsive UI**
- Modern React-based interface with dark theme
- Real-time message updates with typing indicators
- Sidebar for quick navigation and chat history
- Settings modal for LLM parameter tuning
- Profile management

---

## 🛠️ Technology Stack

### Backend
| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | FastAPI | 0.119.0 |
| **Server** | Uvicorn | Latest |
| **Database** | PostgreSQL (via Supabase) | Latest |
| **LLM** | Azure OpenAI GPT-4o | Latest |
| **Agent Framework** | LangChain + LangGraph | Latest |
| **Tool Management** | FastMCP (Model Context Protocol) | Latest |
| **Monitoring** | LangSmith | Latest |
| **ORM** | SQLAlchemy | Latest |
| **Auth** | Supabase-py | Latest |

### Frontend
| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | React | 19.1.1 |
| **Build Tool** | Vite | 7.1.7 |
| **Router** | React Router DOM | 7.9.5 |
| **API Client** | Axios | Latest |
| **Authentication** | Supabase.js | Latest |
| **Visualization** | Vega-Lite + Vega-Embed | Latest |
| **UI Library** | Bootstrap 5.3.8 + React Bootstrap | Latest |
| **Icons** | Lucide React | Latest |

### DevOps & Deployment
- **Backend**: Render.com (Docker-ready)
- **Frontend**: Vercel (Optimized for Next.js/Vite)
- **Database**: Supabase PostgreSQL
- **Monitoring**: LangSmith Dashboard

---

## 🏗️ Project Architecture

### System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                   │
│         Deployed on Vercel (vercel.com)                      │
│  - Chat Interface      - Session Management                  │
│  - Visualizations      - User Authentication                 │
└────────────────┬──────────────────────────────────────────────┘
                 │ HTTPS/REST API
┌────────────────▼──────────────────────────────────────────────┐
│                 Backend (FastAPI + Python)                    │
│          Deployed on Render.com (onrender.com)               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  FastAPI Router Layer                                 │  │
│  │  - /api/agent/chat    - /api/sessions                 │  │
│  │  - /api/auth/*        - /api/mindat/*                 │  │
│  │  - /api/users/*       - /api/plots/*                  │  │
│  └────────────────┬───────────────────────────────────────┘  │
│                   │                                            │
│  ┌────────────────▼───────────────────────────────────────┐  │
│  │  LangGraph Multi-Agent Engine                         │  │
│  │  ┌──────────────────────────────────────────────────┐ │  │
│  │  │ Supervisor (Decision Router)                     │ │  │
│  │  │ Routes to: General | Geomaterial | Locality     │ │  │
│  │  │           | Plotter | Tools                      │ │  │
│  │  └──────────────────────────────────────────────────┘ │  │
│  │         │                                              │  │
│  │         ├─→ Azure OpenAI GPT-4o (LLM)                 │  │
│  │         └─→ MCP Client (Tool Execution)               │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────┬──────────────────────────────────────────────┘
                 │
        ┌────────┼────────┬──────────────┐
        │        │        │              │
   ┌────▼──┐ ┌──▼──┐ ┌───▼───┐ ┌───────▼────┐
   │Supabase│ │MCP  │ │Mindat │ │PostgreSQL  │
   │Auth    │ │Server│ │API    │ │(Supabase)  │
   └────────┘ └─────┘ └───────┘ └────────────┘
```

### Data Flow Diagram
```
User Input
    │
    ▼
React Chat Interface
    │
    ▼
POST /api/agent/chat (FastAPI)
    │
    ▼
Supervisor Agent (LangGraph)
    │
    ├─→ Text Query? → General Agent → Response
    │
    ├─→ Mineral Data? → Geomaterial Collector
    │                    │
    │                    ▼
    │                  MCP Client
    │                    │
    │                    ▼
    │                  collect_geomaterials()
    │                    │
    │                    ▼
    │                  Mindat API
    │                    │
    │                    ▼
    │                  Response to Supervisor
    │
    ├─→ Visualization? → Vega Plot Generator
    │                     │
    │                     ▼
    │                   Generate Vega Spec
    │
    ▼
Final Response (Text + Chart + Metadata)
    │
    ▼
Save to DB (Message, AgentOutput, Visualization)
    │
    ▼
Return to Frontend
    │
    ▼
Render in MessageBubble Component
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+** (Backend)
- **Node.js 18+** (Frontend)
- **PostgreSQL** (via Supabase)
- **Azure OpenAI API Key**
- **Mindat API Key**
- **Supabase Account**
- **Git**

### Backend Setup

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/the-alchemist.git
cd the-alchemist/Backend
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**
Create `.env` file with:
```bash
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_API_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# Mindat API
MINDAT_API_KEY=your_mindat_key
MINDAT_HOST=https://api.mindat.org/v1/

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key
DATABASE_URL=postgresql://user:password@host:5432/database

# LangSmith (Optional)
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=the-alchemist

# MCP Server
MCP_SERVER_URL=http://localhost:8010/mcp

# System Config
DEBUG=True
REQUEST_TIMEOUT=30
MAX_RETRIES=3
SAMESITE=lax
ENVIRONMENT=development
```

5. **Run Database Migrations**
```bash
# Tables are auto-created on app startup via SQLAlchemy
```

6. **Start Backend Server**
```bash
# Terminal 1: FastAPI Backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: MCP Server (in Backend folder)
python mcp_server.py
```

Backend will be available at `http://localhost:8000`
MCP Server at `http://localhost:8010`

### Frontend Setup

1. **Navigate to Frontend**
```bash
cd ../Frontend
```

2. **Install Dependencies**
```bash
npm install
```

3. **Configure Environment Variables**
Create `.env` file with:
```bash
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
```

4. **Start Development Server**
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Verify Installation

```bash
# Test Backend Health
curl http://localhost:8000/health

# Test Frontend
Open http://localhost:5173 in browser

# Test Chat
1. Sign up/Login
2. Send a message: "What minerals contain copper?"
3. See agent process and return results
```

---

## 📁 Project Structure

### Backend Directory Structure

```
Backend/
├── app/
│   ├── agents/                      # Multi-agent system
│   │   ├── base_agent.py           # AgentFactory & AgentRegistry
│   │   ├── initialize_agent.py     # LangGraph setup & supervisor
│   │   └── initialize_llm.py       # Azure OpenAI initialization
│   │
│   ├── config/                      # Configuration
│   │   ├── settings.py             # Pydantic Settings from env
│   │   └── mindat_config.py        # Mindat API client config
│   │
│   ├── core/                        # FastAPI app setup
│   │   ├── app.py                  # create_app() factory function
│   │   └── config.py               # Templates & paths
│   │
│   ├── database/                    # Data access layer
│   │   └── database.py             # SQLAlchemy engine & SessionLocal
│   │
│   ├── dependencies/                # FastAPI dependency injection
│   │   └── auth.py                 # get_current_user, get_optional_user
│   │
│   ├── input_validation/            # Request validation
│   │   ├── domain.py               # Domain validators
│   │   ├── parameters.py           # Query parameter validation
│   │   ├── security.py             # Security checks
│   │   └── validator.py            # User input validation
│   │
│   ├── models/                      # Pydantic request/response models
│   │   ├── agent_models.py         # AgentQueryRequest, Response
│   │   ├── auth_models.py          # LoginRequest, RegisterRequest
│   │   ├── chat_models.py          # Session, Message schemas
│   │   ├── mindat_query.py         # Mindat query models
│   │   ├── tool_response_models.py # Tool output schemas
│   │   ├── user_models.py          # User models
│   │   └── visualization.py        # Plot & visualization models
│   │
│   ├── routers/                     # API route handlers
│   │   ├── agent.py                # POST /api/agent/chat
│   │   ├── auth.py                 # /api/auth/* endpoints
│   │   ├── default.py              # GET /, /health
│   │   ├── mindat.py               # /api/mindat/geomaterials
│   │   ├── plots.py                # /api/plots/download, /email
│   │   ├── profile.py              # /api/profile/* endpoints
│   │   ├── sessions.py             # /api/sessions/* (CRUD)
│   │   └── user.py                 # /api/users/* (CRUD)
│   │
│   ├── schema/                      # SQLAlchemy ORM models
│   │   ├── user.py                 # User table definition
│   │   ├── profile.py              # Profile table definition
│   │   ├── chat.py                 # Session, Message, AgentOutput tables
│   │   └── agent.py                # AgentTask, Run, Artifact tables
│   │
│   ├── services/                    # Business logic
│   │   ├── mindat_endpoints_services.py # Mindat API clients
│   │   ├── plots_services.py       # Plot generation logic
│   │   ├── profile_service.py      # Profile management
│   │   └── user_service.py         # User CRUD operations
│   │
│   ├── tools/                       # MCP-registered tools
│   │   ├── geomaterial.py          # collect_geomaterials() tool
│   │   ├── locality.py             # collect_localities() tool
│   │   ├── data_profile.py         # profile_sample_data() tool
│   │   └── visualizing.py          # Plot generation (commented)
│   │
│   ├── utils/                       # Utility functions
│   │   ├── custom_message.py       # Custom exceptions
│   │   ├── custom_prompts.py       # Agent system prompts
│   │   ├── helpers.py              # Helper functions
│   │   └── plot_sepcs.py           # Vega-Lite specifications
│   │
│   ├── contents/                    # Generated data & plots
│   │   └── sample_data/            # Sample API responses
│   │
│   ├── __init__.py
│   └── main.py                     # FastAPI app with CORS
│
├── mcp_server.py                   # FastMCP server for tools
├── requirements.txt                # Python dependencies
├── render.yaml                     # Render.com deployment config
├── .env                           # Environment variables (git ignored)
└── .env.production                # Production environment file
```

### Frontend Directory Structure

```
Frontend/
├── src/
│   ├── App.jsx                     # Main app component & routes
│   ├── main.jsx                    # React entry point
│   ├── App.css                     # Global styles
│   ├── index.css                   # CSS reset
│   │
│   ├── api/                        # API integration
│   │   ├── apiClient.js           # Axios instance with interceptors
│   │   └── testEndpoint.js        # Health check utility
│   │
│   ├── components/
│   │   ├── auth/                  # Authentication components
│   │   │   ├── SignIn.jsx         # Login form
│   │   │   ├── Signup.jsx         # Registration form
│   │   │   ├── AuthCallback.jsx   # OAuth callback handler
│   │   │   └── auth.css           # Auth styles
│   │   │
│   │   ├── chats/                 # Chat interface components
│   │   │   ├── Sidebar.jsx        # Chat list & navigation
│   │   │   ├── ChatWindow.jsx     # Message display area
│   │   │   ├── ChatInput.jsx      # Message input form
│   │   │   ├── MessageBubble.jsx  # Individual message display
│   │   │   ├── DataTable.jsx      # Table visualization
│   │   │   ├── VegaChart.jsx      # Vega-Lite chart renderer
│   │   │   ├── ProfileModal.jsx   # User profile modal
│   │   │   ├── SettingsModal.jsx  # LLM settings modal
│   │   │   ├── ChartSettingsModal.jsx # Chart customization
│   │   │   ├── IconComponents.jsx # Custom icon library
│   │   │   └── *.css              # Component stylesheets
│   │   │
│   │   ├── dashboard/             # Dashboard components
│   │   │   └── comp1.jsx          # Landing/home page
│   │   │
│   │   ├── profile/               # Profile components
│   │   │
│   │   └── shared/                # Shared components
│   │       └── header.jsx         # Navigation header
│   │
│   ├── contexts/
│   │   └── AuthContext.jsx        # Auth state management
│   │
│   ├── lib/
│   │   └── supabase.js            # Supabase client initialization
│   │
│   ├── pages/                      # Page components
│   │   ├── Chat.jsx               # Chat interface page
│   │   ├── Dashboard.jsx          # Home/landing page
│   │   ├── Logout.jsx             # Logout handler
│   │   └── *.css                  # Page styles
│   │
│   └── services/
│       └── chatService.js         # Chat API service layer
│
├── public/
│   └── images/                    # Logo & static assets
│
├── vite.config.js                 # Vite configuration with API proxy
├── package.json                   # Dependencies & scripts
├── index.html                     # HTML template
├── .env                          # Environment variables (git ignored)
└── .env.example                  # Environment template
```

### Documentation Directory

```
Docs/
├── architecture.mmd               # System architecture diagram
├── mcp.mmd                       # MCP integration diagram
├── sequence.mmd                  # Message flow sequence
└── workflow.mmd                  # Multi-agent workflow
```

---

## 📡 API Documentation

### Authentication Endpoints (`/api/auth`)

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123",
  "full_name": "John Doe"
}

Response: 
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-04-22T10:00:00Z"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123"
}

Response:
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user": { ...user_data }
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer {access_token}

Response:
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

#### Logout
```http
POST /api/auth/logout
Authorization: Bearer {access_token}
```

### Chat Session Endpoints (`/api/sessions`)

#### List User Sessions
```http
GET /api/sessions
Authorization: Bearer {access_token}

Response:
[
  {
    "id": "session-uuid",
    "user_id": "user-uuid",
    "title": "Copper Minerals Analysis",
    "created_at": "2024-04-22T10:00:00Z"
  }
]
```

#### Create New Session
```http
POST /api/sessions
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "New Session"
}

Response: { ...session_data }
```

#### Get Session Messages
```http
GET /api/sessions/{session_id}/messages
Authorization: Bearer {access_token}

Response:
[
  {
    "id": "message-uuid",
    "sender": "user|agent",
    "text": "What minerals contain copper?",
    "timestamp": "2024-04-22T10:00:00Z"
  }
]
```

#### Save Message
```http
POST /api/sessions/{session_id}/messages
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "text": "Message content",
  "sender": "user"
}
```

#### Update Session
```http
PUT /api/sessions/{session_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Updated Title"
}
```

#### Delete Session
```http
DELETE /api/sessions/{session_id}
Authorization: Bearer {access_token}
```

### Agent Endpoints (`/api/agent`)

#### Chat with Agent
```http
POST /api/agent/chat
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "user_message": "Find minerals with hardness > 7",
  "session_id": "session-uuid (optional)"
}

Response:
{
  "response": "Here are minerals with hardness > 7...",
  "agent_output": {
    "type": "text|chart|table",
    "data": {...}
  },
  "session_id": "session-uuid",
  "message_id": "message-uuid"
}
```

#### Health Check
```http
GET /api/agent/health

Response:
{
  "status": "healthy",
  "uptime": "2h 30m",
  "agents_available": 5
}
```

### Mindat Endpoints (`/api/mindat`)

#### Search Geomaterials
```http
GET /api/mindat/geomaterials
Authorization: Bearer {access_token}

Query Parameters:
- elements: "Cu,Au"
- crystal_system: "Cubic"
- hardness_min: 5
- hardness_max: 9
- density_min: 2.5
- density_max: 20
- limit: 100

Response:
{
  "data": [
    {
      "id": "mineral-id",
      "name": "Malachite",
      "formula": "Cu2CO3(OH)2",
      "hardness": "3.5 - 4",
      "density": "3.73 - 3.94",
      "elements": ["Cu", "C", "O", "H"]
    }
  ],
  "total": 45,
  "limit": 100
}
```

### Plot Endpoints (`/api/plots`)

#### Download Plot
```http
GET /api/plots/download/{fileName}
Authorization: Bearer {access_token}

Response: Binary file (PNG/PDF)
```

#### Email Plot
```http
POST /api/plots/email
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "recipient_email": "user@example.com",
  "fileName": "plot-name.png",
  "message": "Check out this visualization"
}
```

### User Endpoints (`/api/users`)

#### Get User
```http
GET /api/users/user
Authorization: Bearer {access_token}

Response:
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-04-22T10:00:00Z"
}
```

#### Update User
```http
PATCH /api/users/user
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "full_name": "John Doe Updated",
  "email": "newemail@example.com"
}
```

#### Delete User
```http
DELETE /api/users/user
Authorization: Bearer {access_token}
```

---

## 🔧 Configuration

### Environment Variables

#### Backend Configuration (`.env`)

```bash
# ============================================
# System Configuration
# ============================================
DEBUG=True                          # Enable debug mode
REQUEST_TIMEOUT=30                  # Request timeout in seconds
MAX_RETRIES=3                      # Max API retry attempts
SAMESITE=lax                       # Cookie SameSite policy
ENVIRONMENT=development            # development|staging|production

# ============================================
# Azure OpenAI Configuration
# ============================================
AZURE_OPENAI_API_KEY=              # Your Azure OpenAI API key
AZURE_OPENAI_API_ENDPOINT=         # e.g., https://your-resource.openai.azure.com/
AZURE_DEPLOYMENT_NAME=gpt-4o       # Deployment name
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# ============================================
# Mindat API Configuration
# ============================================
MINDAT_API_KEY=                    # Your Mindat API key
MINDAT_HOST=https://api.mindat.org/v1/

# ============================================
# Supabase Configuration
# ============================================
SUPABASE_URL=                      # Your Supabase project URL
SUPABASE_KEY=                      # Supabase service role key
DATABASE_URL=                      # PostgreSQL connection string

# ============================================
# LangSmith Configuration (Optional)
# ============================================
LANGSMITH_API_KEY=                 # Your LangSmith API key
LANGSMITH_TRACING=true             # Enable tracing
LANGSMITH_PROJECT=the-alchemist    # Project name

# ============================================
# MCP Server Configuration
# ============================================
MCP_SERVER_URL=http://localhost:8010/mcp  # Local or deployed URL
```

#### Frontend Configuration (`.env`)

```bash
# ============================================
# API Configuration
# ============================================
VITE_API_URL=http://localhost:8000  # Backend API URL

# ============================================
# Supabase Configuration
# ============================================
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
```

---

## 🤖 Multi-Agent System

### Supervisor Architecture

The system uses a **Supervisor Agent** powered by LangGraph that analyzes user queries and routes them to specialized agents:

#### Agent Types

1. **Supervisor Node**
   - Analyzes incoming queries
   - Determines agent type needed
   - Routes to appropriate agent
   - Aggregates final response

2. **General Agent**
   - Handles greetings ("Hello", "Hi")
   - Answers FAQs
   - Provides conversational responses
   - No tool invocation

3. **Geomaterial Collector Agent**
   - Collects mineral data from Mindat API
   - Filters by: element, crystal system, hardness, density, optical properties
   - Performs data aggregation
   - Returns structured mineral datasets

4. **Locality Collector Agent**
   - Queries mineral locations worldwide
   - Groups by country/region
   - Provides occurrence data
   - Links to specimen records

5. **Vega Plot Generator Agent**
   - Creates interactive visualizations
   - Generates Vega-Lite specifications
   - Supports: histograms, heatmaps, scatter plots, network graphs
   - Customizable colors and aggregations

### Agent Workflow Example

```
User: "How many minerals contain copper?"
       │
       ▼
Supervisor analyzes intent
       │
       ├─ Type: GEOMATERIAL_QUERY
       ├─ Action: Collect geomaterials with Cu element
       │
       ▼
Geomaterial Collector invokes MCP tool
       │
       ├─ Tool: collect_geomaterials(element="Cu")
       │
       ▼
MCP Server executes tool
       │
       ├─ Calls Mindat API
       ├─ Returns 500 copper minerals
       │
       ▼
Supervisor evaluates response
       │
       ├─ Needs visualization? YES
       │
       ▼
Vega Plot Generator Agent
       │
       ├─ Creates histogram spec
       ├─ Groups by hardness/density
       │
       ▼
Final Response
       │
       ├─ Text: "Found 500 copper-bearing minerals"
       ├─ Chart: Vega histogram visualization
       ├─ Metadata: Data source, timestamp
       │
       ▼
Frontend renders MessageBubble with text + chart
```

### Tool Integration (MCP)

Tools are registered via FastMCP and consumed by agents:

```python
# Backend/mcp_server.py
mcp.tool(collect_geomaterials)
mcp.tool(collect_localities)
mcp.tool(profile_sample_data)
```

Agents invoke tools via MCP Client:
```python
# Agent makes HTTP request to MCP Server
response = mcp_client.invoke_tool(
    name="collect_geomaterials",
    arguments={"element": "Cu", "limit": 100}
)
```

---

## 🚢 Deployment

### Backend Deployment (Render.com)

1. **Create Render Account**
   - Sign up at render.com
   - Connect GitHub repository

2. **Configure Services**
   
   **Service 1: FastAPI Backend**
   - Name: `alchemist-backend`
   - Runtime: Python
   - Region: Oregon (US)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Health Check Path: `/health`

   **Service 2: MCP Server**
   - Name: `alchemist-mcp`
   - Runtime: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python mcp_server.py`

3. **Set Environment Variables**
   - Add all `.env` variables in Render dashboard
   - Update `MCP_SERVER_URL` to deployed MCP endpoint

4. **Deploy**
   - Push to GitHub
   - Render auto-deploys on push

### Frontend Deployment (Vercel)

1. **Create Vercel Account**
   - Sign up at vercel.com
   - Connect GitHub repository

2. **Configure Project**
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist/`

3. **Set Environment Variables**
   - `VITE_API_URL`: Backend deployed URL
   - `VITE_SUPABASE_URL`: Your Supabase URL
   - `VITE_SUPABASE_ANON_KEY`: Supabase anon key

4. **Deploy**
   - Vercel auto-deploys on GitHub push
   - Custom domain available

### Database Deployment (Supabase)

1. **Create Supabase Project**
   - Sign up at supabase.com
   - Create PostgreSQL database

2. **Configure Authentication**
   - Enable Supabase Auth
   - Configure OAuth providers

3. **Update Connection Strings**
   - Copy `DATABASE_URL` to Backend `.env`
   - Copy `SUPABASE_URL` and key to Frontend `.env`

### Deployment Architecture

```
GitHub Repository
    │
    ├─→ [Render Build] → alchemist-backend (Port 8000)
    │       └─→ Deployed as: https://alchemist-backend.onrender.com
    │
    ├─→ [Render Build] → alchemist-mcp (Port 8010)
    │       └─→ Deployed as: https://alchemist-mcp.onrender.com
    │
    └─→ [Vercel Build] → Frontend (React/Vite)
            └─→ Deployed as: https://alchemist.vercel.app

    [Supabase PostgreSQL]
        └─→ Database: the-alchemist
```

---

## 🔨 Development

### Running Tests

```bash
# Backend tests
cd Backend
pytest

# Frontend tests
cd Frontend
npm test
```

### Code Quality

```bash
# Backend linting
pylint app/
black app/

# Frontend linting
npm run lint
```

### Database Migrations

```bash
# Use Alembic for migrations (recommended)
alembic init migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Debugging

1. **LangSmith Dashboard**
   - Monitor agent behavior at https://smith.langchain.com
   - View execution traces and token usage

2. **Browser DevTools**
   - Inspect network requests
   - Check local storage (sessions)
   - Console for errors

3. **Backend Logs**
   - Check Render dashboard
   - Local: `uvicorn app.main:app --reload --log-level debug`

### Key Dependencies

**Backend (Critical)**
```
langchain==0.x.x
langgraph==0.x.x
fastapi==0.119.0
sqlalchemy==2.x.x
pydantic==2.x.x
fastmcp==latest
langchain-mcp-adapters==latest
```

**Frontend (Critical)**
```
react==19.1.1
vite==7.1.7
react-router-dom==7.9.5
axios==latest
vega==5.x.x
vega-lite==5.x.x
```

### Project Documentation

- **Docs/architecture.mmd**: System architecture overview
- **Docs/mcp.mmd**: MCP integration diagram
- **Docs/sequence.mmd**: Message flow sequence
- **Docs/workflow.mmd**: Multi-agent workflow

---

## 🐛 Troubleshooting

### Common Issues

1. **Backend Connection Refused**
   - Ensure MCP Server is running on port 8010
   - Check `MCP_SERVER_URL` in `.env`
   - Verify firewall settings

2. **Supabase Auth Issues**
   - Check CORS settings in Supabase
   - Verify `SUPABASE_URL` and keys
   - Clear browser cookies

3. **Agent Not Responding**
   - Check Azure OpenAI API key
   - Verify LangSmith connectivity
   - Check logs in Render dashboard

4. **Database Connection**
   - Verify `DATABASE_URL` format
   - Check Supabase service role key
   - Ensure firewall allows connections

### Getting Help

- 📚 Check documentation in `/Docs` folder
- 🐙 Open issue on GitHub
- 💬 Review LangSmith traces
- 📋 Check API documentation above

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👥 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📧 Contact & Support

For questions or support:
- Open an issue on GitHub
- Check existing documentation
- Review LangSmith dashboard for debugging

---

**Last Updated**: April 22, 2026  
**Version**: 1.0.0

- Query mineral data based on properties like hardness, crystal system, elements.
- Visualize the results via histograms, networks, and heatmaps.
- Explore mineral localities and their distributions across countries.

---

## 🚀 Features

✅ **AI Agent-Powered Workflow**  
- Built using LangChain and LangGraph to create an agent-based system for data retrieval, analysis, and visualization.

✅ **FastAPI Backend**  
- RESTful API endpoints for querying mineral data through Mindat's API.
- FastAPI templating to support HTML-based UI for visualization and user interaction.

✅ **LangSmith Integration**  
- Full agent activity tracking, monitoring of the workflow execution, and debugging.

✅ **Data Visualization**  
- Histograms for element distributions.
- Network diagrams to show mineral relationships.
- Heatmaps for locality data.

✅ **Multi-Agent Collaboration**  
- Agents collaborate to collect mineral information, filter by properties, and generate visual outputs.

---

## 📦 Technologies Used

| Component         | Technology             |
|------------------|------------------------|
| Backend          | FastAPI (Python)       |
| Agent System     | LangChain + LangGraph  |
| Visualization     | Matplotlib, Plotly     |
| API for Data     | REST API (Mindat.org)  |
| Monitoring       | LangSmith              |
| UI / Frontend    | FastAPI Template       |

---

## 🧠 Agent Workflow Overview

```
[User Input] → Supervisor (LangChain) → 
   ↓
  Collector → Locality_Collector → Histogram_Plotter → 
   ↓                        ↓
 Network_Plotter ← Heatmap_Plotter ← Supervisor
```

The supervisor routes the query to the appropriate agent based on parsed input. Each agent interacts with external REST APIs or internal tools (e.g., `tavily_tool`, `python_repl_tool`) to collect data and produce visualizations.

---

## 📚 API Endpoints (FastAPI)

| Endpoint              | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| `/`                  | Root endpoint for FastAPI application.                                     |
| `/query`             | POST endpoint to receive user queries and dispatch them to the agent system. |
| `/plot_histogram`    | GET endpoint to fetch histogram data for elements/distributions.            |
| `/plot_network`      | GET endpoint to fetch network visualization data for mineral relationships.  |
| `/heatmap`           | GET endpoint to generate and return heatmap data based on locality info.    |

---

## 🧪 How It Works

1. **User submits a query** via the FastAPI frontend or through an API call.
2. The query is parsed by a **supervisor agent**, which uses LangChain to determine the next step in the graph.
3. The **LangGraph** routes the query to the appropriate agent (e.g., `Collector`, `Histogram_Plotter`).
4. The selected agent interacts with the **Mindat REST API**, processes data, and returns a result.
5. The result is then returned to the user via FastAPI (as HTML or data visualization).

---

## 📌 Example Queries

```text
1. "Plot histogram of elements in minerals with hardness 3-5."
2. "Show network of mineral distribution for Neodymium in Hexagonal crystal system."
3. "Generate heatmap of mineral occurrences in Canada."
```

---

## 📦 Installation

### Prerequisites
- Python 3.10+
 (with `pip`)
  
### Install Package

```bash
pip install fastapi uvicorn langchain langgraph langsmith matplotlib plotly
```

---

## 🧪 Running the Application

```bash
# Run FastAPI app
uvicorn main:app --reload

# Access the UI at http://localhost:8000
```

---

## 🧑‍💻 UI / Frontend

- Built using FastAPI templates (HTML/JS).
  
You can render your frontend with:

```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
async def root(request: Request):
    return HTMLResponse(
        content="""
            <html>
                <body>
                    <h1>MineralAI</h1>
                    <form action="/query" method="post">
                        <textarea name="user_input"></textarea><br>
                        <button type="submit">Query</button>
                    </form>
                </body>
            </html>
        """,
 status_code=200
    )
```

---

## 📌 LangSmith Integration

To track agent behavior and execution flow:

1. Set your **LangSmith API token** as an environment variable.
2. Use `langsmith.tracing` to wrap your agent's execution in a trace.

Example:

```python
from langsmith import traceable

@traceable
def run_agent(prompt):
    # agent logic here
```

---

## 🧭 Project Structure

```
/mineralai/
├── main.py              # FastAPI app + LangGraph workflow
├── templates/           # Frontend HTML templates
├── agents/
│   ├── collector.py    # Agent for collecting mineral data
│   ├── plotter.py       # Plotting agents (Histogram, Network, Heatmap)
├── utils/
│   ├── api_client.py   # For querying Mindat REST API
├── requirements.txt
```

---



