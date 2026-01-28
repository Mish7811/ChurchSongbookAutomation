# 🎵 Monthly Songbook Automation System

A full-stack automation system to **collect, process, and generate church songbooks monthly**, designed for **team-based parallel work**.

This revamped version shifts from weekly automation to a **monthly batch workflow**, allowing a team of 3 to work simultaneously and complete **all songbooks for the upcoming month in advance**.

---

## ✨ What This System Does

- Collects **~60 songs per month**
- Splits work across **3 team members**, each handling separate weeks
- Generates **4 or 5 weekly songbooks** for a month
- Ensures everything is completed **by the last week of the previous month**
- Eliminates Google Apps Script — **pure Python backend**
- Keeps frontend and backend clearly separated

---

## 🧠 Workflow Overview

1. **Monthly Input**
   - Songs are directly inputted for the entire month (no weekly submissions).
   - Each song contains:
     - Original language lyrics (Tamil / Telugu)
     - English lyrics

2. **Team Distribution**
   - The month is logically divided into **Week 1–Week 4/5**
   - Each team member works independently on their assigned week
   - No overlap, no conflicts

3. **Processing & Automation**
   - Backend processes song data
   - Organizes songs by week
   - Prepares structured outputs for songbook generation

4. **Final Output**
   - All weekly songbooks for a month are finalized **before the month starts**
   - Ready for publishing / projection / sharing

---

## 🏗️ Project Structure

```text
songbook-automation/
│
├── frontend/
│ ├── (UI for inputting and managing monthly songs)
│ └── README.md
│
├── backend/
│ ├── (Python services for processing and automation)
│ ├── requirements.txt
│ └── README.md
│
└── README.md
```
---

## ⚙️ Tech Stack

### Backend
- **Python**
- Data processing & orchestration logic
- No Google Apps Script
- Designed for scalability and parallel execution

### Frontend
- Lightweight interface for:
  - Monthly song input
  - Week-wise organization
  - Team coordination

---

## 👥 Team-Based Design

This system is built specifically for **parallel collaboration**:

- 👤 **Team Member 1** → Week 1
- 👤 **Team Member 2** → Week 2
- 👤 **Team Member 3** → Week 3 / 4 / 5

Each workflow is isolated, ensuring:
- No race conditions
- No accidental overwrites
- Faster turnaround

---

## 🎯 Why Monthly Instead of Weekly?

| Weekly Model | Monthly Model |
|-------------|---------------|
| Repeated setup | One-time batch input |
| Tight weekly deadlines | Relaxed parallel workflow |
| Higher friction | Lower friction |
| Hard to scale | Easily scalable |

---

## 🚀 Getting Started

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
``` 
Run the backend service as per the project configuration.

### Frontend Setup

cd frontend
- install dependencies
- start dev server
(Refer to frontend/README.md for UI-specific instructions.)

---

## 🔮 Future Improvements

- Role-based access for team members
- Validation & duplicate song detection
- Auto-export to Slides / PDF
- Admin dashboard for monthly progress tracking

---

## 🤝 Contribution Guidelines
- Keep backend logic week-agnostic
- Avoid hardcoding month/week values
- Follow clear naming for week identifiers
- Write changes with parallel execution in mind

---

## 📌 Note
This system is purpose-built for church songbook preparation workflows and prioritizes:
- Reliability
- Team coordination
- Low operational friction

---

# 🧑‍💻 Author

Built with real-world church workflow constraints in mind.
Designed to scale without burning out volunteers 🙌
