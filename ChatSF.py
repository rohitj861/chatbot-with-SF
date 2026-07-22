import os
import functools
import operator
from typing import List, Annotated
from typing_extensions import TypedDict

import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END

# ---------------------------------------------------------------------------
# API keys
# ---------------------------------------------------------------------------
# Keys are read from a .env file in this folder (see .env.example / .env).
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set. Set it before running ChatSF.py.")
if not SERPER_API_KEY:
    raise RuntimeError("SERPER_API_KEY is not set. Get a free key at https://serper.dev.")

# ---------------------------------------------------------------------------
# OpenAI chat model
# ---------------------------------------------------------------------------
llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=OPENAI_API_KEY)


# ---------------------------------------------------------------------------
# Web search tool (Serper -> Google) — self-contained HTTP call
# ---------------------------------------------------------------------------
@tool
def web_search(query: str) -> str:
    """Search the web with Google (via Serper) and return the top results.

    Use this for any question that needs current, factual, or up-to-date
    information from the internet.
    """
    resp = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
        json={"q": query, "num": 5},
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()

    results = []
    if data.get("answerBox"):
        box = data["answerBox"]
        answer = box.get("answer") or box.get("snippet") or ""
        if answer:
            results.append(f"Answer: {answer}")

    for item in data.get("organic", [])[:5]:
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        link = item.get("link", "")
        results.append(f"- {title}\n  {snippet}\n  {link}")

    return "\n".join(results) if results else "No results found."


# ---------------------------------------------------------------------------
# Graph state
# ---------------------------------------------------------------------------
class SearchState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]


def agent_node(state, agent, name):
    """Run an agent and return its final message as a named message."""
    result = agent.invoke(state)
    return {
        "messages": [HumanMessage(content=result["messages"][-1].content, name=name)]
    }


# ---------------------------------------------------------------------------
# Search agent + graph
# ---------------------------------------------------------------------------
search_agent = create_agent(llm, tools=[web_search])
search_node = functools.partial(agent_node, agent=search_agent, name="search_agent")

search_graph = StateGraph(SearchState)
search_graph.add_node("search_agent", search_node)
search_graph.add_edge(START, "search_agent")
search_graph.add_edge("search_agent", END)
search_app = search_graph.compile()

# Persistent state to maintain conversation history across turns
persistent_state = {"messages": []}


def stream_graph_updates(user_input: str):
    global persistent_state
    persistent_state["messages"].append(HumanMessage(content=user_input))

    print("\nAssistant: Searching the web now...\n")

    for event in search_app.stream(persistent_state):
        for value in event.values():
            last_msg = value["messages"][-1]
            print("Assistant:", last_msg.content, "\n")
            persistent_state["messages"].append(last_msg)


if __name__ == "__main__":
    print("AI Web Search Agent (type 'quit', 'exit', or 'q' to stop)\n")
    while True:
        try:
            user_input = input("User: ")
            if user_input.strip().lower() in ["quit", "exit", "q"]:
                print("Thank you and Goodbye!")
                break
            stream_graph_updates(user_input)
        except KeyboardInterrupt:
            print("\nThank you and Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
