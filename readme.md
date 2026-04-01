# VeriClear

Full-stack application with FastAPI backend and modern frontend.

## Project Structure

```
VeriClear/
├── backend/          # FastAPI backend
├── frontend/         # Frontend application
└── readme.md        # This file
```

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

Backend will run at http://localhost:8000

See `backend/README.md` for detailed instructions.

### Frontend Setup

```bash
cd frontend
# Setup instructions coming soon
```

## Documentation

- Backend API Docs: http://localhost:8000/docs
- Backend README: [backend/README.md](backend/README.md)

## Tech Stack

**Backend:**
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- PostgreSQL/SQLite

**Frontend:**
- Coming soon

## Contributing

1. Clone the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request