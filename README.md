# Jaarvi

A small learning project for building web apps with agents. We will grow it one
small feature at a time.

## Environment setup

This project uses Python and `uv` to keep the Python version and dependencies
consistent. The current environment is Python 3.13.

1. Install `uv` if you do not already have it: <https://docs.astral.sh/uv/getting-started/installation/>
2. From the project folder, create/sync the environment and lock dependencies:

   ```bash
   uv sync
   ```

   `uv sync` creates `.venv/` when needed and writes `uv.lock`. Keep `uv.lock`
   in git so later installs use the same resolved dependency versions.
3. Copy `.env.example` to `.env` when you are ready to add credentials. Put
   provider and LangSmith keys only in `.env`; it is ignored by git.
4. Run Python commands through uv, for example `uv run python --version`.

The project uses FastAPI and Uvicorn for the web app, plus LangChain, LangGraph,
LangSmith, and Deep Agents for the agent stack. Ollama is the current local
model provider.

## First milestone

The first milestone is a web health endpoint. Start the development server:

```bash
uv run --env-file .env uvicorn app:app --reload
```

Open <http://127.0.0.1:8000/health> in a browser. It should return
`{"status":"ok"}`. FastAPI's interactive API page is at
<http://127.0.0.1:8000/docs>.

The agent endpoint is `POST /chat`. It accepts a message such as
`{"message":"What is the latest price for AAPL?"}` and returns a reply. The
local model is configured by `OLLAMA_MODEL` in `.env`. Install Ollama, start its
local service, and download the selected model before calling `/chat`:

```bash
ollama pull llama3.2:3b
```

Create `.env` from `.env.example` and add your Alpaca API credentials there
before asking the agent for stock data. Keep those credentials out of Git. Use
the interactive `/docs` page to try `/chat`. The agent uses the Alpaca stock
data function internally through its `lookup_stock_quote` tool; there is no
separate public quote endpoint.

## Code organization

- `app.py` handles HTTP routes and translates application errors into HTTP responses.
- `market_data.py` talks to Alpaca and normalizes its response.
- `schemas.py` defines the JSON request and response shapes for chat.
- `stock_agent.py` defines the quote tool and the LangChain agent that uses it.

FastAPI generates the interactive `/docs` page from the route and response
schema. The JSON response is the API's presentation layer; this project does
not have an HTML frontend yet.

## Testing environment

For now, tests run in the same `.venv` as development, but use fake external
services. This keeps setup small while making tests repeatable: they do not
load `.env`, contact Alpaca, or need Alpaca credentials. The Alpaca HTTP call
is replaced with a fake response in `tests/test_market_data.py`.

Run the tests with:

```bash
uv run python -m unittest discover -s tests -v
```

The test command intentionally does not use `--env-file .env`. Later, if the
project needs different installed package versions, a CI runner, or test-only
services, we can give testing more isolation. A separate virtual environment
is not necessary for these first unit tests.
