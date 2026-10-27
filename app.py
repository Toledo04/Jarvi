from fastapi import FastAPI, HTTPException

from market_data import (
    AlpacaCredentialsError,
    MarketDataUnavailable,
    StockTradeNotFound,
)
from schemas import ChatRequest, ChatResponse
from stock_agent import answer_stock_question

app = FastAPI(title="Jaarvi")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Ask Jaarvi for a stock quote using a ticker symbol."""
    try:
        reply = answer_stock_question(request.message)
    except AlpacaCredentialsError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except StockTradeNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except MarketDataUnavailable as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=(
                "The local model could not answer. Check that Ollama is running "
                "and the configured model is installed."
            ),
        ) from error

    return ChatResponse(reply=reply)
