# AI Application Learning Path — Step by Step

---

## Phase 1: Foundation (Week 1–2)

### Goal: Understand LLMs and make your first API call

**Step 1 — Get an API key**
- Sign up at https://console.anthropic.com (Claude)
- Or https://platform.openai.com (OpenAI)
- Store key as environment variable: `ANTHROPIC_API_KEY`

**Step 2 — Install SDK**
```bash
pip install anthropic
# or
pip install openai
```

**Step 3 — Your first LLM call**
```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="You are a helpful assistant.",
    messages=[{"role": "user", "content": "What is RAG in AI?"}]
)
print(response.content[0].text)
```

**Step 4 — Try these prompting patterns**
- Zero-shot: just ask directly
- Few-shot: give 2-3 examples first
- Chain-of-thought: add "Think step by step" to your prompt
- Role prompting: "You are an expert in..."
- Output format: "Return your answer as JSON with keys: ..."

**Key Concepts to Solidify**
- [ ] What a token is and how it affects cost
- [ ] System prompt vs user message
- [ ] Temperature and when to adjust it
- [ ] How to count tokens before calling the API

---

## Phase 2: RAG Application (Week 3–5)

### Goal: Build an app that answers questions from your own documents

**Step 1 — Install dependencies**
```bash
pip install langchain langchain-community langchain-anthropic chromadb sentence-transformers
```

**Step 2 — Build the indexing pipeline**
```python
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Load
loader = PyPDFLoader("my_document.pdf")
docs = loader.load()

# Chunk
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

# Embed and store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")
```

**Step 3 — Build the query pipeline**
```python
from langchain_anthropic import ChatAnthropic
from langchain.chains import RetrievalQA

llm = ChatAnthropic(model="claude-sonnet-4-6")
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

result = qa_chain.invoke({"query": "What are the main risks?"})
print(result["result"])
```

**Step 4 — Add a simple UI with Streamlit**
```bash
pip install streamlit
streamlit run app.py
```

**Exercises**
- [ ] Index a set of PDFs from your domain
- [ ] Ask questions and check if retrieved chunks are relevant
- [ ] Experiment with chunk sizes (300 vs 500 vs 1000 tokens)
- [ ] Try different K values in retrieval (3, 5, 10)
- [ ] Add citation display — show which document the answer came from

---

## Phase 3: Tool-Calling Agent (Week 6–8)

### Goal: Build an agent that can use tools to accomplish tasks

**Step 1 — Define tools**
```python
import anthropic
import json

client = anthropic.Anthropic()

tools = [
    {
        "name": "search_web",
        "description": "Search the web for current information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "run_sql",
        "description": "Run a SQL query on the database",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "SQL query to execute"}
            },
            "required": ["query"]
        }
    }
]
```

**Step 2 — Build the agent loop**
```python
def run_agent(user_message):
    messages = [{"role": "user", "content": user_message}]
    
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )
        
        # If model is done, return final answer
        if response.stop_reason == "end_turn":
            return response.content[0].text
        
        # If model wants to call a tool
        if response.stop_reason == "tool_use":
            # Add assistant's response to messages
            messages.append({"role": "assistant", "content": response.content})
            
            # Execute each tool call
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            # Add tool results back
            messages.append({"role": "user", "content": tool_results})

def execute_tool(name, inputs):
    if name == "search_web":
        return web_search(inputs["query"])  # your search function
    elif name == "run_sql":
        return run_database_query(inputs["query"])
```

**Exercises**
- [ ] Build a research agent that can search + summarize
- [ ] Build a data analyst agent that can query a database
- [ ] Add memory so the agent remembers past conversations
- [ ] Add human-in-the-loop confirmation for destructive actions

---

## Phase 4: Production Readiness (Week 9–12)

### Goal: Make your app reliable, observable, and deployable

**Step 1 — Add observability with LangSmith**
```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-key"
# Now all LangChain calls are auto-traced
```

**Step 2 — Add streaming for better UX**
```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a report..."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

**Step 3 — Add prompt caching (save up to 90% on repeated context)**
```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=[{
        "type": "text",
        "text": "Your large system prompt here...",
        "cache_control": {"type": "ephemeral"}  # Cache this!
    }],
    messages=[{"role": "user", "content": user_query}]
)
```

**Step 4 — Add input/output guardrails**
```python
def validate_input(user_input: str) -> bool:
    # Check for prompt injection attempts
    # Check for PII
    # Check for off-topic requests
    pass

def validate_output(response: str) -> str:
    # Check for hallucination markers
    # Remove any leaked internal data
    # Ensure format compliance
    pass
```

**Step 5 — Deploy with FastAPI + Docker**
```bash
pip install fastapi uvicorn
```

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    question: str
    session_id: str

@app.post("/ask")
async def ask(query: Query):
    response = run_agent(query.question)
    return {"answer": response}
```

**Checklist for Production**
- [ ] API keys in environment variables, never in code
- [ ] Rate limiting on your API
- [ ] Token usage logging and cost alerts
- [ ] Error handling and retries with exponential backoff
- [ ] Input validation and sanitization
- [ ] Output format validation
- [ ] Automated tests for your prompts
- [ ] Monitoring and alerting

---

## Recommended Learning Resources

### Official Docs
- Anthropic: https://docs.anthropic.com
- LangChain: https://python.langchain.com
- LlamaIndex: https://docs.llamaindex.ai
- MCP Spec: https://modelcontextprotocol.io

### Practice Projects (Increasing Difficulty)
1. **PDF Q&A bot** — RAG over a set of PDFs
2. **Internal knowledge base** — Index your company documents
3. **SQL agent** — Natural language to database queries
4. **Research agent** — Autonomously researches topics, writes reports
5. **Code review agent** — Analyzes code PRs and suggests improvements
6. **Multi-agent pipeline** — Research + Analyze + Write + Review

---

*Next: See `04_QuickReference.md` for code snippets you'll reuse constantly.*
