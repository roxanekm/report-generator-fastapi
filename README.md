# Report Generator API

**Author:** Roxane Kouamé  
**Stack:** FastAPI · Whisper · HuggingFace Transformers · Python 3.10+

---

## 1. Description

This API automatically generates a meeting report from an audio file.  
It combines speech recognition (Whisper) and automatic text summarization (BART/SAMSum) to produce:

- a complete transcription of the audio file  
- a structured summary of the discussion  
- identified decisions and actions  
- a final downloadable report in Markdown format

---

## 2. Project Architecture

.
├── main.py                  # FastAPI entrypoint (includes routers, CORS, etc.)
├── app/
│   ├── api/
│   │   └── meetings.py      # /meetings endpoint: orchestrates the pipeline
│   └── services/
│       ├── transcription.py # Audio transcription with Whisper
│       └── notes.py         # Summarization + report generation
└── downloads/               # Generated Markdown reports

---

## 3. Workflow

The report generation pipeline follows these main steps:

1. Audio upload – user sends an audio file via POST /meetings/  
2. Transcription – transcription.py converts speech to text using Whisper and detects the spoken language
3. Summarization – notes.py summarizes the text and extracts key elements  
4. Information extraction – identifies topics, decisions, and actions  
5. Report generation – builds and returns a Markdown file as response

---

## 4. Endpoint

### POST /meetings/

**Request example:**
curl -X POST "http://localhost:8000/meetings/" -F "file=@meeting_audio.wav"

**Response:**
Returns a downloadable .md file containing:
- discussed topics  
- decisions taken  
- actions to be done  
- overall summary  
- complete transcription

---

## 5. Technologies Used


**Speech-to-Text – Whisper (OpenAI)**  
Whisper was chosen for its performance on multilingual and noisy data.  
Unlike lightweight models such as Wav2Vec2 or Vosk, Whisper can handle overlapping speech, accents, and variable quality audio, which makes sense for real meeting recordings.  It required no fine-tuning so it was a fast and reproducible setup.  The base model was used on CPU as a proof of concept to ensure fast deployment without GPU dependency. For higher throughput, a GPU-optimized or distilled version could later be deployed for the 'small' or 'medium' model if necessary.

**Summarization – BART/SAMSum**  
The summarization module relies on the BART model fine-tuned on the SAMSum dataset, optimized for conversational data. It was selected because it captures the dynamics of human dialogue — context continuity, pronoun resolution, and intent detection — which are essential in meeting transcripts.
Before integrating BART, a heuristic approach based on word frequency and clustering was tested. However, this method required constant manual tuning and quickly degraded with noisy transcripts or long meetings. The deep-learning model provided a more stable and scalable alternative.
The implementation segments the transcript into manageable chunks (about 2 000 characters) to avoid the model’s input length limitations, summarizes each segment independently, and then concatenates the partial summaries into a coherent global report.
Without depending on an external API or heavy LLMs that would be power-hungry, this setup provides a sweet spot between efficiency and semantic accuracy.
For future improvements, one could explore LLM-based summarization with role-conditioned prompts to extract actions and decisions more precisely, or integrate multilingual fine-tuning to improve cross-language generalization.


**File Handling – FileResponse (FastAPI)**  
FastAPI’s built-in `FileResponse` was used to stream the generated Markdown report back to the client.  
It minimizes memory overhead and avoids temporary storage duplication.  


---

### Summary Table

| Task | Technology | Purpose |
|------|-------------|----------|
| Backend | FastAPI | Async web framework with built-in validation and documentation |
| Speech-to-Text | Whisper (OpenAI) | Multilingual speech recognition |
| Summarization | BART / SAMSum | Dialogue-oriented text summarization |
| File Handling | FileResponse | Efficient Markdown report export |


---

## 6. Code Organization

### main.py
- Initializes the FastAPI app  
- Configures CORS, logging, and router inclusion  
- Defines the base health endpoint  

### meetings.py
- Manages the /meetings/ route  
- Handles file upload and validation  
- Connects all processing stages (transcription, summarization, elements extraction ) into a single endpoint.  
- Returns a Markdown file as a downloadable response  

### transcription.py
- Loads and caches the Whisper model once (LRU cache)  
- Handles temporary audio file storage and automatic cleanup  
- Extracts text from the uploaded audio  

### notes.py
- Summarizes long transcriptions using BART SAMSum  
- Detects and separates topics, decisions, and actions  
- Builds the final report in Markdown format, ready to export  

---

## 7. Example Output

# Meeting Report

## Topics Discussed
- Sprint planning  
- UI design validation  

## Decisions
- Extended deadline by two weeks  

## Actions
- Finalize UI mockups  
- Prepare sprint review  

## Summary
The meeting focused on sprint planning and design validation.  

## Full Transcription
Let's review the sprint timeline...

---

## 8. Dependencies

Additional dependencies were added for the AI-based meeting report generation:

- **openai-whisper** – for automatic speech-to-text transcription  
- **transformers (BART/SAMSum)** – for dialogue-oriented summarization  
- **torch** – required backend for Whisper and Transformers  
- **sentencepiece** – tokenizer for summarization models  
- **numpy** – numerical support for Whisper  

## Install all dependencies with:
pip install -r requirements.txt

---

## 9. Run the Application

### Option 1 — Docker
docker build -t report-generator .
docker run -p 8000:8000 report-generator

Access the API docs at: http://localhost:8000/docs

### Option 2 — Local Development
pip install -r requirements.txt
uvicorn main:app --reload

---

## 9. Author

**Roxane Kouamé**  
Engineer in Embedded Systems & Artificial Intelligence  
LinkedIn: https://www.linkedin.com/in/roxane-kouame

---





######

# FastAPI Template

A production-ready FastAPI template with authentication, async database operations, and Docker support.

## Features

- **Modern Python**: Type hints, async/await syntax, and the latest FastAPI features
- **JWT Authentication**: Complete authentication system with access and refresh tokens
- **SQLAlchemy with Async**: Fully async database operations using SQLAlchemy 2.0+
- **Alembic Migrations**: Database schema migrations with Alembic
- **Role-based Access Control**: User roles with different permission levels (active, staff, superuser)
- **Docker Support**: Ready-to-use Docker and Docker Compose configurations
- **Developer-friendly**: Auto-reload, debugging, and development tools
- **Production-ready**: Configuration for deployment in production environments

## Project Structure

```
.
├── alembic/                 # Database migrations
├── app/                     # Main application package
│   ├── api/                 # API endpoints
│   ├── core/                # Core functionality (config, security)
│   ├── db/                  # Database session and base
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── docker-compose.yml       # Docker Compose for production
├── docker-compose.dev.yml   # Docker Compose for development
├── Dockerfile               # Docker configuration
├── alembic.ini              # Alembic configuration
├── main.py                  # Application entry point
├── pyproject.toml           # Project dependencies and metadata
├── start.sh                 # Production startup script
└── start-dev.sh             # Development startup script
```

## Requirements

- Python 3.11+
- Docker (optional)

## Installation

### Using Docker (recommended)

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd fastapi-template
   ```

2. Start the application with Docker Compose:
   ```bash
   # For development
   docker-compose -f docker-compose.dev.yml up --build

   # For production
   docker-compose up --build
   ```

3. The API will be available at http://localhost:8000

### Local Development

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd fastapi-template
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Set up environment variables (create a `.env` file):
   ```
   DEBUG=true
   SECRET_KEY=your-secret-key
   DB_ENGINE=sqlite  # or postgresql
   # For PostgreSQL, add these:
   # DB_USER=postgres
   # DB_PASSWORD=password
   # DB_HOST=localhost
   # DB_PORT=5432
   # DB_NAME=app
   ```

5. Run migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the application:
   ```bash
   uvicorn main:app --reload
   ```

7. The API will be available at http://localhost:8000

## API Documentation

Once the application is running, you can access:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /auth/signup` - Register a new user
- `POST /auth/login` - Authenticate and get tokens
- `POST /auth/token/refresh` - Refresh access token
- `POST /auth/logout` - Logout user
- `GET /auth/me` - Get current user information

### System

- `GET /health` - Health check endpoint

## Configuration

The application is configured through environment variables which can be set in a `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `true` |
| `SECRET_KEY` | JWT secret key | `supersecretkey` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiration time | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration time | `7` |
| `CORS_ORIGINS` | CORS allowed origins | `["*"]` |
| `DB_ENGINE` | Database engine | `sqlite` |
| `DB_USER` | Database user | `""` |
| `DB_PASSWORD` | Database password | `""` |
| `DB_HOST` | Database host | `""` |
| `DB_PORT` | Database port | `""` |
| `DB_NAME` | Database name | `app.db` |

## Development

### Running Tests

```bash
pytest
```

### Code Quality Tools

The project uses several tools to ensure code quality:

- **Black**: Code formatter
- **isort**: Import sorter
- **mypy**: Static type checking
- **pre-commit**: Git hooks for code quality checks

To set up pre-commit hooks:

```bash
pre-commit install
```

## Database

The template supports SQLite for development and PostgreSQL for production. The default is SQLite.

### Migrations

To create a new migration after changing models:

```bash
alembic revision --autogenerate -m "Description of changes"
```

To apply migrations:

```bash
alembic upgrade head
```

## Docker

The project includes Docker configurations for both development and production:

- `docker-compose.yml`: Production setup
- `docker-compose.dev.yml`: Development setup with hot-reload

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b ft/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin ft/my-feature`
