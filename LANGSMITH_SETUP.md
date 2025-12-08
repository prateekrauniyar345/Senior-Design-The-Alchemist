# LangSmith Tracing Setup Guide

## ✅ What's Been Configured

All key components now have `@traceable` decorators for complete observability:

### 🛠️ Tools (5 functions traced)
- `mindat_geomaterial_collector` - Geomaterial data collection
- `mindat_locality_collector` - Locality data collection  
- `pandas_hist_plot` - Histogram visualization
- `network_plot` - Network graph visualization
- `heatmap_plot` - Geographic heatmap visualization

### 🤖 Agent Nodes (6 nodes traced)
- `supervisor_decision` - AI-powered routing logic
- `geomaterial_collector_agent` - Geomaterial collection workflow
- `locality_collector_agent` - Locality collection workflow
- `histogram_plotter_agent` - Histogram plotting workflow
- `network_plotter_agent` - Network plotting workflow
- `heatmap_plotter_agent` - Heatmap plotting workflow

### 🌐 API Endpoints (3 methods traced)
- `agent_chat_endpoint` - Main chat interface
- `mindat_api_geomaterial_search` - Mindat geomaterial API calls
- `mindat_api_locality_search` - Mindat locality API calls

### 🔧 Helper Functions (1 function traced)
- `convert_params_to_api_format` - Query parameter conversion

---

## 🚀 Setup Instructions

### 1. Add Environment Variables

Add these to your `Backend/.env` file:

```bash
# LangSmith Tracing Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="<your-langsmith-api-key>"
LANGCHAIN_PROJECT="pr-wilted-countess-63"  # or your custom project name
```

### 2. Get Your API Key

1. Go to https://smith.langchain.com/
2. Sign up or log in
3. Navigate to **Settings** → **API Keys**
4. Click **Create API Key**
5. Copy the key and add it to your `.env` file

### 3. Test Your Configuration

Run the test script:

```bash
cd Backend
python test_langsmith_tracing.py
```

You should see:
```
✅ ALL TESTS PASSED!
🎉 LangSmith tracing is fully configured
```

### 4. Start Your Application

```bash
# Terminal 1: Start Backend
cd Backend
uvicorn main:app --reload

# Terminal 2: Start Frontend
cd Frontend
npm run dev
```

### 5. View Traces

1. Send a query through your chat interface (e.g., "Find IMA minerals")
2. Go to https://smith.langchain.com/
3. Select your project (default: `pr-wilted-countess-63`)
4. View the complete trace tree

---

## 📊 What You'll See in LangSmith

### Example Trace Tree

```
📊 User Query: "Plot histogram of IMA minerals"
  ├─ 🔄 agent_chat_endpoint (2.3s)
  │  └─ 🤖 LangGraph Workflow
  │     ├─ 🧠 supervisor_decision (0.8s)
  │     │  ├─ LLM Call: GPT-4
  │     │  └─ Decision: geomaterial_collector
  │     │
  │     ├─ 🔧 geomaterial_collector_agent (1.2s)
  │     │  └─ 🛠️ mindat_geomaterial_collector_execution (1.1s)
  │     │     ├─ convert_params_to_api_format (0.01s)
  │     │     └─ 🌐 mindat_api_geomaterial_search (1.0s)
  │     │        └─ HTTP Request: GET /geomaterials
  │     │
  │     ├─ 🧠 supervisor_decision (0.7s)
  │     │  ├─ LLM Call: GPT-4
  │     │  └─ Decision: histogram_plotter
  │     │
  │     ├─ 📊 histogram_plotter_agent (0.5s)
  │     │  └─ 🛠️ histogram_plot_execution (0.4s)
  │     │     └─ Created: mineral_histogram_20251207_161022.png
  │     │
  │     └─ 🧠 supervisor_decision (0.6s)
  │        └─ Decision: FINISH
  │
  └─ ✅ Response: Success with plot URL
```

### Trace Details Include:

- ⏱️ **Timing**: Duration for each step
- 📝 **Inputs/Outputs**: Full request and response data
- 🔗 **Relationships**: Parent-child trace hierarchy
- ⚠️ **Errors**: Stack traces and error context
- 💰 **Costs**: Token usage and API costs
- 🏷️ **Metadata**: Custom tags and annotations

---

## 🎯 Benefits

### 1. Debugging
- See exact flow through your multi-agent system
- Identify which agent is failing and why
- View full error stack traces with context

### 2. Performance Optimization
- Find bottlenecks in your agent workflow
- See which API calls are slowest
- Optimize tool execution times

### 3. Cost Tracking
- Monitor LLM token usage per query
- Track API costs over time
- Identify expensive operations

### 4. Quality Monitoring
- Compare different prompts and models
- A/B test agent configurations
- Track success rates over time

---

## 🔍 Advanced Features

### Custom Tags

Add tags to traces for better filtering:

```python
from langsmith import traceable

@traceable(tags=["production", "high-priority"])
def my_function():
    pass
```

### Run Metadata

Add custom metadata to traces:

```python
@traceable(metadata={"user_id": "123", "query_type": "visualization"})
def my_function():
    pass
```

### Feedback Tracking

Add user feedback to traces programmatically:

```python
from langsmith import Client

client = Client()
client.create_feedback(
    run_id="<trace-run-id>",
    key="user_rating",
    score=1.0,  # 0.0 to 1.0
    comment="Great visualization!"
)
```

---

## 📚 Additional Resources

- **LangSmith Docs**: https://docs.smith.langchain.com/
- **Tracing Guide**: https://docs.smith.langchain.com/tracing
- **Best Practices**: https://docs.smith.langchain.com/best_practices
- **API Reference**: https://api.smith.langchain.com/redoc

---

## ⚠️ Troubleshooting

### Traces Not Appearing?

1. **Check environment variables**:
   ```bash
   cd Backend
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('LANGCHAIN_TRACING_V2'))"
   ```
   Should print: `true`

2. **Verify API key**:
   - Log in to https://smith.langchain.com/
   - Check that your API key is active
   - Regenerate if needed

3. **Check network connectivity**:
   ```bash
   curl https://api.smith.langchain.com/
   ```
   Should return: `{"status":"ok"}`

4. **Review server logs**:
   - Look for LangSmith-related errors
   - Check for import errors

### Slow Trace Upload?

- Traces are sent asynchronously in the background
- They may take a few seconds to appear in the UI
- Check the "Pending" filter in LangSmith

### Missing Traces?

- Ensure `LANGCHAIN_TRACING_V2=true` (not `"True"` or `"yes"`)
- Restart your server after changing `.env`
- Check that `langsmith` package is installed: `pip show langsmith`

---

## 🎉 You're All Set!

Your multi-agent system now has complete observability. Every tool call, agent decision, and API request is traced and visible in LangSmith.

**Next Steps:**
1. ✅ Add environment variables to `.env`
2. ✅ Run `python test_langsmith_tracing.py`
3. ✅ Start your servers
4. ✅ Send a test query
5. ✅ View traces at https://smith.langchain.com/

Happy debugging! 🚀
