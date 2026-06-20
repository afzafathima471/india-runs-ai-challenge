"""
India Runs - Data & AI Challenge
Intelligent Candidate Ranking System
Approach: Multi-signal scoring without heavy ML dependencies
"""

import json
import csv
import math
from datetime import datetime, date

# ─── CONFIG ───────────────────────────────────────────────────────────────────
CANDIDATES_FILE = "/tmp/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl"
OUTPUT_FILE = "/home/claude/submission.csv"
TOP_N = 100

# ─── JD SIGNALS (from job_description.docx analysis) ─────────────────────────

# Absolute must-have skills (core AI/ML/search)
MUST_HAVE_SKILLS = {
    "embeddings", "vector database", "sentence-transformers", "faiss", "pinecone",
    "weaviate", "qdrant", "milvus", "opensearch", "elasticsearch", "hybrid search",
    "retrieval", "ranking", "recommendation", "nlp", "information retrieval",
    "python", "fine-tuning", "fine-tuning llms", "lora", "qlora", "peft",
    "transformer", "bert", "rag", "semantic search", "vector search",
    "learning to rank", "bm25", "ndcg", "mrr", "a/b testing",
    "machine learning", "deep learning", "pytorch", "tensorflow",
    "xgboost", "lightgbm", "feature engineering", "model deployment",
    "mlops", "kubeflow", "airflow", "spark", "data engineering",
    "neural network", "llm", "gpt", "language model", "text classification",
    "named entity recognition", "ner", "text mining", "search engine",
    "recommender system", "collaborative filtering", "matrix factorization",
    "weights & biases", "mlflow", "bentoml", "triton", "onnx",
    "image classification", "speech recognition", "tts", "gans",
    "statistical modeling", "scikit-learn", "sklearn", "pandas", "numpy",
    "databricks", "kafka", "redis", "postgresql", "mongodb",
    "docker", "kubernetes", "aws", "gcp", "azure", "cloud",
    "fastapi", "flask", "rest api", "microservices",
    "git", "github", "open source"
}

# Good-to-have (adjacent skills)
NICE_TO_HAVE_SKILLS = {
    "java", "scala", "go", "rust", "c++", "sql", "react", "typescript",
    "product management", "agile", "scrum", "system design", "distributed systems",
    "data science", "analytics", "tableau", "power bi", "hadoop"
}

# Disqualifying current companies (from JD "explicitly do NOT want")
DISQUALIFYING_COMPANIES = {
    "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini",
    "tech mahindra", "hcl", "mphasis", "hexaware"
}

# Good company types (product companies)
PRODUCT_COMPANY_INDICATORS = {
    "startup", "ai", "tech", "labs", "io", "data", "ml", "intelligence",
    "platform", "software", "systems", "solutions", "digital"
}

# Target roles
TARGET_TITLES = {
    "ai engineer", "ml engineer", "machine learning engineer", "data scientist",
    "senior engineer", "software engineer", "backend engineer", "nlp engineer",
    "research engineer", "applied scientist", "data engineer", "platform engineer",
    "search engineer", "ranking engineer", "recommendation engineer",
    "senior machine learning", "principal engineer", "staff engineer",
    "founding engineer", "tech lead"
}

# Bad roles (not relevant)
BAD_TITLES = {
    "marketing", "hr", "human resource", "content writer", "graphic designer",
    "accountant", "sales", "customer support", "operations manager",
    "project manager", "mechanical engineer", "civil engineer",
    "business analyst", "seo", "influencer", "social media"
}


def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return None


def days_since(date_str, ref_date=date(2026, 6, 10)):
    d = parse_date(date_str)
    if not d:
        return 9999
    return (ref_date - d).days


def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 0.5
    return max(0, min(1, (value - min_val) / (max_val - min_val)))


def score_candidate(cand):
    """
    Multi-signal scoring:
    1. Skills match (AI/ML core skills)       30%
    2. Career relevance (title + company)      25%  
    3. Experience years (5-9 sweet spot)       10%
    4. Redrob behavioral signals               25%
    5. Profile quality + availability          10%
    """
    profile = cand.get("profile", {})
    career = cand.get("career_history", [])
    skills = cand.get("skills", [])
    education = cand.get("education", [])
    signals = cand.get("redrob_signals", {})
    
    score = 0.0
    notes = []

    # ── 1. SKILLS MATCH (30%) ─────────────────────────────────────────────────
    skill_names_lower = {s["name"].lower() for s in skills}
    
    must_have_matches = skill_names_lower & MUST_HAVE_SKILLS
    nice_matches = skill_names_lower & NICE_TO_HAVE_SKILLS
    
    # Weighted skill score: expert > advanced > intermediate > beginner
    proficiency_weights = {"expert": 1.0, "advanced": 0.8, "intermediate": 0.5, "beginner": 0.2}
    
    skill_score = 0.0
    for s in skills:
        name_lower = s["name"].lower()
        if name_lower in MUST_HAVE_SKILLS:
            w = proficiency_weights.get(s.get("proficiency", "beginner"), 0.2)
            endorsements_bonus = min(0.2, s.get("endorsements", 0) / 100)
            skill_score += w + endorsements_bonus
    
    # Also check skill assessment scores (from redrob platform)
    assessment_scores = signals.get("skill_assessment_scores", {})
    assessment_bonus = 0
    for skill_name, score_val in assessment_scores.items():
        if skill_name.lower() in MUST_HAVE_SKILLS:
            assessment_bonus += score_val / 100 * 0.3  # up to 0.3 per assessed skill
    
    # Normalize: assume 10 strong skill matches = perfect
    normalized_skill = min(1.0, skill_score / 10.0) * 0.85 + min(0.15, assessment_bonus)
    
    # Check skill assessment scores from redrob
    ai_skills_count = len(must_have_matches)
    
    score += normalized_skill * 0.30
    notes.append(f"{ai_skills_count} AI core skills")

    # ── 2. CAREER RELEVANCE (25%) ─────────────────────────────────────────────
    career_score = 0.0
    
    current_title = profile.get("current_title", "").lower()
    
    # Title scoring
    title_match = any(t in current_title for t in TARGET_TITLES)
    bad_title = any(t in current_title for t in BAD_TITLES)
    
    if title_match:
        career_score += 0.5
    elif bad_title:
        career_score -= 0.3
    
    # Career history analysis
    product_company_exp_months = 0
    consulting_only = True
    has_ai_role = False
    total_ai_months = 0
    
    for job in career:
        company_lower = job.get("company", "").lower()
        title_lower = job.get("title", "").lower()
        duration = job.get("duration_months", 0)
        
        # Check if consulting company
        is_consulting = any(c in company_lower for c in DISQUALIFYING_COMPANIES)
        if not is_consulting:
            consulting_only = False
            product_company_exp_months += duration
        
        # Check for AI/ML role in history
        if any(t in title_lower for t in TARGET_TITLES):
            has_ai_role = True
            total_ai_months += duration
    
    if consulting_only and len(career) > 0:
        career_score -= 0.4  # JD explicitly says no consulting-only candidates
    
    if has_ai_role:
        career_score += 0.3
        total_ai_years = total_ai_months / 12
        notes.append(f"{total_ai_years:.1f} yrs AI/ML")
    
    if product_company_exp_months > 24:
        career_score += 0.2
    
    # Check career descriptions for key concepts
    full_career_text = " ".join([j.get("description", "") for j in career]).lower()
    
    key_concepts = ["ranking", "retrieval", "embedding", "recommendation", "search", 
                    "production", "deployed", "scale", "real user", "vector"]
    concept_hits = sum(1 for c in key_concepts if c in full_career_text)
    career_score += min(0.3, concept_hits * 0.05)
    
    score += max(0, min(1, career_score)) * 0.25
    notes.append(f"{profile.get('current_title', 'Unknown')} with {profile.get('years_of_experience', 0):.1f} yrs")

    # ── 3. EXPERIENCE YEARS (10%) ─────────────────────────────────────────────
    yoe = profile.get("years_of_experience", 0)
    
    # Sweet spot: 5-9 years
    if 5 <= yoe <= 9:
        exp_score = 1.0
    elif 4 <= yoe < 5 or 9 < yoe <= 12:
        exp_score = 0.7
    elif 3 <= yoe < 4 or 12 < yoe <= 15:
        exp_score = 0.4
    elif yoe > 15:
        exp_score = 0.3  # Over-experienced, likely won't accept
    else:
        exp_score = 0.2  # Under-experienced
    
    score += exp_score * 0.10

    # ── 4. REDROB BEHAVIORAL SIGNALS (25%) ────────────────────────────────────
    behavioral_score = 0.0
    
    # Recency: last active date (huge signal for availability)
    days_inactive = days_since(signals.get("last_active_date"))
    if days_inactive <= 7:
        recency_score = 1.0
    elif days_inactive <= 30:
        recency_score = 0.85
    elif days_inactive <= 90:
        recency_score = 0.6
    elif days_inactive <= 180:
        recency_score = 0.3
    else:
        recency_score = 0.1  # Inactive > 6 months = probably not looking
    
    behavioral_score += recency_score * 0.35
    
    # Open to work
    if signals.get("open_to_work_flag", False):
        behavioral_score += 0.15
    
    # Recruiter response rate
    response_rate = signals.get("recruiter_response_rate", 0)
    behavioral_score += response_rate * 0.20
    
    # Interview completion rate
    interview_rate = signals.get("interview_completion_rate", 0)
    behavioral_score += interview_rate * 0.10
    
    # Notice period (JD prefers sub-30 days)
    notice = signals.get("notice_period_days", 90)
    if notice <= 30:
        notice_score = 1.0
    elif notice <= 60:
        notice_score = 0.6
    elif notice <= 90:
        notice_score = 0.3
    else:
        notice_score = 0.1
    behavioral_score += notice_score * 0.10
    
    # GitHub activity (good signal for engineers)
    github = signals.get("github_activity_score", -1)
    if github >= 0:
        behavioral_score += (github / 100) * 0.10
    
    score += min(1.0, behavioral_score) * 0.25

    # ── 5. PROFILE QUALITY + AVAILABILITY (10%) ───────────────────────────────
    quality_score = 0.0
    
    completeness = signals.get("profile_completeness_score", 0) / 100
    quality_score += completeness * 0.4
    
    # Verified credentials
    if signals.get("verified_email", False):
        quality_score += 0.1
    if signals.get("verified_phone", False):
        quality_score += 0.1
    if signals.get("linkedin_connected", False):
        quality_score += 0.1
    
    # Education tier
    for edu in education:
        tier = edu.get("tier", "unknown")
        if tier == "tier_1":
            quality_score += 0.2
        elif tier == "tier_2":
            quality_score += 0.1
        elif tier == "tier_3":
            quality_score += 0.05
        break  # only count highest degree
    
    # Willing to relocate to Pune/Noida
    if signals.get("willing_to_relocate", False):
        quality_score += 0.1
    
    score += min(1.0, quality_score) * 0.10

    # ── HARD DISQUALIFIERS ────────────────────────────────────────────────────
    # Only consulting experience = big penalty
    if consulting_only and len(career) > 0:
        score *= 0.5
    
    # Bad title with no AI skills = penalize heavily
    if bad_title and ai_skills_count < 3:
        score *= 0.4
    
    # Inactive > 1 year = strong downweight
    if days_inactive > 365:
        score *= 0.6

    return round(min(1.0, max(0.0, score)), 4), notes


def main():
    print("Loading candidates...")
    candidates = []
    
    with open(CANDIDATES_FILE, "r") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                cand = json.loads(line)
                candidates.append(cand)
            except json.JSONDecodeError:
                continue
            
            if (i + 1) % 10000 == 0:
                print(f"  Loaded {i+1:,} candidates...")
    
    print(f"Total candidates: {len(candidates):,}")
    print("Scoring candidates...")
    
    scored = []
    for i, cand in enumerate(candidates):
        cid = cand.get("candidate_id", f"UNKNOWN_{i}")
        score, notes = score_candidate(cand)
        scored.append((cid, score, notes, cand))
        
        if (i + 1) % 20000 == 0:
            print(f"  Scored {i+1:,}...")
    
    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\nTop 10 preview:")
    for i, (cid, score, notes, cand) in enumerate(scored[:10]):
        profile = cand.get("profile", {})
        print(f"  {i+1}. {cid} | {score:.4f} | {profile.get('current_title')} {profile.get('years_of_experience')}yrs | {', '.join(notes[:2])}")
    
    # Write submission CSV
    print(f"\nWriting top {TOP_N} to {OUTPUT_FILE}...")
    
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        
        for rank, (cid, score, notes, cand) in enumerate(scored[:TOP_N], 1):
            profile = cand.get("profile", {})
            title = profile.get("current_title", "Unknown")
            yoe = profile.get("years_of_experience", 0)
            signals = cand.get("redrob_signals", {})
            response_rate = signals.get("recruiter_response_rate", 0)
            reasoning = f"{title} with {yoe:.1f} yrs; {'; '.join(notes[:3])}; response rate {response_rate:.2f}."
            writer.writerow([cid, rank, score, reasoning])
    
    print(f"✅ Submission saved: {OUTPUT_FILE}")
    print(f"\nScore distribution of top 100:")
    top_scores = [s[1] for s in scored[:100]]
    print(f"  Max: {max(top_scores):.4f}")
    print(f"  Min: {min(top_scores):.4f}")
    print(f"  Mean: {sum(top_scores)/len(top_scores):.4f}")


if __name__ == "__main__":
    main()
