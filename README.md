# 🧾 Food Receipt QnA Application

AI-powered receipt management system with OCR and chatbot.

## 🚀 Quick Start

### 1. Install Docker

**macOS:**
```bash
brew install --cask docker
```

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

**Windows:** Download from https://www.docker.com/products/docker-desktop

### 2. Clone & Setup

```bash
# Clone repository
git clone https://github.com/FadlyHidayat2651/FoodReceipt_AI.git
cd FoodReceipt_AI

# Create .env file
cp .env.example .env
nano .env
```

Add your API key to `.env`:
```env
OPENROUTER_API_KEY=your_key_here
```

Get API key from: https://openrouter.ai/

### 3. Run

```bash
# Start application
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

### 4. Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8114

## 📖 How It Works

### Backend Services

1. **OCR Service** - Extracts text from receipt images using EasyOCR
2. **Database** 
   - SQLite: Stores receipt data (vendor, date, items, total)
   - Vector DB: Enables semantic search using FAISS
3. **AI Agent** - LangGraph powers intelligent question answering
4. **API** - Flask REST API for frontend communication

### Frontend

Simple HTML chatbot interface for uploading receipts and asking questions.

## 💬 Usage

1. Open http://localhost:3000
2. Click "Upload Receipt" → Select image → Process
3. Ask questions like:
   - "Did I buy salmon?"
   - "What's my total spending?"
   - "Show receipts from last week"

## 🔧 Troubleshooting

**Container won't start:**
```bash
docker-compose logs
docker-compose restart
```

**Port already in use:**
```bash
# Edit docker-compose.yml and change ports
ports:
  - "8115:8114"
  - "3001:3000"
```

**Database issues:**
```bash
docker-compose down -v
docker-compose up -d --build
```

## 🔄 CI/CD

GitHub Actions automatically builds and tests on every push.

**Setup:**
1. Go to GitHub repo → Settings → Secrets → Actions
2. Add secret: `OPENROUTER_API_KEY`
3. Push code → Check Actions tab

## 📁 Project Structure

```
FoodReceipt_AI/
├── src/
│   ├── backend/app/
│   │   ├── db/
│   │   │   ├── init_all.py          # Initialize all databases
│   │   │   ├── init_db.py           # SQLite setup
│   │   │   ├── init_vector_db.py    # Vector DB setup
│   │   │   ├── receipt_db.py        # SQLite operations
│   │   │   ├── receipts.db          # SQLite database
│   │   │   ├── vector_db.pkl        # FAISS vector store
│   │   │   └── vector_service.py    # Vector search
│   │   ├── services/
│   │   │   ├── agenti.py            # LangGraph agent
│   │   │   ├── llm_service_openrouter.py  # LLM integration
│   │   │   ├── ocr_service.py       # EasyOCR service
│   │   │   └── receipt_ingestion.py # Receipt processor
│   │   ├── __init__.py
│   │   └── main.py                  # Flask API
│   └── frontend/
│       └── index.html               # Web UI
├── .github/workflows/
│   └── docker-ci.yml                # CI/CD pipeline
├── Dockerfile
├── requirements.txt
└── .env                             # Your credentials
```

## 🛠️ Tech Stack

- Python 3.11, Flask, LangGraph
- EasyOCR, FAISS, SQLite
- Docker, GitHub Actions

---

**Need help?** Open an issue on GitHub