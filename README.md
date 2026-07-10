# AI-Observer

An AI observability tool that analyzes any AI conversation and returns detailed metrics for debugging and monitoring.

## What it does

- Paste any prompt and response from ChatGPT, Claude, Gemini, or any LLM
- Select the model used
- Get instant observability metrics:
  - Estimated temperature range
  - Input, output, and total token counts
  - Estimated cost based on model pricing
  - Analysis latency
  - Prompt safety score (detects injection attempts)
  - Response quality score

## Tech Stack

- Frontend: React + Vite
- Backend: FastAPI (Python)
- Database: SQLite + SQLAlchemy
- Token counting: tiktoken
- Deployment: Vercel (frontend) + Render (backend)

## Use case

Paste any AI conversation into the tool to instantly understand:
- How much it cost
- How many tokens were used
- Whether the prompt contains injection patterns
- Whether the response quality is high or low
- What temperature range was likely used

## Who is it for

- Developers debugging LLM applications
- Teams monitoring AI response quality
- Anyone who wants visibility into their AI interactions