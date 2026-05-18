# AI Application Development — Core Terminology

---

## 1. LLM — Large Language Model

### What is it?
A Large Language Model is a deep learning model trained on massive amounts of text data (books, web, code, research) to understand and generate human language.

### How it works
- Trained using **transformers** — a neural network architecture that learns attention (which words/tokens matter relative to others)
- Input text is split into **tokens** (roughly 3/4 of a word each)
- The model predicts the next token, one at a time, building up a response

### Key Concepts
| Term | Meaning |
|------|---------|
| **Token** | Smallest unit of text the model processes (~¾ word) |
| **Context Window** | Max tokens the model can "see" at once (e.g. 200K tokens for Claude) |
| **Temperature** | Controls randomness: 0 = deterministic, 1+ = creative |
| **Prompt** | The input/instruction you send to the model |
| **Completion / Response** | The model's output |
| **System Prompt** | Background instructions that shape behavior before user input |
| **Fine-tuning** | Further training on domain-specific data to specialize behavior |
| **Inference** | Running the model to get a response (as opposed to training) |

### Popular LLMs
| Model | Provider |
|-------|----------|
| Claude (Opus, Sonnet, Haiku) | Anthropic |
| GPT-4o, o1, o3 | OpenAI |
| Gemini 1.5 / 2.0 | Google |
| Llama 3.x | Meta (open source) |
| Mistral / Mixtral | Mistral AI (open source) |

### What can LLMs do?
- Text generation, summarization, translation
- Code generation and debugging
- Question answering
- Classification and sentiment analysis
- Structured data extraction

---

## 2. RAG — Retrieval Augmented Generation

### What is it?
RAG is a technique to give an LLM access to **your own data** without retraining it. Instead of baking knowledge into the model weights, you fetch relevant documents at query time and inject them into the prompt.

### Why is it needed?
LLMs have a knowledge cutoff (they don't know recent events or your private data). RAG bridges this gap.

### How it works — Step by Step

```
User Query
    │
    ▼
[Embedding Model] ──► Convert query to vector
    │
    ▼
[Vector Database] ──► Search for top-K similar document chunks
    │
    ▼
[Context Assembly] ──► Inject retrieved chunks into the prompt
    │
    ▼
[LLM] ──► Generate answer grounded in retrieved context
    │
    ▼
Response to User
```

### Key Components
| Component | Role | Examples |
|-----------|------|---------|
| **Document Loader** | Ingest PDFs, Word docs, web pages | LangChain loaders, Unstructured |
| **Chunker** | Split documents into manageable pieces | LangChain TextSplitter |
| **Embedding Model** | Convert text to numeric vectors | OpenAI ada-002, Cohere, sentence-transformers |
| **Vector Store** | Store and search embeddings | Pinecone, Weaviate, Chroma, pgvector, FAISS |
| **Retriever** | Find top-K relevant chunks for a query | Cosine similarity, MMR, BM25 hybrid |
| **LLM** | Generate the final answer | Claude, GPT-4, Gemini |

### RAG Pipeline Terminology
| Term | Meaning |
|------|---------|
| **Embedding** | A dense numeric vector representing semantic meaning of text |
| **Vector Search** | Finding similar embeddings via distance math (cosine, dot product) |
| **Chunking** | Splitting long documents into ~500–1000 token pieces for indexing |
| **Top-K Retrieval** | Fetching the K most relevant chunks (typically K=3–10) |
| **Re-ranking** | A second pass to improve chunk ordering before feeding to LLM |
| **Grounding** | LLM answer is based on retrieved facts, not hallucinated |
| **Hallucination** | LLM generating plausible but factually wrong information |

---

## 3. Agentic AI / AI Agents

### What is it?
An AI Agent is an LLM that can **reason, plan, and take actions** — not just answer questions. It can call tools, browse the web, write and run code, and iterate toward a goal.

### Core Loop (ReAct Pattern)
```
Observe ──► Think ──► Act ──► Observe ──► Think ──► Act ...
```

The agent sees the current state, reasons about what to do, calls a tool, gets the result, then reasons again — until the goal is reached.

### Key Concepts
| Term | Meaning |
|------|---------|
| **Tool / Function Calling** | LLM can invoke external functions (search, DB query, API call) |
| **Tool Use** | The mechanism by which an LLM returns structured JSON to trigger a function |
| **Planning** | Breaking a complex goal into sub-tasks (e.g. chain-of-thought) |
| **Memory** | Storing context beyond the current conversation (episodic, semantic, working) |
| **Orchestration** | Managing which agent/tool runs when and passing results between them |
| **Multi-Agent System** | Multiple specialized agents collaborating on a task |
| **Guardrails** | Rules/checks to prevent the agent from doing harmful things |
| **Human-in-the-loop** | Pausing for human approval at critical decision points |

### Agent Architectures
| Pattern | Description |
|---------|-------------|
| **Single Agent** | One LLM with multiple tools |
| **ReAct** | Reason + Act loop with tool calls |
| **Plan-and-Execute** | Separate planning step, then execution agent |
| **Multi-Agent** | Orchestrator delegates to specialist sub-agents |
| **Supervisor** | One agent reviews/validates another agent's work |

### Popular Agent Frameworks
| Framework | Language | Notes |
|-----------|----------|-------|
| LangChain / LangGraph | Python/JS | Most popular, rich ecosystem |
| CrewAI | Python | Role-based multi-agent |
| AutoGen | Python | Microsoft, conversational multi-agent |
| LlamaIndex | Python | Strong RAG + agent integration |
| Anthropic Agent SDK | Python | Native Claude agents |

---

## 4. MCP — Model Context Protocol

### What is it?
MCP is an **open standard protocol** created by Anthropic (2024) that defines how AI models connect to external tools, data sources, and services in a standardized, pluggable way.

Think of MCP as **USB for AI** — any AI host that speaks MCP can plug in any MCP server without custom integration code.

### The Problem MCP Solves
Before MCP: every AI app had to write custom code to connect to each tool (Slack, GitHub, databases, etc.). This created a fragmented N×M integration problem.

After MCP: one standard protocol. Any LLM + any tool. Write it once.

### MCP Architecture

```
┌─────────────────────────────────┐
│         MCP Host                │   (e.g. Claude Desktop, Claude Code, your app)
│  ┌──────────────┐               │
│  │  LLM Client  │               │
│  └──────┬───────┘               │
│         │ MCP Protocol          │
└─────────┼───────────────────────┘
          │
    ┌─────┴──────┐
    │            │
┌───▼───┐   ┌───▼───┐   ┌───────┐
│MCP    │   │MCP    │   │MCP    │
│Server │   │Server │   │Server │
│(Files)│   │(Git)  │   │(DB)   │
└───────┘   └───────┘   └───────┘
```

### MCP Core Concepts
| Concept | Description |
|---------|-------------|
| **Host** | The application running the LLM (e.g. Claude Desktop, your app) |
| **Client** | Lives inside the host, manages connections to MCP servers |
| **Server** | Exposes tools/resources/prompts via the MCP protocol |
| **Transport** | How host and server communicate: stdio (local) or SSE/HTTP (remote) |
| **Tool** | A callable function exposed by a server (e.g. `read_file`, `run_query`) |
| **Resource** | Data the server exposes for the LLM to read (files, DB rows) |
| **Prompt** | Pre-built prompt templates the server provides |

### MCP vs Traditional Tool Use
| Feature | Tool Use (ad hoc) | MCP |
|---------|-------------------|-----|
| Discovery | Manual/hardcoded | Automatic via protocol |
| Reusability | Low | High — any host works |
| Standardization | None | Full protocol spec |
| Security | Per-app | Consistent sandboxing |

---

## 5. Prompt Engineering

### What is it?
The practice of crafting inputs to an LLM to get the best, most reliable outputs.

### Key Techniques
| Technique | Description |
|-----------|-------------|
| **Zero-shot** | Ask directly, no examples |
| **Few-shot** | Provide 2–5 examples before asking |
| **Chain-of-Thought (CoT)** | Ask model to "think step by step" — improves reasoning |
| **Role Prompting** | "You are an expert in X..." to prime behavior |
| **Output Format** | "Return JSON with keys: name, date, amount" |
| **Retrieval Prompting** | Inject retrieved documents into the prompt (RAG) |

---

## 6. Embeddings

A technique to convert text (or images, audio) into a fixed-size numeric vector that captures **semantic meaning**. Similar texts have vectors that are close together in vector space.

Used heavily in: RAG, semantic search, classification, clustering.

---

## 7. Vector Database

A database optimized to store and search high-dimensional embedding vectors. Supports similarity search (find documents closest to a query vector).

| Database | Type | Notes |
|----------|------|-------|
| **Pinecone** | Managed cloud | Easy to start |
| **Weaviate** | Open source / cloud | Rich metadata filtering |
| **Chroma** | Open source local | Best for prototyping |
| **FAISS** | In-memory library | Facebook, no persistence |
| **pgvector** | Postgres extension | Use if you already have Postgres |
| **Qdrant** | Open source / cloud | High performance |

---

## 8. Other Important Terms

| Term | Meaning |
|------|---------|
| **API** | How your code talks to an LLM service (HTTP REST calls) |
| **SDK** | Library that wraps the API for your language (Python, JS, etc.) |
| **Streaming** | Getting tokens back one-by-one as they're generated |
| **Function Calling** | LLM returns a JSON call spec for your code to execute |
| **Structured Output** | LLM constrained to return valid JSON matching a schema |
| **Context Stuffing** | Putting all relevant data directly in the prompt (alternative to RAG) |
| **Fine-tuning** | Retraining model weights on your data (expensive, usually unnecessary) |
| **Inference API** | Calling a hosted model vs running locally |
| **Semantic Search** | Search by meaning, not keyword matching |
| **Knowledge Graph** | Structured graph of entities and relationships (alternative to vector store) |
| **LangChain** | Popular Python framework for building LLM applications |
| **LlamaIndex** | Python framework focused on data ingestion and RAG |
| **Orchestration** | Coordinating multiple LLM calls, tools, and agents in a flow |
| **LCEL** | LangChain Expression Language — composable chains |
| **Chain** | A sequence of LLM calls and transformations |
| **Workflow** | A directed graph of steps in an AI pipeline |
| **Guardrails** | Input/output validation to prevent harmful or off-topic responses |
| **Tracing / Observability** | Logging every LLM call, token count, latency for debugging |
| **LangSmith** | LangChain's observability/tracing platform |
| **Weights & Biases** | ML experiment tracking and observability |

---

*Next: See `02_Architecture.md` for how these pieces fit together in real applications.*
