# AI Game Master: A Full-Stack RAG-Powered RPG

[![CI](https://github.com/PawanKonwar/ai-game-master/actions/workflows/main.yml/badge.svg)](https://github.com/PawanKonwar/ai-game-master/actions/workflows/main.yml)

An AI-powered text adventure RPG where an intelligent game master creates immersive, interactive fantasy adventures using retrieval-augmented generation (RAG), OpenAI, and LangChain.

![AI Game Master](screenshot.png)

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | **FastAPI** (Python), **LangChain**, **OpenAI GPT-3.5** (gpt-3.5-turbo), ChromaDB, Uvicorn, Pydantic |
| **Frontend** | **Vanilla JavaScript**, **CSS**, HTML5 |

- **FastAPI (Python)** — REST API, request/response validation, CORS.
- **LangChain** — Agent orchestration, tool use, and LLM integration.
- **OpenAI GPT-3.5** — Natural language generation for scenes, choices, and narrative.
- **Vanilla JavaScript / CSS** — No frameworks; clean, responsive UI with modern CSS (Grid, Flexbox).

---

## Features

- **Dynamic Choice Extraction** — The AI parses your actions and the story state to generate contextual multiple-choice options and free-form prompts, so every turn feels responsive and story-driven.
- **Dice Roller Tool** — Built-in dice tool supports standard notation (e.g. `3d6`, `1d20`, `2d10+5`). Rolls are executed by the agent and results are shown in the story and in roll history.
- **RAG-Based Memory** — ChromaDB-backed vector store with domain-specific collections (sessions, NPCs, locations, items). Relevant memories are retrieved and injected into prompts so the game master keeps continuity, remembers characters, and stays consistent with the world.
- **Interactive UI** — Real-time story display, choice buttons, custom action input, connection status, and a responsive layout that works on desktop and mobile.

---

## Getting Started

### Prerequisites

- **Python 3.8+** and **pip**
- **OpenAI API key**
- A modern web browser

### Backend

1. **Go to the backend directory and create a virtual environment:**

   ```bash
   cd backend
   python3 -m venv venv
   ```

2. **Activate the virtual environment:**

   - **macOS / Linux:** `source venv/bin/activate`
   - **Windows:** `venv\Scripts\activate`

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   Create a `.env` file in the `backend/` directory (or copy from `.env.example`) and set:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   CHROMA_PERSIST_DIR=./chroma_db
   APP_ENVIRONMENT=development
   ```

5. **Run the API server:**

   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at **http://localhost:8000**.

### Frontend

1. **Open the game in your browser:**

   - Open **`frontend-web/index.html`** directly in your browser (double-click or drag into the window),  
   - Or serve the folder locally, e.g.:
     ```bash
     cd frontend-web
     python3 -m http.server 8080
     ```
     Then go to **http://localhost:8080**.

2. **Connect and play:**

   - Click **“Connect to Server”** (ensure the backend is running at `http://localhost:8000`).
   - A starting scene will be generated; use the choice buttons or type custom actions to continue the adventure.

---

## Project Structure

```
ai-game-master/
├── backend/
│   ├── main.py           # FastAPI app and endpoints
│   ├── game_agent.py     # LangChain game master agent
│   ├── memory_store.py   # ChromaDB RAG / memory
│   ├── tools.py          # Dice roller tool
│   ├── requirements.txt
│   └── .env              # Your env vars (not in git)
├── frontend-web/
│   ├── index.html
│   ├── style.css
│   └── app.js
└── README.md
```

---

## API Overview

- `GET /` — Root
- `GET /health` — Health check
- `GET /test-scene` — Sample scene
- `POST /generate-scene` — Generate a scene (body: `{"prompt": "...", "include_dice_rolls": false}`)

---

## License

This project is open source and available under the MIT License.

---

**Note:** Keep your `.env` file secure and never commit API keys to version control.
