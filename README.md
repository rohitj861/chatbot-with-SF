# ChatSF — AI Web Search Agent

A command-line chatbot that answers questions using **live web search**. It combines
OpenAI's `gpt-4o` chat model with Google search results (via the [Serper](https://serper.dev)
API), orchestrated as a [LangGraph](https://langchain-ai.github.io/langgraph/) agent.

When you ask a question, the agent decides whether to search the web, fetches fresh
results, and synthesizes an answer grounded in what it finds.

## Features

- 🔎 Real-time web search through the Serper (Google) API
- 🧠 Reasoning and answer synthesis with OpenAI `gpt-4o`
- 💬 Interactive command-line chat with conversation memory across turns
- 🔐 API keys loaded from a local `.env` file (never committed)

## Requirements

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- A free [Serper API key](https://serper.dev)

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/rohitj861/chatbot-with-SF.git
   cd chatbot-with-SF
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your API keys**

   Copy the example file and fill in your real keys:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env`:
   ```
   OPENAI_API_KEY=sk-your-openai-key
   SERPER_API_KEY=your-serper-key
   ```
   > `.env` is listed in `.gitignore`, so your keys stay out of version control.

## Usage

Run the agent:
```bash
python ChatSF.py
```

Then chat at the prompt:
```
User: Who won the most recent Formula 1 race?
Assistant: Searching the web now...
Assistant: ...
```

Type `quit`, `exit`, or `q` to stop.

## How it works

```
User question
      │
      ▼
LangGraph agent (create_agent)
      │  decides if a search is needed
      ▼
web_search tool  ──►  Serper API (Google results)
      │
      ▼
gpt-4o  ──►  synthesizes a grounded answer
```

- `ChatSF.py` — the whole application: the `web_search` tool, the agent, and the chat loop.
- `requirements.txt` — Python dependencies.
- `.env.example` — template for the API keys.

## Project structure

| File | Purpose |
|------|---------|
| `ChatSF.py` | Main application (agent + CLI chat loop) |
| `requirements.txt` | Dependencies |
| `.env.example` | API-key template (copy to `.env`) |
| `.gitignore` | Keeps `.env` and caches out of git |

## Notes

- The model is set to `gpt-4o`. To reduce cost, change `model="gpt-4o"` to
  `model="gpt-4o-mini"` in `ChatSF.py`.
- Never commit your real `.env`. If a key is ever exposed, rotate it from the
  OpenAI and Serper dashboards.
