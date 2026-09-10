# CattleVision AI

A full-stack cattle intelligence application for breed identification, skin-disease prediction, nutrition recommendations, breed information, and document-based question answering.

The project combines a React/Vite frontend with a FastAPI backend and machine-learning services built with YOLO, Vision Transformers, scikit-learn, and LangChain.

## Features

- Cattle breed prediction using YOLO and Vision Transformer models
- Cattle skin-disease prediction using YOLO and Vision Transformer models
- Nutrition recommendations from a persisted decision-tree model
- Breed information and traits from PostgreSQL
- Retrieval-Augmented Generation (RAG) over PDF documents
- REST API with automatic OpenAPI documentation
- React frontend for interacting with the backend services

## Project Structure

```text
MAJOR_PROJECT/
├── BACKEND/
│   ├── app.py                         # FastAPI application
│   ├── rag.py                         # Document ingestion and RAG question answering
│   ├── NUTRITION_RECOMEND.py          # Nutrition model integration
│   ├── requirements.txt               # Python dependencies
│   ├── Artifacts/                     # PDF documents used by RAG
│   ├── MODELS/                        # Trained model files and class labels
│   └── MY_SPACE/                      # Local Python virtual environment
├── FRONTEND/
│   ├── src/                           # React application source
│   ├── package.json                   # Frontend scripts and dependencies
│   └── vite.config.js                 # Vite configuration
└── README.md
```

## Technology Stack

### Backend

- Python 3.13
- FastAPI
- Uvicorn
- PyTorch and Torchvision
- Ultralytics YOLO
- timm Vision Transformer models
- LangChain, FAISS, Hugging Face Transformers
- PostgreSQL with psycopg2

### Frontend

- React 19
- Vite
- JavaScript and CSS

## Prerequisites

Install the following before starting:

- Python 3.13 or compatible Python version
- Node.js and npm
- PostgreSQL
- Git, if cloning the project
- A Groq API key for RAG question answering

## Configuration

Create a `.env` file inside `BACKEND/`:

```env
API_KEY=your_groq_api_key

DB_HOST=localhost
DB_PORT=5432
DB_NAME=PROJECT_PHASE_1
DB_USER=postgres
DB_PASSWORD=your_database_password
```

`API_KEY` is required when the RAG service is initialized. The database variables are used by the `/breeds` endpoint. Do not commit `.env` files or real credentials.

## Backend Setup

Open PowerShell in the project root and activate the included virtual environment:

```powershell
Set-Location .\BACKEND
.\MY_SPACE\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start the FastAPI server from the `BACKEND` directory because model paths are relative to that working directory:

```powershell
uvicorn app:app --reload
```

The backend is available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available at:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Frontend Setup

Open a second terminal:

```powershell
Set-Location .\FRONTEND
npm install
npm run dev
```

The Vite development server normally runs at:

```text
http://localhost:5173
```

The frontend currently sends requests to `http://127.0.0.1:8000`.

## API Overview

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Basic service status |
| `GET` | `/health` | Model and service health information |
| `GET` | `/classes` | Available cattle breed classes |
| `POST` | `/predict` | Predict cattle breed from an image |
| `POST` | `/predict-skin-disease` | Predict cattle skin disease from an image |
| `GET` | `/breeds` | Load breed details and traits from PostgreSQL |
| `GET` | `/nutrition-options` | Load supported nutrition input options |
| `POST` | `/nutrition-recommendation` | Generate a nutrition recommendation |
| `POST` | `/rag/ingest` | Ingest PDFs from `BACKEND/Artifacts` |
| `POST` | `/rag/ask` | Ask a question about ingested documents |
| `GET` | `/rag/status` | Check RAG initialization and ingestion status |

Image endpoints accept JPEG, PNG, or WebP uploads using the `file` form field.

Example health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Example RAG question:

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/rag/ask `
  -Method Post `
  -ContentType 'application/json' `
  -Body '{"question":"What information is available in the documents?"}'
```

Before asking questions, ingest the PDF documents:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/rag/ingest -Method Post
```

## Model Assets

The backend expects trained assets in these locations:

```text
BACKEND/MODELS/
├── cattle_breed_model_v2/best.pt
├── class_names.json
├── ViT_Results_85Plus/best_vit_small_patch16_224_cattle.pth
├── SKIN_DISEASE_MODELS/
│   ├── VIT/vit_cattle_skin_model.pth
│   ├── VIT/class_names.json
│   └── YOLO/best (3).pt
└── NUTRITION_RECOMENDATION_MODEL/
    ├── cattle_nutrition_tree.pkl
    ├── label_encoders.pkl
    └── training data
```

RAG PDF files should be placed in:

```text
BACKEND/Artifacts/
```

## Database

The `/breeds` endpoint expects PostgreSQL tables containing breed data and traits, including:

- `cattle_breeds`
- `breed_traits`

The default database settings are database `PROJECT_PHASE_1`, host `localhost`, and port `5432`. Configure these values in `BACKEND/.env` for a different database.

## Troubleshooting

### `ModuleNotFoundError` for LangChain packages

Make sure the backend virtual environment is active and reinstall dependencies:

```powershell
Set-Location .\BACKEND
.\MY_SPACE\Scripts\python.exe -m pip install -r requirements.txt
```

### Model files are not found

Start Uvicorn from `BACKEND/`, not from the project root, because several model paths are relative to the current working directory.

### Pylance reports unresolved imports

In VS Code, select this interpreter:

```text
BACKEND\MY_SPACE\Scripts\python.exe
```

Then restart the Python language server.

### RAG is unavailable

Verify that `API_KEY` is present in `BACKEND/.env`, that the `Artifacts` directory contains PDFs, and that the `/rag/ingest` endpoint has been called.

## Development Notes

- Backend CORS is currently open for development. Restrict allowed origins before production deployment.
- Model loading happens during FastAPI startup and may take time depending on hardware.
- GPU acceleration is used when available; otherwise, inference runs on CPU.
- Keep model files, database credentials, API keys, and generated virtual-environment files out of version control.

## License

No license has been specified for this project yet.
