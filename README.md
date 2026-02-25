<div align="center">

![Seatify AI Banner](https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=1200&auto=format&fit=crop&q=80)

# 🍽️ Seatify AI — Sri Lanka

**Your intelligent dining companion for reservations across the Pearl of the Indian Ocean**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=flat&logo=openai&logoColor=white)](https://openai.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📖 About the Project

**Seatify AI** is a full-stack, agentic restaurant reservation assistant built specifically for Sri Lanka's dining scene. Powered by **OpenAI GPT-4o** with real-time tool calling, it understands natural language queries and handles the complete reservation lifecycle — from discovery to booking confirmation — through a sleek glassmorphism-styled chat interface.

The system spans **30 curated Sri Lankan restaurants** across Colombo, Galle, Kandy, Mirissa, Sigiriya, Negombo, and more — covering cuisines from traditional Sri Lankan fare to Ayurvedic dining and beach fusion.

---

## ✨ Features

### 🤖 Agentic AI Engine
- **GPT-4o function calling** — the AI autonomously decides when to search restaurants, check availability, or confirm bookings
- **Multi-turn conversation memory** — maintains full context across the entire chat session
- **Tool orchestration** — chains multiple API calls in a single reasoning loop
- **Function simulation detection** — guards against hallucinated tool responses
- **Live agent trace** — collapsible expander shows real-time tool calls, arguments, and results

### 🔍 Restaurant Discovery
- Search by **area** (Colombo, Galle, Kandy, Mirissa, Sigiriya…)
- Filter by **cuisine** (Sri Lankan, Seafood, Ceylonese, Tamil, Ayurvedic, Beach Fusion, Continental)
- Filter by **group size** and **opening hours**
- View restaurant details: description, capacity, rating, contact, and price range

### 📅 Reservation Management
- **Book a table** with name, contact number, party size, date, and time
- **Capacity validation** — checks real-time availability before confirming
- **Placeholder detection** — rejects incomplete bookings with missing fields
- Instant booking confirmation with booking reference

### 🎨 Glassmorphism UI
- Dark aesthetic with **Galle Fort hero image** backdrop
- **Playfair Display** serif headline with gradient text
- Frosted glass cards with `backdrop-filter: blur()`
- Smooth hover lift effects on all interactive elements
- Pulsing AI online indicator, floating hero icon, fade-in animations
- Sri Lanka photo mosaic in sidebar (Galle Fort · Sigiriya · Mirissa · Landscape)
- Quick suggestion chips for instant prompts

---

## 🏗️ Codebase Structure

```
Seatify-AI/
│
├── seatify_app.py              # Streamlit frontend — UI, chat loop, session state
│
├── agent/
│   ├── conversation_engine.py  # OpenAI API calls, response normalisation, tool execution
│   ├── toolkit.py              # Tool schema definitions (function specs for GPT-4o)
│   └── prompt_library.py       # System prompts + few-shot examples (3 variants)
│
├── data/
│   ├── service_api.py          # FastAPI backend — search & reservation endpoints
│   ├── restaurant_list.json    # 30 Sri Lankan restaurants (r001–r030)
│   └── bookings_list.json      # Bookings store
│
├── .env                        # Local secrets (gitignored)
├── .env.example                # Template for environment variables
├── requirements.txt            # Python dependencies
├── .gitignore
└── README.md
```

### Key Module Responsibilities

| File | Role |
|---|---|
| `seatify_app.py` | Streamlit UI, CSS injection, chat rendering, session state |
| `agent/conversation_engine.py` | `generate_chat_completion()`, `normalize_chat_response()`, `execute_tool_calls()` |
| `agent/toolkit.py` | JSON schema definitions for `search_restaurants` and `make_reservation` tools |
| `agent/prompt_library.py` | System prompt with Sri Lanka context, few-shot conversation examples |
| `data/service_api.py` | FastAPI app with `/search` and `/reserve` endpoints, capacity checking |
| `data/restaurant_list.json` | Restaurant data — name, area, cuisine, capacity, hours, rating, price |
| `data/bookings_list.json` | Booking records — persisted reservations |

---

## 🚀 Getting Started

### Prerequisites
- Python **3.10+**
- An **OpenAI API key** with GPT-4o access

### 1 — Clone the Repository
```bash
git clone https://github.com/your-username/Seatify-AI.git
cd Seatify-AI
```

### 2 — Create & Activate Virtual Environment
```powershell
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
```bash
# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### 4 — Configure Environment Variables
```bash
# Copy the template
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
```
Edit `.env` and add your key:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 5 — Run the Application

Open **two separate terminals** in the project root:

**Terminal 1 — FastAPI Backend (port 8000)**
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn data.service_api:app --host 127.0.0.1 --port 8000
```

**Terminal 2 — Streamlit Frontend (port 8501)**
```powershell
.\.venv\Scripts\Activate.ps1
streamlit run seatify_app.py --server.port 8501
```

Then open **http://localhost:8501** in your browser.

---

## 💬 Example Conversations

```
User  → Show me seafood restaurants near Mirissa
AI    → [calls search_restaurants] Here are 3 seafood options in Mirissa…

User  → Book a table at Ocean Breeze for 4 people this Saturday at 7 PM
AI    → [calls make_reservation] Your table is confirmed! Booking ref: BK-00247
```

**Quick prompts available in the UI:**
- 🔍 Show me restaurants in Galle
- 🦞 Seafood near Mirissa Bay
- 👥 Book for 8 people this Friday
- 🕗 What's open after 9 PM?
- ⭐ Top Kandy restaurants

---

## 🍴 Restaurants & Coverage

| Area | Cuisine Focus |
|---|---|
| Colombo | Sri Lankan, Continental, Seafood |
| Galle | Ceylonese, Beach Fusion, Seafood |
| Kandy | Tamil Sri Lankan, Ayurvedic, Sri Lankan |
| Mirissa | Beach Fusion, Seafood |
| Sigiriya | Sri Lankan, Ayurvedic |
| Negombo | Seafood, Sri Lankan |
| Nuwara Eliya | Ceylonese, Continental |
| Trincomalee | Seafood, Tamil Sri Lankan |

---

## 🔮 Future Enhancements

| Priority | Enhancement |
|---|---|
| 🔴 High | **Persistent database** — replace JSON files with PostgreSQL / Supabase |
| 🔴 High | **User authentication** — login system with booking history per user |
| 🟠 Medium | **SMS / Email confirmations** — send booking details via Twilio or SendGrid |
| 🟠 Medium | **Real-time availability calendar** — visual date/time picker with slot display |
| 🟠 Medium | **Restaurant ratings & reviews** — user-submitted feedback after dining |
| 🟡 Normal | **Multi-language support** — Sinhala and Tamil language responses |
| 🟡 Normal | **Map integration** — Leaflet/Google Maps with restaurant pins |
| 🟡 Normal | **Voice input** — Web Speech API for hands-free booking |
| 🟡 Normal | **Recommendation engine** — ML-based personalised suggestions |
| 🟢 Low | **Admin dashboard** — restaurant management portal for owners |
| 🟢 Low | **Mobile app** — React Native wrapper around the API |
| 🟢 Low | **Multi-city expansion** — extend beyond Sri Lanka |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **AI Model** | OpenAI GPT-4o (function calling) |
| **Frontend** | Streamlit 1.35+ |
| **Backend API** | FastAPI + Uvicorn |
| **Data Validation** | Pydantic v2 |
| **Environment** | python-dotenv |
| **Styling** | Custom CSS — glassmorphism, animations, Google Fonts |
| **Data Store** | JSON (restaurant & bookings) |

---

## 👥 Team

Built by **Azaam Ahmed & Team** © 2026

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
