# AI Apps — Quick Reference Card

---

## Claude API — Essential Patterns

### Basic Call
```python
import anthropic
client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY env var

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="You are a helpful assistant.",
    messages=[{"role": "user", "content": "Hello"}]
)
text = response.content[0].text
```

### Streaming
```python
with client.messages.stream(model="claude-sonnet-4-6", max_tokens=1024,
    messages=[{"role": "user", "content": "Write me a story"}]) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### Multi-turn Conversation
```python
messages = []
while True:
    user_input = input("You: ")
    messages.append({"role": "user", "content": user_input})
    response = client.messages.create(model="claude-sonnet-4-6", max_tokens=1024, messages=messages)
    assistant_text = response.content[0].text
    messages.append({"role": "assistant", "content": assistant_text})
    print(f"Assistant: {assistant_text}")
```

### Structured Output (JSON)
```python
response = client.messages.create(
    model="claude-sonnet-4-6", max_tokens=1024,
    system="Always respond with valid JSON only.",
    messages=[{"role": "user", "content": "Extract: name, date, amount from: 'John paid $500 on March 15'"}]
)
import json
data = json.loads(response.content[0].text)
```

### Tool Calling
```python
tools = [{
    "name": "get_weather",
    "description": "Get current weather for a city",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"]
    }
}]

response = client.messages.create(
    model="claude-sonnet-4-6", max_tokens=1024, tools=tools,
    messages=[{"role": "user", "content": "What's the weather in Mumbai?"}]
)

if response.stop_reason == "tool_use":
    tool_call = next(b for b in response.content if b.type == "tool_use")
    print(tool_call.name, tool_call.input)  # get_weather {'city': 'Mumbai'}
```

### Prompt Caching (saves cost on repeated large context)
```python
response = client.messages.create(
    model="claude-sonnet-4-6", max_tokens=1024,
    system=[{"type": "text", "text": "Your large context here...", "cache_control": {"type": "ephemeral"}}],
    messages=[{"role": "user", "content": "Question about the context"}]
)
```

---

## RAG — LangChain Snippets

### Load + Chunk + Index
```python
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

loader = DirectoryLoader("./docs/", glob="**/*.pdf", loader_cls=PyPDFLoader)
docs = loader.load()
chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")
```

### Query
```python
db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
results = db.similarity_search("What is the refund policy?", k=4)
for doc in results:
    print(doc.page_content)
    print(doc.metadata)
```

### RAG Chain
```python
from langchain_anthropic import ChatAnthropic
from langchain.chains import RetrievalQA

llm = ChatAnthropic(model="claude-sonnet-4-6")
qa = RetrievalQA.from_chain_type(llm=llm, retriever=db.as_retriever(search_kwargs={"k": 4}), return_source_documents=True)
result = qa.invoke({"query": "your question"})
print(result["result"])
```

---

## Cost Estimation

### Claude Pricing (approximate, check current pricing)
| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| Haiku | $0.25 | $1.25 |
| Sonnet | $3 | $15 |
| Opus | $15 | $75 |

### Estimate tokens
```python
import anthropic
client = anthropic.Anthropic()
token_count = client.messages.count_tokens(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": "your text here"}]
)
print(token_count.input_tokens)
```

---

## Common Prompt Templates

### Summarization
```
System: You are a precise summarizer. Return only the summary, no preamble.
User: Summarize the following in {num_sentences} sentences:

{document}
```

### Data Extraction
```
System: Extract structured data. Return valid JSON only, no markdown.
User: Extract these fields: {fields}

Text: {input_text}

Return format: {{"field1": "value", "field2": "value"}}
```

### Classification
```
System: You classify text into one of these categories: {categories}. Return only the category name.
User: {text}
```

### Code Review
```
System: You are a senior software engineer. Review code for bugs, security issues, and improvements. Be specific and actionable.
User: Review this {language} code:

```{language}
{code}
```
```

---

## Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install core packages
pip install anthropic langchain langchain-anthropic langchain-community
pip install chromadb sentence-transformers
pip install fastapi uvicorn streamlit python-dotenv

# .env file (never commit to git!)
ANTHROPIC_API_KEY=sk-ant-...
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_TRACING_V2=true
```

```python
# Load .env in Python
from dotenv import load_dotenv
load_dotenv()
import os
api_key = os.getenv("ANTHROPIC_API_KEY")
```

---

## Debugging Tips

| Problem | Fix |
|---------|-----|
| Response cuts off | Increase `max_tokens` |
| Inconsistent format | Use few-shot examples + explicit format instruction |
| Hallucination | Add "only use information from the provided context" to system prompt |
| Tool not called | Make tool description very clear and specific |
| Slow responses | Use `claude-haiku-4-5` for speed, enable streaming |
| High cost | Use caching for repeated system prompts, batch requests |
| RAG wrong docs retrieved | Increase K, adjust chunk size, try hybrid search |
