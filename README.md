# Shahid Nalwar — AI Persona

> AI persona for the Scaler AI Engineer Intern screening assignment.  
> Call it, chat with it, and book an interview — no human in the loop.

**Live chat**: [shahid-ai-persona.vercel.app](https://shahid-ai-persona.vercel.app)  
**Voice agent**: +1 989 582 1766  
**Book interview**: [cal.com/shahid-nalwar-bf5bxg/interview-with-shahid](https://cal.com/shahid-nalwar-bf5bxg/interview-with-shahid)

---

## What it does

| Feature | Details |
|---|---|
| **Chat** | Ask about any project, skill, or experience — RAG-grounded over real resume + GitHub |
| **Voice** | Call the Twilio number — ElevenLabs agent answers, handles interruptions, stays in character |
| **Booking** | Ask to book an interview via chat or voice — checks real Cal.com calendar, confirms booking |
| **Prompt injection** | Detects and deflects jailbreak attempts gracefully |

---

## Architecture

```
Browser / Mobile                    Phone caller
      │                                   │
      ▼                                   ▼
Next.js frontend              ElevenLabs voice agent
(Vercel)                      (Twilio phone number)
      │                                   │
      │ POST /query              Custom LLM
      │                    /v1/chat/completions
      └──────────┬────────────────────────┘
                 ▼
         FastAPI backend
         (Railway)
         ├── /query          → RAG retrieval + Groq inference
         ├── /v1/chat/completions → OpenAI-compatible for ElevenLabs
         ├── /check-availability  → Cal.com slots lookup
         ├── /book-slot           → Cal.com booking
         └── /ingest              → background re-ingestion
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
    ChromaDB   Groq     Cal.com
    (312 docs) (Llama   (v2 API)
               3.3 70B)
        │
        ▼
  Ingest pipeline
  (5 GitHub repos + resume PDF + commit history)
```

### Stack

| Component | Technology |
|---|---|
| Frontend | Next.js 14, deployed on Vercel |
| Backend | FastAPI, deployed on Railway |
| Vector DB | ChromaDB (persistent, 312 documents) |
| Embeddings | `all-MiniLM-L6-v2` (SentenceTransformers) |
| LLM | Llama 3.3 70B via Groq API |
| Voice agent | ElevenLabs Conversational AI |
| Phone | Twilio (linked to ElevenLabs) |
| Calendar | Cal.com v2 API |
| Ingestion | PyGithub + PyMuPDF + custom chunker |

---

## Repository structure

```
shahid-ai-persona/
├── app/                        # Next.js frontend
│   ├── page.js                 # Chat UI
│   └── api/chat/route.js       # API route → Railway backend
├── backend/
│   ├── main.py                 # FastAPI app (all endpoints)
│   ├── ingest.py               # RAG ingestion pipeline
│   ├── start.sh                # Container startup script
│   ├── Dockerfile              # Docker build config
│   ├── requirements.txt        # Python dependencies
│   └── data/
│       └── Shahid Nalwar-resume.pdf
└── README.md
```

---

## RAG pipeline

The knowledge base is built by `ingest.py`:

1. **GitHub scraping** — fetches all `.py`, `.md`, `.ipynb`, `.dart`, `.ts`, `.json` files from 5 repos recursively via GitHub API git tree
2. **Commit history** — fetches last 50 commits per repo as knowledge chunks
3. **Resume parsing** — extracts text from PDF using PyMuPDF (pypdf fallback)
4. **Chunking** — markdown split by headers, notebooks parsed cell-by-cell, code split by line count with 200-char overlap
5. **Manual chunks** — 7 pre-written plain-English summaries for high-probability evaluator questions
6. **Embedding** — `all-MiniLM-L6-v2` encodes all chunks locally
7. **Storage** — ChromaDB persistent vector database (`shahid_knowledge_base`)

**Repos ingested:**
- `ShahidNalwar/Focus_Gaurdian`
- `ShahidNalwar/Malaria-Detection-Using-CNN-and-GAN`
- `ShahidNalwar/Laptolyze-AI`
- `ShahidNalwar/Crop-Disease-Detection`
- `ShahidNalwar/Shahid-AI-Persona`

---

## Local setup

### Prerequisites
- Node.js 18+
- Python 3.10+
- Groq API key
- GitHub personal access token
- Cal.com API key
- ElevenLabs account

### 1. Clone and install

```bash
git clone https://github.com/ShahidNalwar/Shahid-AI-Persona.git
cd Shahid-AI-Persona

# Frontend
npm install

# Backend
cd backend
pip install -r requirements.txt
```

### 2. Environment variables

Create `backend/.env.local`:
```
GROQ_API_KEY=gsk_...
GITHUB_TOKEN=ghp_...
CALCOM_API_KEY=cal_...
```

Create `.env.local` in root:
```
RAG_API_URL=http://127.0.0.1:8080
```

### 3. Run ingestion

```bash
cd backend
python ingest.py
```

### 4. Start backend

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### 5. Start frontend

```bash
# From root
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## Deployment

| Service | Purpose | Config |
|---|---|---|
| **Vercel** | Next.js frontend | Root dir: `./`, env: `RAG_API_URL` |
| **Railway** | FastAPI backend | Root dir: `backend`, env: `GROQ_API_KEY`, `GITHUB_TOKEN`, `CALCOM_API_KEY` |

Railway uses `backend/Dockerfile` and runs `start.sh` at startup.  
`start.sh` skips ingestion if ChromaDB already has documents (avoids re-scraping on every redeploy).

### Health check
```
GET https://shahid-ai-persona-production.up.railway.app/health
→ {"status":"healthy","model_loaded":true,"database_loaded":true,"database_records":312}
```

---

## Cost breakdown

### Per chat session (avg 10 messages)
| Item | Cost |
|---|---|
| Groq API — Llama 3.3 70B (~5k tokens) | ~$0.004 |
| Railway compute (always-on) | ~$0.001 |
| Vercel (free tier) | $0.000 |
| **Total per session** | **~$0.005** |

### Per voice call (avg 3 min)
| Item | Cost |
|---|---|
| ElevenLabs — TTS + ASR (~3 min) | ~$0.09 |
| Twilio — inbound call (~3 min) | ~$0.025 |
| Groq API — LLM inference | ~$0.003 |
| Railway compute | ~$0.001 |
| **Total per call** | **~$0.12** |

### Monthly (low usage — 100 chats + 20 calls)
| Item | Cost |
|---|---|
| Railway (Hobby plan) | $5.00 |
| Groq API | ~$0.40 |
| ElevenLabs | ~$1.80 |
| Twilio | ~$0.50 |
| Vercel (free) | $0.00 |
| **Total/month** | **~$7.70** |

---

## Failure modes discovered

1. **ChromaDB version mismatch** — DB built locally with v1.5.7 but Railway installed older version. Fixed by removing DB from git and building at container startup.
2. **Cal.com wrong API path** — `/v2/slots` returns 404; correct path is `/v2/slots/available`.
3. **RAG missing code-level answers** — `ingest.py` wasn't scraping the AI-Persona repo itself. Fixed by adding it to `REPOS` and increasing `n_results` from 5 to 10.

---

## Evals

See `shahid_evals_report.pdf` for:
- Voice latency measurements (target < 2s)
- Hallucination rate (judge model method, 15-question golden set)
- Retrieval quality (precision@5, recall@10)
- 3 failure modes with root causes and fixes
- Tradeoff: Groq Llama 3.3 70B vs GPT-4o (latency vs quality)
- 2-week roadmap

---

## Author

**Shahid Nalwar**  
B.Tech AI & Data Science · N.K. Orchid College of Engineering, Solapur  
[github.com/ShahidNalwar](https://github.com/ShahidNalwar)
