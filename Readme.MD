# The Alchemist

## 📌 Overview

**The Alchemist** is a full-stack application that leverages **LangChain**, **LangGraph**, and **LangSmith** to build an intelligent, AI-powered system for exploring mineral data. The application uses:

- **FastAPI** as the backend framework.
- **LangChain + LangGraph** for building a multi-agent workflow to query, analyze, and visualize mineral data.
- **LangSmith** for monitoring agent behavior, tracking execution flow, and debugging.
- REST API endpoints to fetch data from **Mindat.org**, a well-known mineral database.

The application allows users to:

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


## 📌 Next Steps

- Deploy the app using Docker or a cloud provider (e.g., AWS, Vercel).
- Implement full user authentication and permissions.
- Add a dashboard for monitoring agent activity via **LangSmith**.

---

