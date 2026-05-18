# AI Application Architecture — From Simple to Production

---

## The Spectrum of AI App Complexity

```
Simple Chatbot ──► RAG App ──► Single Agent ──► Multi-Agent System ──► Autonomous AI System
     │                │              │                  │                       │
  1 LLM call     LLM + docs    LLM + tools       Many LLMs + tools        Continuous loop
  Stateless       Memory        Loops             Orchestration            Self-directed
```

---

## Tier 1: Simple LLM Application

The most basic pattern — one API call, one response.

### Architecture

```
User Input
    │
    ▼
┌─────────────────────────────┐
│  Application Layer          │
│  ┌──────────────────────┐   │
│  │  System Prompt       │   │   (Instructions for the LLM)
│  │  + User Message      │   │
│  └──────────┬───────────┘   │
└─────────────┼───────────────┘
              │ HTTPS API call
              ▼
┌─────────────────────────────┐
│  LLM Provider               │
│  (Claude / OpenAI / etc.)   │
└─────────────────────────────┘
              │
              ▼
        Response Text
              │
              ▼
     Display to User
```

### Use Cases
- Summarization tool
- Email drafter
- Code explainer
- Simple Q&A chatbot

### What you need to build this
- API key from Anthropic / OpenAI
- Python or JavaScript
- HTTP requests (or SDK)

### Example Code (Python + Claude)
```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="You are a helpful assistant specialized in financial analysis.",
    messages=[
        {"role": "user", "content": "Summarize the key risks in this report: ..."}
    ]
)
print(response.content[0].text)
```

---

## Tier 2: RAG Application (Retrieval Augmented Generation)

### Architecture

```
                    INDEXING PIPELINE (run once / on schedule)
                    ─────────────────────────────────────────
Documents ──► Loader ──► Chunker ──► Embedding Model ──► Vector Store


                    QUERY PIPELINE (run per user query)
                    ────────────────────────────────────
User Query
    │
    ├──► Embedding Model ──► Query Vector
    │                              │
    │                              ▼
    │                    ┌─────────────────┐
    │                    │  Vector Store   │ ──► Top-K Chunks
    │                    └─────────────────┘
    │                              │
    ▼                              ▼
┌────────────────────────────────────────┐
│  Prompt Assembly                       │
│  System + User Query + Retrieved Docs  │
└───────────────────┬────────────────────┘
                    │
                    ▼
             LLM (Claude/GPT)
                    │
                    ▼
              Final Answer
```

### Components and Technology Choices

| Layer | Options |
|-------|---------|
| Document Loaders | LangChain, LlamaIndex, Unstructured.io |
| Embedding Model | OpenAI text-embedding-3, Cohere embed, sentence-transformers |
| Vector Store | Chroma (local), Pinecone (cloud), pgvector (Postgres) |
| LLM | Claude Sonnet/Opus, GPT-4o, Gemini |
| Orchestration | LangChain, LlamaIndex, custom Python |
| Frontend | Streamlit, Gradio, Next.js, FastAPI |

### When to use RAG
- Your app needs to answer from **private/internal documents**
- Data changes frequently (reindex rather than retrain)
- You need the LLM to cite sources
- The knowledge base is too large to fit in context window

---

## Tier 3: Single Agent with Tools

### Architecture

```
User Goal
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│  Agent Loop                                              │
│                                                          │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────┐ │
│  │  LLM Core   │◄──►│    Memory    │    │   Planner   │ │
│  └──────┬──────┘    └──────────────┘    └─────────────┘ │
│         │                                                │
│         │ Tool Call Request                              │
│         ▼                                                │
│  ┌──────────────────────────────────────────────┐       │
│  │  Tool Router                                 │       │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │       │
│  │  │Web Search│ │Code Exec │ │DB Query      │ │       │
│  │  └──────────┘ └──────────┘ └──────────────┘ │       │
│  └──────────────────────────────────────────────┘       │
│         │ Tool Result                                    │
│         └──► Back to LLM ──► Continue or Final Answer   │
└──────────────────────────────────────────────────────────┘
```

### Memory Types in Agents
| Memory Type | Storage | Scope |
|-------------|---------|-------|
| **Working Memory** | Current conversation context window | Current task only |
| **Short-term Memory** | Conversation history in DB | Current session |
| **Long-term / Semantic Memory** | Vector store | Persists across sessions |
| **Episodic Memory** | Log of past events/actions | Learning over time |

### Tool Types Agents Can Use
| Tool | Example |
|------|---------|
| **Search** | Web search, semantic search |
| **Code Execution** | Python sandbox, SQL queries |
| **File I/O** | Read/write documents |
| **API Calls** | REST APIs, GraphQL |
| **Browser** | Web scraping, automation |
| **Database** | Query structured data |
| **Email/Calendar** | Send emails, schedule |
| **MCP Servers** | Any MCP-compatible tool |

---

## Tier 4: Multi-Agent System

### Architecture

```
User Request
     │
     ▼
┌─────────────────────────────────────────────────────┐
│  Orchestrator Agent                                 │
│  - Understands the goal                             │
│  - Breaks into sub-tasks                            │
│  - Assigns to specialist agents                     │
│  - Aggregates results                               │
└──────┬───────────────┬──────────────────┬───────────┘
       │               │                  │
       ▼               ▼                  ▼
┌──────────┐   ┌──────────────┐   ┌──────────────┐
│ Research │   │   Analysis   │   │   Writing    │
│  Agent   │   │    Agent     │   │    Agent     │
│(web tool)│   │(code + data) │   │(LLM + docs)  │
└──────────┘   └──────────────┘   └──────────────┘
       │               │                  │
       └───────────────┴──────────────────┘
                       │
                       ▼
              Aggregated Output
                       │
              ┌────────────────┐
              │ Review / Guard │  (optional validator agent)
              └────────────────┘
                       │
                       ▼
              Final Response to User
```

### Communication Patterns
| Pattern | Description |
|---------|-------------|
| **Sequential** | Agent A → Agent B → Agent C (pipeline) |
| **Parallel** | All agents run simultaneously, results merged |
| **Hierarchical** | Orchestrator + specialist tree |
| **Peer-to-Peer** | Agents communicate directly with each other |

---

## Full Production Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│  CLIENT LAYER                                                      │
│  Web App / Mobile App / API Consumer                               │
└───────────────────────────────┬────────────────────────────────────┘
                                │ HTTPS
┌───────────────────────────────▼────────────────────────────────────┐
│  API GATEWAY / BACKEND                                             │
│  FastAPI / Next.js API Routes / Express                            │
│  - Auth (JWT / OAuth)                                              │
│  - Rate limiting                                                   │
│  - Request routing                                                 │
└─────────┬─────────────────────────────────────┬────────────────────┘
          │                                     │
┌─────────▼──────────┐               ┌──────────▼───────────────────┐
│  AGENT / RAG CORE  │               │  DATA LAYER                  │
│                    │               │  ┌────────────────────────┐  │
│  Orchestrator      │◄──────────────┤  │ Vector Store           │  │
│  Agent(s)          │               │  │ (Pinecone/Chroma)      │  │
│  Tool Router       │               │  └────────────────────────┘  │
│  Memory Manager    │               │  ┌────────────────────────┐  │
│                    │               │  │ Relational DB           │  │
│  LangChain /       │               │  │ (Postgres/MySQL)        │  │
│  LlamaIndex /      │               │  └────────────────────────┘  │
│  Custom            │               │  ┌────────────────────────┐  │
└─────────┬──────────┘               │  │ Document Store          │  │
          │                          │  │ (S3/Blob/local)         │  │
┌─────────▼──────────┐               │  └────────────────────────┘  │
│  LLM PROVIDER(S)   │               └──────────────────────────────┘
│  Claude API        │
│  OpenAI API        │               ┌──────────────────────────────┐
│  (via SDK)         │               │  OBSERVABILITY               │
└────────────────────┘               │  LangSmith / Langfuse        │
                                     │  Logging / Tracing           │
┌───────────────────────────────┐    │  Cost tracking               │
│  MCP SERVERS (optional)       │    └──────────────────────────────┘
│  - File system MCP            │
│  - GitHub MCP                 │    ┌──────────────────────────────┐
│  - Database MCP               │    │  GUARDRAILS                  │
│  - Custom tool MCPs           │    │  Input validation            │
└───────────────────────────────┘    │  Output filtering            │
                                     │  PII detection               │
                                     └──────────────────────────────┘
```

---

## Key Architecture Decisions

### Decision 1: RAG vs Fine-tuning vs Context Stuffing

| Approach | When to use | Cost | Freshness |
|----------|-------------|------|-----------|
| **Context Stuffing** | Small dataset, <100K tokens | Low | Always fresh |
| **RAG** | Large/dynamic dataset | Medium | Fresh on re-index |
| **Fine-tuning** | Specific style/behavior | High | Static (retrain) |

**Recommendation:** Start with RAG. Fine-tune only if style/format is the issue.

### Decision 2: Which LLM?

| Model | Best for | Speed | Cost |
|-------|---------|-------|------|
| Claude Haiku | Simple tasks, high volume | Fastest | Cheapest |
| Claude Sonnet | Most tasks, balanced | Fast | Mid |
| Claude Opus | Complex reasoning, critical tasks | Slower | Highest |
| GPT-4o | If OpenAI ecosystem needed | Fast | Mid |
| Llama 3 (local) | Privacy-first, on-prem | Variable | Infrastructure |

### Decision 3: Agent Framework

| Need | Framework |
|------|-----------|
| Quick prototype | LangChain + simple tools |
| Complex RAG | LlamaIndex |
| Multi-agent systems | LangGraph or CrewAI |
| Native Claude agents | Anthropic Agent SDK |
| Production + observability | LangGraph + LangSmith |

---

## What You MUST Know to Build AI Apps

### Must-Have Skills
1. **Python** (primary language for AI/ML ecosystem)
2. **REST API basics** (calling LLM APIs, handling JSON responses)
3. **Prompt engineering** (crafting system prompts, few-shot examples)
4. **Basic async programming** (streaming, concurrent tool calls)
5. **Environment variables** (keeping API keys out of code)
6. **Git** (version control)

### Good to Have
1. SQL — for structured data retrieval
2. Docker — deploying your app
3. FastAPI / Flask — building API backends
4. React / Next.js — building frontends
5. Cloud basics (AWS/Azure/GCP) — hosting your app

### AI-Specific Skills to Learn
1. Embedding models and vector search
2. LangChain or LlamaIndex
3. Prompt engineering patterns
4. Token counting and cost estimation
5. Streaming responses
6. Function/tool calling
7. Structured output (JSON mode)

---

*Next: See `03_LearningPath.md` for a step-by-step guide to building your first AI app.*
