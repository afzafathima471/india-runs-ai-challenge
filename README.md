# Intelligent Candidate Ranking System
### India Runs — Data & AI Challenge | Hack2Skill

> **Role:** Senior AI Engineer — Founding Team (Redrob AI)  
> **Dataset:** 100,000 candidates (Redrob platform)  
> **Output:** Top 100 ranked candidates with scores and reasoning

---

## 🧠 Approach

Most keyword-matching systems fail because they treat a job description as a bag of words. This solution treats it as a **hiring intent document** — understanding *what the role actually needs* vs what it literally says.

### The Core Insight

The JD itself warned us:
> *"The right answer is NOT to find candidates whose skills section contains the most AI keywords. That's a trap."*

So instead of simple keyword matching, this system uses **multi-signal scoring** across 5 dimensions:

```
┌─────────────────────────────────────────────────────────┐
│              SCORING DIMENSIONS                          │
├──────────────────────────┬──────────────────────────────┤
│ 1. Skills Match          │ 30% — AI/ML core skills,     │
│                          │       proficiency, endorsements│
├──────────────────────────┼──────────────────────────────┤
│ 2. Career Relevance      │ 25% — Title match, product   │
│                          │       company exp, career text│
├──────────────────────────┼──────────────────────────────┤
│ 3. Experience Years      │ 10% — Sweet spot: 5-9 years  │
├──────────────────────────┼──────────────────────────────┤
│ 4. Behavioral Signals    │ 25% — Activity recency,      │
│                          │       response rate, notice  │
├──────────────────────────┼──────────────────────────────┤
│ 5. Profile Quality       │ 10% — Completeness, verified,│
│                          │       education tier         │
└──────────────────────────┴──────────────────────────────┘
```

---

## 🚫 Hard Disqualifiers (from JD)

| Signal | Action |
|--------|--------|
| Only consulting company experience (TCS/Infosys/Wipro etc.) | 50% score penalty |
| Bad title (Marketing/HR/Accountant) + < 3 AI skills | 60% score penalty |
| Inactive > 1 year on platform | 40% score penalty |

---

## 📁 Repository Structure

```
india-runs-ai-challenge/
│
├── ranker.py                  # Main scoring system
├── submission.csv             # Final ranked output (Top 100)
├── requirements.txt           # Dependencies
├── approach.pdf               # Methodology presentation
└── README.md                  # This file
```

---

## ⚙️ How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Place dataset
Put `candidates.jsonl` in the same directory (download from challenge portal).

### 3. Run the ranker
```bash
python ranker.py
```

Output: `submission.csv` with top 100 ranked candidates.

---

## 📊 Scoring Details

### Skills Scoring
- Each skill matched to a curated AI/ML skills dictionary
- Weighted by proficiency: `expert=1.0, advanced=0.8, intermediate=0.5, beginner=0.2`
- Endorsement bonus: `min(0.2, endorsements/100)`
- Platform assessment scores included as additional signal

### Behavioral Signals Breakdown
```
Recency (last active):   35% of behavioral score
Open to work flag:       15%
Recruiter response rate: 20%
Interview completion:    10%
Notice period:           10%
GitHub activity:         10%
```

### Career Text Analysis
Career descriptions are scanned for key concepts:
`ranking, retrieval, embedding, recommendation, search, production, deployed, scale, vector`

Each concept hit adds to career relevance score — this catches candidates who did the work but didn't list the buzzwords as skills.

---

## 🎯 Why This Works Better Than Keyword Matching

**Example:**  
A candidate titled "Backend Engineer" with 7 years at a product company, whose career description mentions *"built candidate-JD matching pipeline using Kafka and Spark"* and is actively responding to recruiters — scores higher than a "Senior AI Engineer" who listed 15 AI keywords but hasn't logged in for 8 months and works only at consulting firms.

**The behavioral layer is critical.** A perfect-on-paper candidate who is unreachable is useless to a recruiter.

---

## 🔧 Tech Stack

- **Python 3.10+** — core language
- **pandas** — data handling
- **JSON/CSV** — input/output formats
- No heavy ML dependencies — runs on any machine in ~30 seconds for 100K candidates

---

## 📈 Results

| Metric | Value |
|--------|-------|
| Candidates processed | 100,000 |
| Top score | 0.9603 |
| Bottom score (rank 100) | 0.8448 |
| Mean score (top 100) | 0.8826 |
| Avg experience (top 10) | 7.1 years |
| Most common title (top 10) | Senior ML/AI Engineer |

---

## 👤 Author

**Afza Fathima**  
B.E. Computer Science Engineering — KIT Tiptur (VTU)  
Python Full Stack + AI/ML Intern  
GitHub: [@afzafathima471](https://github.com/afzafathima471)

---

*Submitted for India Runs — Data & AI Challenge, Hack2Skill, June 2026*
