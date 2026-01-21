# AI Game Master

An AI-powered text adventure RPG game master that creates immersive, interactive fantasy adventures using OpenAI's GPT models, LangChain, and ChromaDB.

![AI Game Master](screenshot.png)

## Description

AI Game Master is a full-stack application that combines the power of large language models with persistent memory to create dynamic, engaging text-based role-playing game experiences. The AI acts as a game master, generating scenes, responding to player choices, and maintaining story continuity across sessions.

## Features

### 🎮 Core Gameplay
- **Dynamic Scene Generation**: AI-generated fantasy scenes based on player prompts
- **Interactive Choices**: Multiple choice buttons that continue the story
- **Custom Actions**: Free-form text input for player creativity
- **Story Continuity**: Maintains narrative consistency across scenes and sessions

### 🎲 Game Mechanics
- **Dice Rolling System**: Integrated dice roller tool supporting standard notation (e.g., 3d6, 1d20, 2d10+5)
- **Dice Roll History**: Track all dice rolls during gameplay
- **Game Statistics**: Monitor scenes generated and actions taken

### 🧠 AI & Memory
- **LangChain Integration**: Powered by LangChain for agent orchestration
- **OpenAI GPT Models**: Uses GPT-3.5-turbo for natural language generation
- **Persistent Memory**: ChromaDB vector database stores:
  - Game session history
  - NPC information and relationships
  - Location descriptions and world lore
  - Item properties and history
- **RAG (Retrieval-Augmented Generation)**: Retrieves relevant memories to maintain consistency

### 🎨 User Interface
- **Modern Web Interface**: Clean, responsive design with gradient backgrounds
- **Real-time Story Display**: Auto-scrolling story area
- **Connection Status**: Visual indicator for backend connectivity
- **Responsive Design**: Works on desktop and mobile devices

### 🔧 Technical Features
- **FastAPI Backend**: RESTful API with CORS support
- **Modular Architecture**: Separated concerns (agent, memory, tools)
- **Error Handling**: Comprehensive error handling and user feedback
- **Auto-reload**: Development server with hot-reload support

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- OpenAI API key
- Modern web browser

### Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   - Open the `.env` file in the `backend/` directory
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     CHROMA_PERSIST_DIR=./chroma_db
     APP_ENVIRONMENT=development
     ```

6. **Start the FastAPI server**:
   ```bash
   uvicorn main:app --reload
   ```
   
   The server will start at `http://localhost:8000`

### Frontend Setup

1. **Open the frontend**:
   - Simply open `frontend-web/index.html` in your web browser
   - Or use a local web server:
     ```bash
     cd frontend-web
     python3 -m http.server 8080
     ```
     Then navigate to `http://localhost:8080`

2. **Connect to the backend**:
   - Click the "Connect to Server" button
   - The game will automatically generate a starting scene

## Project Structure

```
ai-game-master/
├── backend/
│   ├── main.py              # FastAPI application and endpoints
│   ├── game_agent.py        # LangChain game master agent
│   ├── memory_store.py      # ChromaDB memory management
│   ├── tools.py             # Dice roller tool
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables (not in git)
│   └── venv/                # Virtual environment (not in git)
├── frontend-web/
│   ├── index.html           # Main HTML structure
│   ├── style.css            # Styling
│   └── app.js               # Frontend JavaScript logic
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /test-scene` - Sample game scene
- `POST /generate-scene` - Generate a new game scene
  - Request body: `{"prompt": "scene description", "include_dice_rolls": false}`

## Usage

1. **Start the backend server** (see Setup Instructions)
2. **Open the frontend** in your browser
3. **Connect to the server** using the connect button
4. **Begin your adventure** - a starting scene will be automatically generated
5. **Make choices** by clicking the choice buttons or entering custom actions
6. **Watch the story unfold** as the AI continues the narrative based on your decisions

## Technologies Used

- **Backend**:
  - FastAPI - Modern Python web framework
  - LangChain - LLM application framework
  - OpenAI - GPT-3.5-turbo language model
  - ChromaDB - Vector database for persistent memory
  - Uvicorn - ASGI server
  - Pydantic - Data validation

- **Frontend**:
  - HTML5
  - CSS3 (with modern features like Grid and Flexbox)
  - Vanilla JavaScript (ES6+)

## Future Improvements

### Gameplay Enhancements
- [ ] Character creation and stat tracking
- [ ] Inventory management system
- [ ] Combat system with turn-based mechanics
- [ ] Multiple save slots for different adventures
- [ ] Achievement system
- [ ] Multiplayer support

### AI & Memory Improvements
- [ ] Fine-tuned prompts for better scene generation
- [ ] Enhanced memory retrieval with semantic search
- [ ] NPC relationship tracking
- [ ] World state management
- [ ] Procedural quest generation
- [ ] Dynamic difficulty adjustment

### UI/UX Enhancements
- [ ] Dark mode theme
- [ ] Text-to-speech for story narration
- [ ] Sound effects and background music
- [ ] Animated transitions
- [ ] Mobile app version
- [ ] Accessibility improvements (screen reader support)

### Technical Improvements
- [ ] User authentication and profiles
- [ ] Cloud deployment (Docker, AWS, etc.)
- [ ] Database migration system
- [ ] API rate limiting
- [ ] Caching layer for faster responses
- [ ] WebSocket support for real-time updates
- [ ] Unit and integration tests
- [ ] CI/CD pipeline

### Content & Features
- [ ] Multiple game genres (sci-fi, horror, modern, etc.)
- [ ] Pre-built adventure modules
- [ ] Community-shared adventures
- [ ] Mod support for custom tools and features
- [ ] Export/import game sessions
- [ ] Story replay functionality

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with OpenAI's GPT models
- Powered by LangChain for AI orchestration
- Uses ChromaDB for vector storage
- FastAPI for the backend framework

---

**Note**: Make sure to keep your `.env` file secure and never commit API keys to version control.
