import os
from functools import lru_cache

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_ollama import ChatOllama

from market_data import get_latest_stock_trade


@tool
def lookup_stock_quote(symbol: str) -> dict[str, str | float]:
    """Look up the latest Alpaca IEX trade for an explicit stock ticker symbol.

    Args:
        symbol: The stock ticker symbol, such as AAPL.
    """
    return get_latest_stock_trade(symbol.upper())


@lru_cache(maxsize=1)
def get_stock_agent():
    model = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        temperature=0,
    )
    return create_agent(
        model=model,
        tools=[lookup_stock_quote],
        system_prompt=(
            "You are Jaarvi, a stock quote assistant. You answer questions about "
            "the latest stock trade using the lookup_stock_quote tool. Only look "
            "up an explicit ticker symbol supplied by the user. If the user gives "
            "a company name without a ticker, ask them for the ticker instead of "
            "guessing. Never invent or estimate a price; use only the tool result. "
            "Include the price, timestamp, and that the source is Alpaca IEX. "
            "Do not give investment advice."
        ),
    )


def answer_stock_question(message: str) -> str:
    result = get_stock_agent().invoke(
        {"messages": [{"role": "user", "content": message}]}
    )
    content = result["messages"][-1].content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict)
        )
    return str(content)
