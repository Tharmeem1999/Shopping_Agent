# 🛒 Shopping Agent

An AI-powered shopping assistant that helps users discover, evaluate, and order products through a conversational interface. The agent combines natural-language understanding, vision capabilities, and structured product data to deliver a guided shopping experience with ratings, filters, and one-click checkout.

---

## Project Overview

**Shopping Agent** is a Streamlit-based conversational AI application that lets users shop the way they naturally think: in plain language or by uploading a product photo. It uses a **LangChain agent** powered by **Google Gemini** to understand user intent, search a local SQLite product catalog, fetch customer ratings, and place orders — all while keeping the user firmly in control of what gets bought.

The project demonstrates a practical end-to-end agentic workflow:

1. **Understand** the user's request (text or image).
2. **Search** a structured product database.
3. **Enrich** results with aggregated customer reviews.
4. **Present** a curated, ranked shortlist.
5. **Confirm** with the user before placing an order.

---

## Key Features

- **Conversational Search** — Describe what you want in natural language (e.g. *"organic honey under $15 with 4+ rating"*).
- **Visual Product Discovery** — Upload a product photo; the agent uses Gemini's vision model to extract attributes and find similar items.
- **Rating-Aware Recommendations** — Products are filtered by average customer rating derived from real review data.
- **Safe Checkout** — The agent never places an order without explicit user confirmation.
- **Smart Filters** — Filter by keyword, maximum price, and organic status.
- **Stateful Chat** — Conversation history is preserved across turns in the Streamlit session.
- **Extensible Tools** — Agent capabilities are implemented as discrete LangChain tools, easy to extend.
- **Local-First Data** — Uses a lightweight SQLite database (`store.db`) — no external services required.

---

## Technology Stack

| Layer | Technology |
| --- | --- |
| **UI** | [Streamlit](https://streamlit.io/) |
| **Agent Framework** | [LangChain](https://www.langchain.com/) (`create_agent`) |
| **LLM** | [Google Gemini](https://ai.google.dev/) via `langchain-google-genai` (`gemini-3.1-flash-lite`) |
| **Vision** | Gemini multimodal image understanding |
| **Data Store** | SQLite (local `store.db`) |
| **Environment Mgmt** | [`uv`](https://docs.astral.sh/uv/) (PEP 621 / `pyproject.toml`) |
| **Config** | `python-dotenv` (`.env` file) |
| **Language** | Python ≥ 3.14 |

---

## Project Structure

```text
Shopping_Agent/
├── app.py                   # Streamlit UI — chat + image upload
├── shopping_agent.py        # LangChain agent + tool definitions
├── reviews_api.py           # Reviews aggregation helpers (SQLite)
├── store.db                 # SQLite database (products, reviews, orders)
├── pyproject.toml           # Project metadata & dependencies
├── uv.lock                  # Locked dependency graph
├── .env                     # Local secrets (not committed)
├── resources/               # Sample product images for testing
│   ├── elephant.png
│   ├── honey.png
│   └── oats.png
└── src/
    └── shopping_agent/
        └── __init__.py      # Package entry — exposes `main()` for `uv run shopping-agent`
```

---

## Getting Started

### Prerequisites

- **Python 3.14+**
- **`uv`** — the fast Python package & project manager

  ```bash
  # Install uv (if you don't have it)
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- A **Google Gemini API key** — get one at [aistudio.google.com](https://aistudio.google.com/app/apikey).

### Installation

```bash
# Clone the repository
git clone https://github.com/Tharmeem1999/Shopping_Agent.git
cd Shopping_Agent

# Install all dependencies (creates .venv automatically)
uv sync
```

### Configuration

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your-gemini-api-key-here
```

The agent loads it automatically via `python-dotenv`.

### Seed the Database (if `store.db` is missing)

If the database is not present, create the required tables and seed it with sample data. A minimal schema:

```sql
CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    category    TEXT,
    price       REAL NOT NULL,
    description TEXT,
    is_organic  INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS reviews (
    id         INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    rating     REAL NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS orders (
    id           INTEGER PRIMARY KEY,
    product_id   INTEGER NOT NULL,
    product_name TEXT,
    price        REAL,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Usage

### Run the Streamlit App

```bash
uv run streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

### Run the CLI Entry Point

```bash
uv run shopping-agent
```

### Try These Example Prompts

```text
I want organic honey under $15 with 4+ rating
Show me chocolate between $5 and $20
Find me vegan snacks
```

Or upload an image from `resources/` (e.g. `honey.png`) using the **sidebar uploader** and click **Find similar products**.

---

## How It Works

### Agent Workflow

```text
┌──────────────┐    ┌────────────────────────┐    ┌──────────────────┐
│  User Input  │───▶│  LangChain Agent       │───▶│  Tool Invocation │
│ (text/image) │    │  (Gemini + tools)      │    │                  │
└──────────────┘    └────────────────────────┘    └──────┬───────────┘
                                                         │
                              ┌───────────────────────────┼────────────────────────────┐
                              ▼                           ▼                            ▼
                  ┌────────────────────┐     ┌────────────────────┐     ┌──────────────────────┐
                  │ search_products    │     │ get_rating         │     │ describe_product_…   │
                  │ (SQLite products)  │     │ (SQLite reviews)   │     │ (Gemini vision)      │
                  └─────────┬──────────┘     └─────────┬──────────┘     └──────────┬───────────┘
                            └─────────────────┬────────┴───────────┬──────────────┘
                                              ▼                    ▼
                                    ┌──────────────────┐  ┌──────────────────┐
                                    │ checkout         │  │  Final Response  │
                                    │ (SQLite orders)  │  │  to user         │
                                    └──────────────────┘  └──────────────────┘
```

### Tools Exposed to the Agent

| Tool | Purpose |
| --- | --- |
| `search_products` | Filter products by keyword, max price, and organic flag |
| `get_rating` | Return average rating + review count for a product |
| `describe_product_image` | Use Gemini vision to extract product attributes from an image |
| `checkout` | Persist an order to the `orders` table (only after explicit user confirmation) |

### Safety Guarantees

- The agent **never** calls `checkout` without an explicit "yes" / "order #N" / "get me the first one" from the user.
- Product IDs are taken **only** from the `(ID:X)` tokens the agent itself emitted — never guessed.

---

## Database Schema

| Table | Columns |
| --- | --- |
| `products` | `id`, `name`, `category`, `price`, `description`, `is_organic` |
| `reviews` | `id`, `product_id`, `rating` |
| `orders` | `id`, `product_id`, `product_name`, `price`, `created_at` |

Located at: `store.db` (project root, auto-created on first run if seeded).

---

## Development

### Install dev dependencies

```bash
uv sync --dev
```

### Run the app in dev mode with auto-reload

```bash
uv run streamlit run app.py --server.runOnSave=true
```

### Add a new tool

1. Define a new `@tool` function in [shopping_agent.py](shopping_agent.py).
2. Register it in the `tools=[...]` list passed to `create_agent`.
3. Update the `system_prompt` so the agent knows when and how to call it.

### Project Conventions

- Tool functions return **JSON strings** (or plain text) for reliable LLM parsing.
- All SQL is parameterized to prevent injection.
- Streamlit session state uses `st.session_state.messages` to keep conversation history.

---

## Deployment

### Streamlit Community Cloud (free, recommended)

1. Push the repo to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io) and connect your repo.
3. Set `GOOGLE_API_KEY` in **Secrets**.
4. Set the entry point to `app.py`.

---

> Built with ❤️ using LangChain, Google Gemini, and Streamlit.
