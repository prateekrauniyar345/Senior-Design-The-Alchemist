# 🧪 The Alchemist - AI-Powered Mineral Data Explorer

**The Alchemist** is a sophisticated, production-ready full-stack AI application that transforms mineral data exploration through intelligent multi-agent workflows. It combines cutting-edge Large Language Models (LLMs), advanced agent orchestration, and specialized tools to enable users to query, analyze, and visualize complex mineralogical data from the Mindat.org database using natural language, without requiring any technical expertise.

> **In essence**: A user asks "Show me minerals with copper in Eastern Canada" in plain English, and the system intelligently routes the request through AI agents that query multiple data sources, process the results, and return interactive visualizations—all without the user writing a single API call or filter parameter.

---

## 📋 Table of Contents

1. [What The Alchemist Does](#what-the-alchemist-does)
2. [Why This Project Exists](#why-this-project-exists)
3. [How It Works End-to-End](#how-it-works-end-to-end)
4. [Core Architecture](#core-architecture)
5. [Technology Stack in Detail](#technology-stack-in-detail)
6. [System Components & Their Interactions](#system-components--their-interactions)
7. [Authentication & Security](#authentication--security)
8. [Multi-Agent Workflow Explained](#multi-agent-workflow-explained)
9. [Database Schema & Data Persistence](#database-schema--data-persistence)
10. [API Endpoints Documentation](#api-endpoints-documentation)
11. [Frontend Implementation](#frontend-implementation)
12. [MCP Server & Tool Integration](#mcp-server--tool-integration)
13. [Input Validation & Security](#input-validation--security)
14. [File Structure & Organization](#file-structure--organization)
15. [Getting Started](#getting-started)
16. [Deployment](#deployment)
17. [Design Decisions & Rationale](#design-decisions--rationale)

---

# What The Alchemist Does

## Primary Purpose

The Alchemist is a **Natural Language Interface to Mineralogical Data**. It transforms how geoscientists, mineral enthusiasts, and researchers interact with mineral databases by allowing them to ask questions in plain English instead of constructing complex API queries.

### User Problems It Solves

1. **Complexity of Mindat API**: The Mindat.org API has 40+ endpoints with complex filtering parameters. Most users don't know how to combine them.
2. **Data Integration Challenges**: Finding minerals, their properties, and their locations requires multiple API calls across different endpoints.
3. **Visualization Gap**: Raw data needs to be processed and visualized. Most users can't create meaningful charts from JSON responses.
4. **Context Awareness**: Traditional APIs are stateless. Users need persistent sessions to maintain conversation context.
5. **Accessibility**: Geoscientists should focus on science, not engineering.

### What Users Can Do

- **Query Minerals**: "Find all IMA-approved minerals with hardness between 5 and 7"
- **Explore Geography**: "Show me mineral localities in Brazil"
- **Filter Chemistry**: "Get minerals that contain copper but not sulfur"
- **Analyze Data**: "Plot a histogram of mineral density distribution"
- **Visualize Networks**: "Show me the co-occurrence network of minerals in Canada"
- **Combine Knowledge**: "For minerals found in Western Australia, show those with hardness > 6"

---

# Why This Project Exists

## Problem Statement

Mineralogists and geoscientists spend significant time:
1. Learning complex API documentation
2. Crafting queries with exact parameter names and formats
3. Parsing JSON responses manually
4. Creating visualizations externally
5. Managing multiple queries across different endpoints

## The Alchemist Solution

By leveraging **Large Language Models (LLMs)** and **agentic workflows**, the system:
- **Understands Intent**: Converts natural language into API parameters
- **Routes Intelligently**: Determines which specialized agent should handle the query
- **Executes Efficiently**: Fetches data in parallel, avoiding redundant API calls
- **Visualizes Automatically**: Generates meaningful charts without user intervention
- **Maintains Context**: Remembers conversation history and user preferences

## Design Philosophy

**"AI-powered simplicity through intelligent orchestration"**

The system is built on the principle that users should interact with data through conversation, not configuration. Behind the scenes, sophisticated agents handle the complexity.

---

# How It Works End-to-End

## Complete User Journey

### Step 1: User Sends a Query
```
User types in chat: "Show me minerals with iron in Canada"
```

### Step 2: Frontend Sends to Backend
```
HTTP POST /api/agent/chat
{
  "query": "Show me minerals with iron in Canada",
  "session_id": "uuid-of-chat-session"
}
```

### Step 3: Backend Receives & Validates
```
FastAPI Router (app/routers/agent.py)
    ↓
Input Validation Layer (input_validation/validator.py)
    - Security check: Is this request safe?
    - Domain check: Is it mineral-related?
    - Parameter check: Are the filters valid?
```

### Step 4: LangGraph Orchestration Begins
```
Initialize Agent Graph (agents/initialize_agent.py)
    ↓
Supervisor Agent (LLM-powered decision maker)
    - Analyzes the query semantically
    - Determines the intent
    - Decides which agents to invoke
```

### Step 5: Supervisor Routes to Appropriate Agents
```
If query needs mineral properties:
    → Geomaterial Collector Agent
    
If query needs location data:
    → Locality Collector Agent
    
If query needs visualization:
    → Vega Plot Generator Agent
    
If query is conversational:
    → General Agent
```

### Step 6: Agents Execute via MCP
```
Agent invokes MCP tools:
    ↓
MCP Server (mcp_server.py)
    ↓
Tool Functions (tools/geomaterial.py, tools/locality.py)
    ↓
Mindat API (https://api.mindat.org/v1/)
```

### Step 7: Data Processing
```
Mindat API returns JSON
    ↓
Tool processes response (validation, filtering)
    ↓
Data saved to disk (contents/sample_data/)
    ↓
Returns to Agent
```

### Step 8: Visualization Generation
```
If visualization needed:
    Vega Plot Generator Agent
        ↓
    Reads data from disk
    ↓
    Generates Vega-Lite specification
    ↓
    Returns chart JSON
```

### Step 9: Response Construction
```
Build AgentQueryResponse:
    - Message: Human-readable summary
    - Data File Path: Link to JSON data
    - Chart Spec: Vega-Lite JSON
    - Sample Data: First 100 rows
```

### Step 10: Save to Database
```
Message saved to PostgreSQL:
    - messages table: User query + Agent response
    - agent_runs table: Execution metadata
    - data_artifacts table: Generated files
    - visualizations table: Chart metadata
```

### Step 11: Return to Frontend
```
HTTP 200 OK with AgentQueryResponse
    ↓
Frontend receives response
    ↓
MessageBubble component renders
    - Text in conversation
    - Chart using Vega-Embed
    - Data table for sample data
```

### Step 12: User Sees Results
```
Interactive chart appears in chat
User can:
  - Hover for details
  - Zoom/pan
  - Download as PNG
  - Export data
```

---

# Core Architecture

## System Layers

### Layer 1: Frontend (User Interface)
- **Technology**: React 19.1.1 + Vite
- **Responsibility**: Present data, accept input, render visualizations
- **Communication**: HTTPS REST API to Backend
- **State**: React Context for authentication

### Layer 2: API Gateway (Request Routing)
- **Technology**: FastAPI 0.119.0 on Uvicorn
- **Responsibility**: Route requests, validate inputs, manage sessions
- **Endpoints**:
  - `/api/auth/*` - Authentication
  - `/api/agent/chat` - Primary chat endpoint
  - `/api/sessions/*` - Session management
  - `/api/users/*` - User management
  - `/health` - Health checks

### Layer 3: Agent Orchestration (Intelligence)
- **Technology**: LangChain 1.0 + LangGraph 1.0
- **Responsibility**: Decide which agents to use, coordinate execution
- **Architecture**:
  ```
  Supervisor (decision router)
      ├── General Agent
      ├── Geomaterial Collector Agent
      ├── Locality Collector Agent
      └── Vega Plot Generator Agent
  ```

### Layer 4: Tool Execution (Action)
- **Technology**: Model Context Protocol (FastMCP 2.14.5)
- **Responsibility**: Execute specific tasks like API calls
- **Tools**:
  - `collect_geomaterials()` - Query mineral properties
  - `collect_localities()` - Query mineral locations
  - `profile_sample_data()` - Analyze data structure

### Layer 5: External APIs (Data Source)
- **Technology**: Mindat.org REST API
- **Responsibility**: Provide authoritative mineral data
- **Endpoints**: 40+ available (geomaterials, localities, references, etc.)

### Layer 6: Data Storage (Persistence)
- **Technology**: PostgreSQL via Supabase
- **Responsibility**: Store users, sessions, messages, execution history
- **Tables**: users, sessions, messages, agent_tasks, agent_runs, data_artifacts, visualizations

---

# Technology Stack in Detail

## Backend Technologies

### FastAPI (Web Framework)
**What**: A modern Python web framework for building APIs
**Why**: 
- Automatic API documentation (Swagger)
- Built-in request validation with Pydantic
- Async-first (better performance)
- Type hints for self-documenting code
- Dependency injection system

**How it's used**:
```python
@router.post("/api/agent/chat")
async def chat_with_agent(
    request: AgentQueryRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # FastAPI automatically:
    # 1. Validates request JSON against AgentQueryRequest schema
    # 2. Injects database session
    # 3. Validates JWT from cookies and injects current user
    # 4. Returns type-safe response
```

### LangChain + LangGraph (Agent Framework)
**What**: Tools for building LLM-powered applications and multi-agent systems
**Why**:
- LangChain: Unified interface to different LLMs, tool calling, message handling
- LangGraph: Graph-based orchestration of agent workflows, state management

**How it's used**:
```python
# LangChain handles:
- Converting natural language to structured tool calls
- Managing conversation context
- Error handling and retries

# LangGraph handles:
- Defining agent nodes (functions)
- Routing decisions (conditional edges)
- State management across agent calls
- Visualization of workflows
```

### Supabase (Database + Auth)
**What**: Backend-as-a-Service combining PostgreSQL + authentication
**Why**:
- Managed PostgreSQL (no DevOps needed)
- Built-in OAuth providers (Google, GitHub, etc.)
- Real-time subscriptions
- Row-level security
- No cold starts

**How it's used**:
```python
# PostgreSQL for:
- User accounts
- Chat sessions & messages
- Agent execution history
- Generated visualizations

# Auth for:
- User registration & login
- JWT token generation
- Session management via cookies
```

### SQLAlchemy (ORM)
**What**: Python ORM for database interaction
**Why**:
- Type-safe database queries
- Automatic schema generation
- Relationship management
- Query composition

**How it's used**:
```python
# Define schema:
class User(Base):
    __tablename__ = "users"
    id = Column(UUID, primary_key=True)
    email = Column(String, nullable=False)
    sessions = relationship("Session")

# Query:
user = db.query(User).filter(User.email == "user@example.com").first()
```

### Model Context Protocol (MCP / FastMCP)
**What**: Protocol for connecting LLMs to external tools via a client-server architecture
**Why**:
- Standardized way to register tools with LLMs
- Separates tool logic from agent logic
- Allows tools to run in isolated processes
- Enables tool versioning and updates without code changes

**How it's used**:
```python
# MCP Server (mcp_server.py):
mcp = FastMCP("Mindat Master Server")
mcp.tool(collect_geomaterials)
mcp.tool(collect_localities)
mcp.run()

# Agent calls:
tools = await client.get_tools()
# Tools now available for LLM function calling
```

---

## Frontend Technologies

### React 19.1.1 (UI Framework)
**What**: JavaScript library for building user interfaces
**Why**:
- Component-based architecture
- Efficient re-rendering with virtual DOM
- Large ecosystem
- React Router for navigation

**How it's used**:
```jsx
<AuthProvider>
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/chat" element={<Chat />} />
      <Route path="/signin" element={<SignIn />} />
    </Routes>
  </BrowserRouter>
</AuthProvider>
```

### Vite (Build Tool)
**What**: Modern JavaScript build tool and dev server
**Why**:
- 10x faster than webpack during development
- Native ES modules (faster HMR)
- Optimized production builds
- Works with React via SWC (super-fast transpiler)

**How it's used**:
```js
// vite.config.js: Proxy API calls to backend
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```

### Vega-Lite (Visualization)
**What**: Declarative visualization grammar for creating interactive charts
**Why**:
- Create complex visualizations with JSON specs
- Automatically handles scales, axes, legends
- Interactive by default (hover, zoom, etc.)
- Responsive and accessible

**How it's used**:
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "description": "Histogram of mineral hardness",
  "data": {"values": [...]},
  "mark": "bar",
  "encoding": {
    "x": {"field": "hardness", "type": "quantitative", "bin": true},
    "y": {"aggregate": "count", "type": "quantitative"}
  }
}
```

### Axios (HTTP Client)
**What**: Promise-based HTTP client for JavaScript
**Why**:
- Request/response interceptors
- Automatic token refresh
- Error handling
- Request cancellation

**How it's used**:
```js
// API interceptor automatically includes JWT:
apiClient.post("/api/agent/chat", {query, session_id})
```

### React Context (State Management)
**What**: Built-in React feature for managing global state
**Why**:
- No external dependencies
- Sufficient for auth and user state
- Lightweight

**How it's used**:
```jsx
// AuthContext provides user state globally:
const {user, login, logout, loading} = useAuth();
```

---

# System Components & Their Interactions

## Backend Component Interaction Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     FastAPI Main App                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────┐  │
│  │  Auth Router    │  │  Agent Router    │  │Session R.  │  │
│  │                 │  │                  │  │            │  │
│  │ - /login        │  │ - POST /chat     │  │- GET /list │  │
│  │ - /register     │  │ - /health        │  │- POST /new │  │
│  │ - /me           │  │                  │  │            │  │
│  └────────┬────────┘  └────────┬─────────┘  └────────┬───┘  │
│           │                    │                     │       │
│           ▼                    ▼                     ▼       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Dependency Injection Layer                  │   │
│  │  - get_db() → SQLAlchemy Session                     │   │
│  │  - get_current_user() → Supabase JWT verification   │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                         │
│                     ▼                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Input Validation Pipeline                    │   │
│  │  1. Security checks (prompt injection, etc.)         │   │
│  │  2. Domain classification (is it mineral-related?)   │   │
│  │  3. Parameter validation (hardness range, etc.)      │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                         │
│                     ▼                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         LangGraph Agent Orchestration                │   │
│  │                                                      │   │
│  │    ┌──────────────────────────────────────┐         │   │
│  │    │ Supervisor Node (LLM Decision)       │         │   │
│  │    │ Routes to appropriate agents         │         │   │
│  │    └──────┬───────┬──────────┬────────────┘         │   │
│  │           │       │          │                       │   │
│  │      ┌────▼────┐  │    ┌─────▼──────┐               │   │
│  │      │General  │  │    │Geomaterial │               │   │
│  │      │Agent    │  │    │Collector   │               │   │
│  │      └────┬────┘  │    └─────┬──────┘               │   │
│  │           │       │          │                       │   │
│  │           │   ┌───▼──────┐   │   ┌────────────┐     │   │
│  │           │   │Locality  │   │   │Vega Plot   │     │   │
│  │           │   │Collector │   │   │Generator   │     │   │
│  │           │   └───┬──────┘   │   └────┬───────┘     │   │
│  │           │       │          │        │             │   │
│  │           └───────┴──────────┴────────┘             │   │
│  │                   │                                 │   │
│  │                   ▼                                 │   │
│  │            MCP Client                              │   │
│  │      (connects to MCP Server)                       │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                         │
│                     ▼                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Database Access Layer                        │   │
│  │  - Users, Sessions, Messages                         │   │
│  │  - Agent Tasks & Runs                               │   │
│  │  - Data Artifacts & Visualizations                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
         ┌─────────────────────────────────────┐
         │  Supabase PostgreSQL Database       │
         └─────────────────────────────────────┘
```

## Separate MCP Server Process

```
┌────────────────────────────────────────┐
│         MCP Server (Port 8010)         │
│      (python mcp_server.py)            │
├────────────────────────────────────────┤
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ FastMCP Server Instance          │ │
│  │ "Mindat Master Server"           │ │
│  └──────────────────────────────────┘ │
│           │       │        │           │
│           ▼       ▼        ▼           │
│  ┌──────────────────────────────────┐ │
│  │  Registered Tools:               │ │
│  │  - collect_geomaterials()        │ │
│  │  - collect_localities()          │ │
│  │  - profile_sample_data()         │ │
│  └──────────────────────────────────┘ │
│           │       │        │           │
│           ▼       ▼        ▼           │
│  ┌──────────────────────────────────┐ │
│  │  Tool Logic (app/tools/):        │ │
│  │  - Parse parameters              │ │
│  │  - Validate inputs               │ │
│  │  - Format for Mindat API         │ │
│  │  - Save results to disk          │ │
│  └──────────────────────────────────┘ │
│           │       │        │           │
│           ▼       ▼        ▼           │
│     (external Mindat API calls)        │
│                                        │
└────────────────────────────────────────┘
         ↑
         │ HTTP Communication
         │ (LangChain MCP Adapter)
         ▼
  Backend FastAPI App
```

---

# Authentication & Security

## Authentication Flow

### Step 1: User Registration
```
1. User submits: email, password, name
2. Frontend POST /api/auth/register
3. Backend:
   - Validates input (email format, password strength)
   - Supabase creates user
   - Creates entry in local PostgreSQL users table
   - Returns user ID & tokens
4. Frontend stores tokens in HTTP-only cookies
```

### Step 2: User Login
```
1. User submits: email, password
2. Frontend POST /api/auth/login
3. Backend:
   - Supabase.auth.sign_in_with_password()
   - Retrieves JWT tokens from Supabase
   - Verifies user exists in local users table
   - Sets HTTP-only cookies (sb-access-token, sb-refresh-token)
   - Returns user info
4. Frontend navigates to Dashboard
```

### Step 3: Protected Request
```
1. Frontend makes request with Authorization header
2. Axios interceptor includes JWT from cookies
3. Backend dependency (get_current_user):
   - Extracts token from cookies
   - Supabase.auth.get_user(token) → validates
   - Queries local users table for additional data
   - Injects user into route handler
4. If token invalid → 401 Unauthorized
5. If user not found locally → 401 Unauthorized
```

### Step 4: Token Refresh
```
1. Axios interceptor detects 401 response
2. Calls /api/auth/refresh with refresh token
3. Backend generates new access token
4. Updates cookie
5. Retries original request
```

## Security Measures

### 1. Input Validation (Multi-Layer)
```
Router Level: Pydantic automatically validates types
            → {"query": 123} becomes error

Security Level: Check for prompt injection attacks
              → ""; DROP TABLE users; --"
              → Detected and blocked

Domain Level: Is the query about minerals?
            → Off-topic queries rejected

Parameter Level: Are hardness values realistic?
               → hmin=1000 rejected (outside 0-10 scale)
```

### 2. Authentication
```
- JWT tokens from Supabase (industry standard)
- HTTP-only cookies (can't be stolen by JavaScript)
- Tokens expire after configured duration
- Refresh tokens for long sessions
- Token validation on every protected request
```

### 3. Database Security
```
- Row-level security in Supabase
  → Users can only access their own data
- SQLAlchemy ORM prevents SQL injection
  → Parameterized queries
- Connection pooling prevents resource exhaustion
```

### 4. CORS Policy
```python
CORSMiddleware in FastAPI:
- Allow origins: localhost:5173, production domain
- Allow credentials: True (cookies)
- Allow methods: GET, POST, PUT, DELETE, OPTIONS
- Allow headers: Content-Type, Authorization
```

### 5. Rate Limiting (Future)
```
- Prevent brute-force attacks
- Prevent DDoS
- Fair resource sharing
```

---

# Multi-Agent Workflow Explained

## What is an "Agent"?

An agent is an AI system that:
1. **Observes**: Understands the current state/query
2. **Decides**: Determines what action to take
3. **Acts**: Executes an action (calls a tool, queries API)
4. **Repeats**: Loops until the goal is achieved

## The Supervisor Agent (Router)

**Purpose**: Intelligently decide which specialized agent should handle the request

**How it works**:
```
Query: "Show me minerals with iron in Canada"

Supervisor LLM (GPT-4o):
  Input: Query + list of available agents
  Reasoning:
    - Query mentions "minerals" → geomaterial query
    - Query mentions "Canada" → location query
    - Query asks to "show" → visualization needed
  Output: Route to [Locality Collector, Vega Plot Generator]
```

**Implementation** (agents/initialize_agent.py):
```python
decision_model = factory.llm.with_structured_output(ControllerDecision)
decision_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
    ("system", f"You must route to: {', '.join(options)}")
])
decision = await chain.ainvoke({"messages": state["messages"]})
# Returns: ControllerDecision(next_agent="locality_collector", reasoning="...")
```

## Agent 1: General Agent

**Triggered when**: Conversational queries, greetings, questions about the system
**Responsibility**: Handle non-data queries
**Tools**: None (no Mindat API calls)
**Example**:
```
User: "What is The Alchemist?"
→ General Agent responds with explanation
```

**Implementation**:
```python
async def general_agent_node(state: State) -> dict:
    agent = registry.get("general_agent")
    result = await agent.ainvoke(state)
    return {
        "messages": result["messages"],
        "next": "supervisor"
    }
```

## Agent 2: Geomaterial Collector

**Triggered when**: Queries about mineral properties, elements, crystal systems, hardness, density, optical properties
**Responsibility**: Query Mindat /v1/geomaterials/ endpoint
**Tools**: `collect_geomaterials()`
**Example**:
```
User: "Find IMA-approved minerals with hardness > 5"
→ Geomaterial Collector:
   1. Parses query → ima=True, hmin=5
   2. Calls MCP tool: collect_geomaterials(ima=True, hmin=5)
   3. MCP Server calls Mindat API
   4. Returns JSON with matching minerals
   5. Saves results to disk
   6. Returns response to Supervisor
```

**Parameter Mapping** (tools/geomaterial.py):
```python
# Natural query: "hardness between 5 and 7"
# Converted to:
def collect_geomaterials(
    hmin: Optional[float] = None,  # Lower bound (5)
    hmax: Optional[float] = None,  # Upper bound (7)
    ima: Optional[bool] = None,    # IMA-approved only
    el_inc: Optional[List[str]] = None,  # Include elements
    el_exc: Optional[List[str]] = None,  # Exclude elements
    crystal_system: Optional[List[str]] = None,
    # ... 20+ more parameters
) -> GeomaterialToolResponse:
    # Make API call with parameters
    # Save to disk
    # Return response
```

## Agent 3: Locality Collector

**Triggered when**: Queries about mineral locations, geographic regions
**Responsibility**: Query Mindat /v1/localities/ endpoint
**Tools**: `collect_localities()`
**Example**:
```
User: "Show me mineral localities in Western Australia"
→ Locality Collector:
   1. Parses query → country="Australia", region="Western"
   2. Calls MCP tool: collect_localities(country="Australia")
   3. MCP Server calls Mindat API
   4. Returns JSON with localities
   5. Saves to disk with geographic coordinates
   6. Returns response to Supervisor
```

## Agent 4: Vega Plot Generator

**Triggered when**: Queries ask to visualize, plot, chart, or show data
**Responsibility**: Generate Vega-Lite specifications for interactive charts
**Tools**: `profile_sample_data()` (to understand data structure)
**Example**:
```
User: "Plot a histogram of mineral hardness distribution"
→ Vega Plot Generator:
   1. Reads previously collected data from disk
   2. Analyzes data structure
   3. Determines appropriate chart type (histogram)
   4. Generates Vega-Lite JSON:
      {
        "mark": "bar",
        "encoding": {
          "x": {"field": "hardness", "bin": true},
          "y": {"aggregate": "count"}
        }
      }
   5. Returns Vega spec to Supervisor
```

**Vega-Lite Spec Template** (utils/plot_specs.py):
```python
def build_histogram_vega_spec(
    data: List[Dict],
    field: str,
    title: str
) -> Dict:
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": title,
        "data": {"values": data},
        "mark": "bar",
        "encoding": {
            "x": {
                "field": field,
                "type": "quantitative",
                "bin": True
            },
            "y": {
                "aggregate": "count",
                "type": "quantitative"
            }
        }
    }
```

## How Agents Work Together (Workflow Graph)

**LangGraph Structure** (agents/initialize_agent.py):

```
State Definition:
- messages: List[BaseMessage]  # Conversation history
- next: Optional[str]          # Which agent to call next
- sample_data_path: Optional[str]  # Path to collected data
- vega_spec: Optional[Dict]    # Generated chart specification
- profile: Optional[Dict]      # Data schema info

Workflow:
START
  ↓
supervisor_node (Decision making)
  ├─→ Routes to: general_agent | geomaterial_collector | 
  │              locality_collector | vega_plot_generator | FINISH
  ↓
(All workers route back to supervisor when done)
supervisor_node (Check if more work needed)
  ├─→ If yes: Route to next agent
  ├─→ If no: FINISH
  ↓
FINISH
  ↓
END
```

**Conditional Routing** (agents/initialize_agent.py):

```python
# Instead of a fixed sequence, Supervisor decides next step
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state.get("next", "FINISH"),  # Get routing decision
    {
        "general_agent": "general_agent",
        "geomaterial_collector": "geomaterial_collector",
        "locality_collector": "locality_collector",
        "vega_plot_generator": "vega_plot_generator",
        "FINISH": "FINISH"
    }
)
```

## Real Example: Complex Query

**Query**: "For minerals found in Canada, show me those with copper, plot their hardness distribution"

**Execution Flow**:
```
1. Supervisor analyzes query
   → Needs: Locality data (Canada) + Geomaterial data (copper)
   → May need: Visualization

2. Routes to Locality Collector
   → collect_localities(country="Canada")
   → Saves: /contents/sample_data/mindat_locality_response.json

3. Returns to Supervisor
   → Supervisor analyzes: Data retrieved, copper filter needed

4. Routes to Geomaterial Collector
   → collect_geomaterials(el_inc=["Cu"])
   → Saves: /contents/sample_data/mindat_geomaterial_response.json

5. Returns to Supervisor
   → Supervisor analyzes: Two datasets collected, visualization requested

6. Routes to Vega Plot Generator
   → read /contents/sample_data/mindat_geomaterial_response.json
   → Generate histogram spec
   → Returns Vega-Lite JSON

7. Returns to Supervisor
   → All tasks complete → FINISH

8. Backend constructs response:
   {
     "message": "Found 47 minerals with copper in Canada...",
     "data_file_path": "http://localhost:8000/contents/...",
     "chart_spec": {...vega-lite json...},
     "sample_data": [first 100 rows]
   }
```

---

# Database Schema & Data Persistence

## Entity-Relationship Diagram

```
┌─────────────────┐
│     Users       │  (Synced with Supabase Auth)
├─────────────────┤
│ id (UUID) [PK]  │
│ supabase_user_id│
│ email           │
│ full_name       │
│ created_at      │
└────────┬────────┘
         │ 1:N
         │
    ┌────▼────────────┐
    │   Sessions      │  (Chat conversations)
    ├─────────────────┤
    │ id (UUID) [PK]  │
    │ user_id [FK]    │
    │ title           │
    │ created_at      │
    └────┬────────────┘
         │ 1:N
         │
    ┌────▼────────────────┐
    │    Messages         │  (Individual messages in session)
    ├──────────────────────┤
    │ id (UUID) [PK]      │
    │ session_id [FK]     │
    │ user_id [FK]        │
    │ sender              │  ("user" or "agent")
    │ content             │
    │ output_type         │  ("text", "plot", "table")
    │ meta_data (JSON)    │  (chart_spec, data_url, etc.)
    │ created_at          │
    └──────────────────────┘
         │ 1:N
         │
    ┌────▼──────────────────┐
    │  Agent Tasks          │  (Tracks what each agent did)
    ├────────────────────────┤
    │ id (UUID) [PK]        │
    │ session_id [FK]       │
    │ agent_name            │  (e.g., "geomaterial_collector")
    │ input_message_id [FK] │
    │ output_message_id [FK]│
    │ status                │  ("pending", "success", "failed")
    │ started_at            │
    │ finished_at           │
    └────────────────────────┘

    ┌──────────────────────┐
    │   Agent Runs         │  (Agent execution history)
    ├──────────────────────┤
    │ id (UUID) [PK]       │
    │ agent_name           │
    │ session_id [FK]      │
    │ status               │  ("running", "success", "failed")
    │ started_at           │
    │ finished_at          │
    └────┬─────────────────┘
         │ 1:N
         │
    ┌────▼──────────────────────┐
    │   Data Artifacts          │  (Generated files)
    ├───────────────────────────┤
    │ id (UUID) [PK]            │
    │ run_id [FK]               │
    │ artifact_type             │  ("json", "csv", "plot")
    │ file_path                 │
    │ description               │
    │ created_at                │
    └────┬──────────────────────┘
         │ 1:N
         │
    ┌────▼──────────────────────┐
    │  Visualizations           │  (Chart metadata)
    ├───────────────────────────┤
    │ id (UUID) [PK]            │
    │ artifact_id [FK]          │
    │ viz_type                  │  ("histogram", "heatmap")
    │ title                     │
    │ description               │
    │ rendered_html_path        │
    │ created_at                │
    └───────────────────────────┘

    ┌──────────────────────┐
    │   Profiles           │  (User profile info)
    ├──────────────────────┤
    │ id (UUID) [PK]       │
    │ email                │
    │ full_name            │
    │ avatar_url           │
    │ bio                  │
    │ preferences (JSON)   │  (LLM temperature, etc.)
    └──────────────────────┘
```

## Table Definitions (SQLAlchemy)

### Users Table
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supabase_user_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    # ↑ Links to Supabase Auth user
    email = Column(String(120), nullable=False)
    full_name = Column(String(120))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    sessions = relationship("Session", back_populates="user")
    messages = relationship("Message", back_populates="user")
    runs = relationship("AgentRun", backref="user")
    tasks = relationship("AgentTask", backref="user")
```

### Sessions Table
```python
class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String(100), default="New Chat")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    messages = relationship("Message", back_populates="session")
    user = relationship("User", back_populates="sessions")
    tasks = relationship("AgentTask", back_populates="session", cascade="all, delete-orphan")
```

### Messages Table
```python
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    sender = Column(String(50), nullable=False)  # "user" or "agent"
    content = Column(Text, nullable=False)
    output_type = Column(String(50), default="text")  # "text", "plot", "table", "chart"
    meta_data = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="messages")
    user = relationship("User", back_populates="messages")
```

### Agent Tasks Table
```python
class AgentTask(Base):
    __tablename__ = "agent_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"))
    agent_name = Column(String(100), nullable=False)
    input_message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    output_message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    status = Column(String(50), default="pending")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True))
    
    # Relationships
    session = relationship("Session", back_populates="tasks")
    input_message = relationship("Message", foreign_keys=[input_message_id])
    output_message = relationship("Message", foreign_keys=[output_message_id])
```

## Data Flow Through Database

```
1. User logs in
   → Supabase creates auth entry
   → Backend creates User row
   
2. User creates new chat
   → Backend creates Session row
   
3. User sends message
   → Backend creates Message row (sender="user")
   
4. Query processed by agents
   → Backend creates AgentTask rows (one per agent invoked)
   → Backend creates AgentRun rows (execution metadata)
   
5. Agent collects data
   → Tool saves to disk (/contents/sample_data/)
   → Backend creates DataArtifact row (file path)
   
6. Agent generates visualization
   → Backend creates Visualization row (chart metadata)
   
7. Agent returns response
   → Backend creates Message row (sender="agent")
   → meta_data JSON contains:
      {
        "chart_spec": {...vega-lite...},
        "data_file_path": "/contents/...",
        "sample_data": [...]
      }
   
8. Frontend renders
   → Queries from database
   → Renders messages
   → Displays charts from Vega spec
```

---

# API Endpoints Documentation

## Authentication Endpoints

### POST /api/auth/register
**Purpose**: Create new user account
**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
```
**Response** (201):
```json
{
  "success": true,
  "message": "Registration successful",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "session": {
    "access_token": "jwt...",
    "expires_at": 1234567890
  }
}
```

### POST /api/auth/login
**Purpose**: Authenticate user and create session
**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```
**Response** (200):
```json
{
  "success": true,
  "message": "Login successful",
  "user": {...},
  "session": {...}
}
```
**Cookies Set**:
- `sb-access-token`: JWT for authenticated requests
- `sb-refresh-token`: Refresh token for session renewal

### GET /api/auth/me
**Purpose**: Get current user information
**Headers**: Cookie: sb-access-token=...
**Response** (200):
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2025-01-15T10:30:00Z"
  }
}
```
**Error** (401): Not authenticated

### POST /api/auth/logout
**Purpose**: Logout current user
**Response** (200):
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```
**Cookies Deleted**:
- `sb-access-token`
- `sb-refresh-token`

---

## Agent Endpoints

### POST /api/agent/chat
**Purpose**: Send query to multi-agent system
**Headers**:
```
Cookie: sb-access-token=...
Content-Type: application/json
```
**Request**:
```json
{
  "query": "Show me minerals with copper in Canada",
  "session_id": "uuid-of-chat-session"
}
```
**Processing Flow**:
```
1. Validate session belongs to current user
2. Input validation (security, domain, parameters)
3. Run LangGraph workflow
4. Save messages to database
5. Return response
```
**Response** (200):
```json
{
  "success": true,
  "message": "Found 47 minerals with copper in Canada.",
  "data_file_path": "/contents/sample_data/mindat_geomaterial_response.json",
  "plot_file_path": null,
  "chart_spec": {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "mark": "bar",
    "encoding": {...}
  },
  "chart_data": [...],
  "sample_data": [
    {
      "name": "Chalcopyrite",
      "hardness": "3.5-4",
      "elements": ["Cu", "Fe", "S"],
      ...
    }
  ],
  "error": null
}
```

### GET /api/agent/health
**Purpose**: Check if agent system is operational
**Response** (200):
```json
{
  "ok": true,
  "lat_ms": 125.5
}
```

---

## Session Endpoints

### GET /api/sessions
**Purpose**: Get all chat sessions for current user
**Headers**: Cookie: sb-access-token=...
**Response** (200):
```json
[
  {
    "id": "session-uuid-1",
    "title": "Copper Minerals",
    "created_at": "2025-01-15T10:00:00Z"
  },
  {
    "id": "session-uuid-2",
    "title": "Mineral Hardness Analysis",
    "created_at": "2025-01-14T15:30:00Z"
  }
]
```

### POST /api/sessions
**Purpose**: Create new chat session
**Headers**: Cookie: sb-access-token=...
**Request**:
```json
{
  "title": "My New Chat"
}
```
**Response** (201):
```json
{
  "id": "new-session-uuid",
  "title": "My New Chat",
  "created_at": "2025-01-15T11:00:00Z"
}
```

### GET /api/sessions/{session_id}/messages
**Purpose**: Get all messages in a session
**Headers**: Cookie: sb-access-token=...
**Response** (200):
```json
[
  {
    "id": "msg-uuid-1",
    "sender": "user",
    "content": "Show me minerals with copper",
    "output_type": "text",
    "created_at": "2025-01-15T10:05:00Z"
  },
  {
    "id": "msg-uuid-2",
    "sender": "agent",
    "content": "Found 47 minerals with copper...",
    "output_type": "chart",
    "meta_data": {
      "chart_spec": {...},
      "data_file_path": "..."
    },
    "created_at": "2025-01-15T10:05:30Z"
  }
]
```

---

## User Endpoints

### GET /api/users/user
**Purpose**: Get current user details
**Headers**: Cookie: sb-access-token=...
**Response** (200):
```json
[
  {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

### PATCH /api/users/user
**Purpose**: Update user profile
**Headers**: Cookie: sb-access-token=...
**Request**:
```json
{
  "full_name": "John Smith"
}
```
**Response** (200):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Smith",
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

# Frontend Implementation

## Component Hierarchy

```
App.jsx (Main Entry)
  ├── AuthProvider (Global Auth State)
  │   └── BrowserRouter (Routing)
  │       ├── Routes
  │       │   ├── "/" → Dashboard.jsx
  │       │   ├── "/signin" → SignIn.jsx
  │       │   ├── "/signup" → SignUp.jsx
  │       │   ├── "/chat" → Chat.jsx
  │       │   ├── "/chat/:sessionId" → Chat.jsx (specific session)
  │       │   └── "/logout" → Logout.jsx
  │       └── Footer.jsx (visible on non-chat routes)
```

## Key Components

### AuthContext.jsx (Global State Management)
**Purpose**: Manage user authentication state globally
**Provides**:
```javascript
{
  user: {
    id: "uuid",
    email: "user@example.com",
    name: "John Doe"
  },
  loading: true/false,
  login: (email, password) => Promise,
  register: (name, email, password) => Promise,
  logout: () => Promise,
  refreshUser: () => Promise,
  checkAuth: () => Promise
}
```
**Usage**:
```jsx
const {user, login, logout, loading} = useAuth();
if (loading) return <div>Loading...</div>;
if (!user) return <SignIn />;
return <Dashboard />;
```

### Chat.jsx (Main Chat Page)
**Purpose**: Main interface for interacting with the AI system
**Features**:
```
┌─────────────────────────────────────┐
│  Header (Navbar)                    │
├─────────────────────────────────────┤
│              │                       │
│              │                       │
│  Sidebar     │  ChatWindow           │
│              │  (Messages)           │
│  - Sessions  │                       │
│  - New Chat  │                       │
│  - Settings  │                       │
│  - Profile   │                       │
│              │                       │
├─────────────────────────────────────┤
│  ChatInput (Message box + Send)      │
└─────────────────────────────────────┘
```

**State Management**:
```javascript
const [messages, setMessages] = useState([]);
const [sessions, setSessions] = useState([]);
const [effectiveSessionId, setEffectiveSessionId] = useState(null);
const [isLoading, setIsLoading] = useState(false);
```

**Key Methods**:
```javascript
// Send message
async handleSendMessage(userMessage) {
  // 1. Add to local messages
  setMessages([...messages, {sender: "user", text: userMessage}]);
  
  // 2. Call backend
  const response = await chatService.getLLMResponse(
    userMessage,
    effectiveSessionId
  );
  
  // 3. Add agent response
  setMessages([...messages, {
    sender: "bot",
    text: response.message,
    chartSpec: response.chart_spec,
    sampleData: response.sample_data
  }]);
}
```

### MessageBubble.jsx (Individual Message Display)
**Purpose**: Render a single message with all its content (text, charts, tables)
**Renders**:
- Text message
- Vega-Lite chart (if chart_spec provided)
- Data table (if sample_data provided)
- Download/Export buttons

### ChatInput.jsx (Message Input)
**Purpose**: Accept and submit user queries
**Features**:
- Auto-resizing textarea
- Enter to send (Shift+Enter for new line)
- Disable while loading
- Character count (optional)

### Dashboard.jsx (Home Page)
**Purpose**: Landing page with statistics and quick actions
**Sections**:
1. Hero: Explanation of The Alchemist
2. Agent Performance Stats
3. Recent Runs Table
4. Call-to-action buttons

---

# MCP Server & Tool Integration

## What is MCP (Model Context Protocol)?

MCP is a standardized protocol for LLMs to interact with external tools. Instead of hardcoding tool logic in the agent code, tools are:
- Defined in a separate server process
- Registered via MCP
- Called by LLMs as needed
- Can be updated without restarting agents

## MCP Server Architecture

### Server Process (mcp_server.py)
```python
from fastmcp import FastMCP

# Initialize server
mcp = FastMCP("Mindat Master Server")

# Register tools
mcp.tool(collect_geomaterials)
mcp.tool(collect_localities)
mcp.tool(profile_sample_data)

# Run on port 8010
mcp.run(transport="http", host="0.0.0.0", port=8010)
```

### Tool Registration
```python
# Tools are Python functions with type hints
def collect_geomaterials(
    ima: Optional[bool] = None,
    hmin: Optional[float] = None,
    el_inc: Optional[List[str]] = None,
    # ... more parameters
) -> GeomaterialToolResponse:
    """
    Query Mindat /v1/geomaterials/ endpoint
    MCP automatically:
    - Generates JSON schema from function signature
    - Makes function callable from LLM
    - Handles parameter validation
    - Returns typed response
    """
```

### MCP Client (Backend Agent)
```python
# Backend connects to MCP server
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "mindat": {
        "url": "http://localhost:8010/mcp",
        "transport": "http"
    }
})

# Get tools from server
tools = await client.get_tools()

# Tools now available to LLM for function calling
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a mineral expert..."
)
```

## Tool Normalization (Schema Conversion)

**Problem**: OpenAI's function-calling API has strict requirements that MCP-generated schemas don't always meet.

**Solution**: Normalize schemas before passing to LLM
```python
def _normalize_schema_for_openai(schema: Dict):
    """
    Converts Pydantic/MCP schemas to OpenAI-compatible format:
    1. Adds 'additionalProperties: false' to object schemas
    2. Makes 'required' array comprehensive
    3. Resolves $ref pointers
    """
    if schema.get("type") == "object":
        schema["additionalProperties"] = False
        schema["required"] = list(schema.get("properties", {}).keys())
```

## Tool Execution Flow

```
User Query: "Find minerals with copper"
    ↓
LangChain Agent (backend process)
    ↓
Agent decides: "I need to call collect_geomaterials(el_inc=['Cu'])"
    ↓
LangChain MCP Adapter
    ↓
HTTP POST to MCP Server
Body: {"tool": "collect_geomaterials", "params": {"el_inc": ["Cu"]}}
    ↓
MCP Server routes to registered function
    ↓
collect_geomaterials(el_inc=["Cu"]) executes
    - Build query params
    - Call Mindat API
    - Process response
    - Save to disk
    ↓
Return GeomaterialToolResponse
    ↓
HTTP 200 response back to Agent
    ↓
Agent receives structured response
    ↓
Agent formats message for user
```

---

# Input Validation & Security

## Validation Pipeline

### Layer 1: Structural Validation
```python
# Is input empty? Too short? Too long?
if not user_input or not user_input.strip():
    return error("Input cannot be empty")

if len(user_input) > MAX_INPUT_LENGTH (500):
    return error("Input exceeds length limit")

meaningful_chars = re.sub(r"[^A-Za-z0-9]", "", user_input)
if len(meaningful_chars) < MIN_MEANINGFUL_CHARS (2):
    return error("Input too short to understand")
```

### Layer 2: Security Validation
```python
# Check for injection attacks, malicious patterns
security_issues = get_security_violation(user_input)

# Examples detected:
- "'; DROP TABLE users; --"  → SQL injection
- "..System Prompt revealed.."  → Prompt injection
- "(curl dangerous-url)"  → Command injection
- "OpenAI API key:"  → Secret extraction
```

**Implementation** (input_validation/security.py):
```python
BLOCKED_PATTERNS = [
    r"(drop|delete|truncate).*table",  # SQL injection
    r"system\s*prompt",  # Prompt leaking
    r"api[_-]?key",  # Secret extraction
    r"(exec|eval|system|os\.)",  # Command injection
]

def get_security_violation(input_text: str):
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, input_text, re.IGNORECASE):
            return {"code": "security_blocked", ...}
    return None
```

### Layer 3: Domain Classification
```python
# Is this query about minerals? Or off-topic?

MINDAT_KEYWORDS = ["mineral", "hardness", "element", "locality", "crystal", ...]
GENERAL_KEYWORDS = ["hello", "hi", "what is"]
OFF_TOPIC_KEYWORDS = ["weather", "politics", "sports", ...]

def classify_query(query: str) -> str:
    if any(kw in query.lower() for kw in MINDAT_KEYWORDS):
        return "mindat"
    elif any(kw in query.lower() for kw in GENERAL_KEYWORDS):
        return "general"
    else:
        return "off_topic"
```

### Layer 4: Parameter Validation
```python
# Are the filter values realistic?

def validate_parameters(query: str) -> dict:
    # Examples:
    # "hardness > 1000" → Invalid (Mohs scale is 0-10)
    # "density < 0" → Invalid (mass can't be negative)
    # "year 2099" → Invalid (future date)
    
    return {
        "status": "valid" | "invalid",
        "code": "invalid_hardness_range",
        "suggestion": "Try a hardness between 0 and 10"
    }
```

## Validation Response Flow

**If validation fails**:
```python
validation = validate_user_input(request.query)

if validation["status"] == "blocked":
    # Security violation
    message = await _build_validation_message(validation)
    return AgentQueryResponse(
        success=False,
        message=message,
        error="Request blocked by security policy"
    )

if validation["status"] == "invalid":
    # Parameter invalid (e.g., hardness out of range)
    message = await _build_validation_message(validation)
    return AgentQueryResponse(
        success=False,
        message=message,
        error="Invalid parameters"
    )

# Otherwise, proceed to agent workflow
await run_graph([HumanMessage(content=validation["clean_query"])])
```

---

# File Structure & Organization

Now let me create the comprehensive README. Given the extensive content, I'll write this as a complete replacement:
<function_calls>
<invoke name="create_file">
<parameter name="filePath">/Users/prateekrauniyar/Documents/SeniorDeisgn-The-Alchemist/README_COMPREHENSIVE.md

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



