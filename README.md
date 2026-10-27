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

The starter dependencies are FastAPI and Uvicorn for the web app, plus
LangChain, LangGraph, LangSmith, and Deep Agents for the agent stack. Model
provider integrations are separate packages in LangChain, so we will add the
one matching our chosen provider when we implement the first agent.

## First milestone

The environment is the first milestone. The next small feature should be a
web health endpoint, before adding an agent or a frontend. That gives us a
working web app to build on and a simple way to verify it locally.
