# B.Tech Final Project Presentation Slides Outline
## AI-Based Smart Allocation Engine for PM Internship Scheme

---

### Slide 1: Title & Project Metadata
- **Title:** AI-Based Smart Allocation Engine for PM Internship Scheme
- **Subtitle:** An Explainable Machine Learning Platform for Talent Matching, Skill Gap Diagnosis, and Concurrency-Safe Seat Allocation
- **Academic Degree:** Bachelor of Technology (B.Tech) in Artificial Intelligence & Data Science
- **Notice:** Academic Prototype for Technical Demonstration and Algorithm Evaluation

---

### Slide 2: Motivation & Context
- **Context:** The Prime Minister's Internship Scheme provides national-scale vocational opportunities for Indian youth across premier corporate organizations.
- **The Challenge:** Millions of aspiring students from diverse collegiate backgrounds submit resumes with heterogeneous vocabularies.
- **Goal:** Build an intelligent, explainable web application that bridges students with relevant internships while giving administrators concurrency-safe seat allocation tools.

---

### Slide 3: Problem Statement & Existing Limitations
- **Keyword Mismatch:** Traditional search misses strong candidates whose resume phrasing slightly differs from job specifications.
- **The "Black-Box" Problem:** Complex neural networks lack transparent justifications, making public scheme audits and student grievance redressal difficult.
- **Seat Over-Allocation (Race Conditions):** In high-volume admission rounds, non-atomic systems risk assigning multiple candidates to the same seat or placing one candidate in multiple organizations simultaneously.

---

### Slide 4: System Architecture & Technology Stack
- **Layered Architecture Diagram:**
  - Client Browser: React 18, TypeScript, Vite, Tailwind CSS, Recharts
  - API Gateway: FastAPI, Pydantic v2, JWT HS256, Bcrypt, PyPDF
  - AI Engine: Scikit-learn (TF-IDF, Cosine Similarity), Curricula Diagnosis
  - Persistence Layer: PostgreSQL 16 / SQLite, SQLAlchemy ORM, Alembic Migrations
- **Key Design Philosophy:** Strict separation of presentation, business services, and mathematical matching.

---

### Slide 5: Explainable AI Matching Model
- **Hybrid Scoring Formula:**
  $$S = w_{\text{skill}} \cdot S_{\text{skill}} + w_{\text{edu}} \cdot S_{\text{edu}} + w_{\text{loc}} \cdot S_{\text{loc}} + w_{\text{ind}} \cdot S_{\text{ind}}$$
- **Skill Score Breakdown:**
  $$S_{\text{skill}} = 0.70 \times \text{Set Overlap Ratio} + 0.30 \times \text{TF-IDF Cosine Similarity}$$
- **Configurable Weights (Prototype Defaults):**
  - Technical Skills: 50%
  - Education Compatibility: 20%
  - Location Preference: 15%
  - Industry Preference: 15%

---

### Slide 6: Resume NLP Pipeline & Human-in-the-Loop
- **Text Extraction:** In-memory stream parsing of PDF resumes via `pypdf`.
- **NLP Keyword Extraction:** Word boundary pattern-matching across normalized technical and soft skills catalogs.
- **Human-in-the-Loop Principle:** Discovered skills are not blindly trusted; candidates must inspect and confirm detected skills before profile vector weights are updated.

---

### Slide 7: Skill Gap Diagnosis & Actionable Curricula
- **Comparative Analysis:** Compares candidate skills against mandatory and preferred internship competencies.
- **Curriculum Recommendation:** Maps missing skills to specific learning modules and estimated study hours (e.g., Docker layer caching, PyTorch tensor manipulation, FastAPI dependency injection).

---

### Slide 8: Smart Allocation Engine & Concurrency Control
- **Merit-Based Allocation:** Candidate applications ranked in descending order of compatibility score.
- **Pessimistic Row Locking (`SELECT ... FOR UPDATE`):** Locks the specific internship row during seat decrement, completely eliminating race conditions.
- **Duplicate Placement Guard:** Enforces single active allocation per candidate across the allocation round.
- **Seat Restoration:** Automated restoration of available seats if an allocation is cancelled by an administrator.

---

### Slide 9: Database Design & Normalization Proof
- **11 Normalized Tables:** `users`, `student_profiles`, `student_skills`, `companies`, `internships`, `internship_skills`, `applications`, `allocations`, `recommendations`, `resume_files`, `audit_logs`.
- **3NF Verification:** Eliminates partial dependencies and transitive dependencies; company metadata is segregated from internship offerings.
- **Integrity Enforcement:** Cascading deletes, unique compound constraints, and foreign key indexes.

---

### Slide 10: Experimental Verification & Test Suite
- **Automated Pytest Suite:** 29 automated unit and integration tests executing in under 9 seconds.
- **Coverage Areas:**
  - Password hashing and JWT security
  - Profile completion calculation
  - PDF stream parsing and skill extraction
  - TF-IDF cosine similarity and ranking
  - Rule-based eligibility disqualifications
  - Atomic seat decrement and restoration

---

### Slide 11: Live Demonstration Highlights
- **Student Journey:**
  1. Login & Dashboard review with profile completion meter.
  2. PDF resume upload and NLP keyword verification.
  3. Explore AI recommendations with natural language explanation callouts.
  4. Interactive weight tuning sliders.
  5. One-click application submission with duplicate rejection proof.
- **Admin Journey:**
  1. Real-time KPI cards & Recharts visualization.
  2. Executing Smart Allocation Round 1 with auto-locking.
  3. Seat confirmation and cancellation demonstration.

---

### Slide 12: Conclusion & Future Scope
- **Key Takeaways:**
  - High explainability builds trust in public digital infrastructure.
  - Concurrency-safe transactions prevent seat over-allocation.
  - Skill-gap diagnosis empowers students with actionable learning paths.
- **Future Scope:**
  - Fine-tuning regional Indian language multilingual embedding models.
  - Integration with DigiLocker API for instant academic document verification.
  - Expanding to multi-round Gale-Shapley stable matching algorithms.
