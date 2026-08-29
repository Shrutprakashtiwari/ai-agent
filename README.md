# 🧠 LLM Tool Agent (From Scratch)

A simple AI agent built from scratch using a local LLM (Mistral via Ollama), without relying on frameworks like LangChain. This project focuses on understanding how real AI agents work internally — including decision-making, tool usage, and structured outputs.

## 🚀 Features
- Uses local LLM (Mistral via Ollama)
- JSON-based decision making (LLM chooses tools)
- Tool support:
  - Calculator (math expressions)
  - Basic RAG (keyword-based retrieval)
- Handles messy LLM output using JSON extraction
- Built entirely in Python (no frameworks)

## 🧠 How It Works
User input is sent to the LLM with instructions to respond in JSON format.  
The LLM decides whether to:
- use a tool (calculator / rag)
- or return a final answer  

Flow:
User Input → LLM Decision → JSON Extraction → Tool Execution → Output

## ⚙️ Example
Input:

2*7548


Output:

Calculator Result: 15096
Decision: {'type': 'tool', 'tool': 'calculator', 'input': '2*7548'}


## 🛠️ Setup
1. Install Ollama → https://ollama.com  
2. Run model:

ollama run mistral

3. Run project:

python llm.py


## ⚠️ Current Limitations
- Single-step reasoning (no chaining) (Fixed)
- Basic RAG (keyword match, not semantic)
- No memory or conversation context
- Simple JSON parsing (can break)
- Uses eval() (not production safe)

## 🔥 Future Improvements
- Multi-step reasoning agent (think → act → observe loop) (Done)
- Real RAG (embeddings + vector DB like FAISS/Chroma)
- Memory system (conversation history)
- Dynamic tool system (plug-and-play tools)
- Robust JSON parsing + retry logic
- Replace eval() with safe parser
- API backend (FastAPI) for deployment

## 🎯 Goal
To deeply understand how LLM agents work internally instead of relying on high-level libraries.

## 👨‍💻 Author
Built while learning LLMs, agents, and real-world AI system design.
