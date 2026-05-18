# Conversation: AI Terminology, Architecture & Learning Path
**Date:** 2026-04-29  
**Project:** AI_Apps (new)

---

## User Request

Explain AI application development — terminology (LLM, Agentic AI, MCP, RAG), what to know to build AI apps, and the architecture. Create root folder AI_Apps, save conversation, and create learning documents.

---

## Key Concepts Covered

### LLM (Large Language Model)
- Transformer-based models trained on massive text data
- Key terms: token, context window, temperature, prompt, system prompt, inference
- Providers: Claude (Anthropic), GPT-4o (OpenAI), Gemini (Google), Llama (Meta)

### RAG (Retrieval Augmented Generation)
- Technique to give LLMs access to private/custom data without retraining
- Two pipelines: Indexing (Document → Chunk → Embed → Vector Store) and Query (Query → Embed → Retrieve → LLM)
- Key components: Embedding model, Vector Store (Chroma/Pinecone/pgvector), Retriever, LLM
- Use when: data is private, large, or frequently updated

### Agentic AI / AI Agents
- LLM that can reason, plan, and take actions via tools (ReAct loop)
- Core loop: Observe → Think → Act → Observe (repeating)
- Memory types: working, short-term, long-term/semantic, episodic
- Frameworks: LangChain, LangGraph, CrewAI, AutoGen, Anthropic Agent SDK

### MCP (Model Context Protocol)
- Open standard by Anthropic (2024) — "USB for AI tools"
- Solves N×M integration problem: any LLM host + any MCP server
- Components: Host, Client, Server, Transport, Tool, Resource, Prompt
- Transport: stdio (local) or SSE/HTTP (remote)

### Other Key Terms
- Embeddings: text → numeric vector capturing semantic meaning
- Vector Database: stores and searches embedding vectors
- Prompt Engineering: zero-shot, few-shot, chain-of-thought, role prompting
- Guardrails: input/output validation
- Observability: tracing every LLM call (LangSmith, Langfuse)
- Prompt Caching: save up to 90% cost on repeated large context

---

## Architecture Tiers

| Tier | Pattern | Use Case |
|------|---------|---------|
| 1 | Simple LLM call | Summarization, Q&A, drafting |
| 2 | RAG | Private document Q&A |
| 3 | Single Agent + Tools | Research, data analysis |
| 4 | Multi-Agent | Complex autonomous workflows |

## Documents Created

| File | Contents |
|------|---------|
| `docs/01_Terminology.md` | LLM, RAG, Agentic AI, MCP, all key terms with tables |
| `docs/02_Architecture.md` | All 4 architecture tiers, production diagram, decision guides |
| `docs/03_LearningPath.md` | 4-phase learning path with code examples, exercises, resources |
| `docs/04_QuickReference.md` | Reusable code snippets: API calls, RAG, prompts, cost estimation |

---

## Recommended First Steps for User

1. Get Claude API key from console.anthropic.com
2. Run first `hello world` LLM call (Phase 1 of learning path)
3. Build a PDF Q&A RAG app on your own documents (Phase 2)
4. Experiment with tool-calling agent (Phase 3)
