# Viva Presentation & Project Defense Guide
## AI-Based Smart Allocation Engine for PM Internship Scheme
### Academic Prototype for B.Tech AI & Data Science Final Examination

---

## 1. Project Abstract & Problem Definition

### Problem Statement
The Prime Minister's Internship Scheme aims to provide practical workplace training to millions of youth across India. However, manual matching and conventional keyword search face three critical engineering bottlenecks:
1. **The Skill Mismatch Bottleneck**: High variance in candidate resume vocabulary vs corporate job descriptions.
2. **The Inexplainability Problem**: Black-box neural models produce recommendations that cannot be audited or explained to students or public auditors.
3. **The Allocation Race Condition**: In high-concurrency seat allocation rounds, conventional systems risk over-allocating limited seats or assigning a single candidate to multiple organizations simultaneously.

### Our Solution
This project develops an **Explainable AI Matching and Smart Allocation Engine**:
- **NLP Resume Parser**: Extracts technical and soft competencies from PDF resumes using `pypdf` and regex boundary matching.
- **Explainable Matching Model**: Combines discrete skill set overlap ($70\%$) with Scikit-learn TF-IDF semantic cosine similarity ($30\%$) and linear multi-criteria weighting.
- **Human-in-the-Loop Transparency**: Discovered skills require candidate confirmation before updating vector representations.
- **Fair Concurrency Allocation**: Implements atomic database transactions with row-level locks (`SELECT ... FOR UPDATE`), preventing seat over-allocation and duplicate student placement.

---

## 2. Mathematical Formulations & Algorithms

### A. TF-IDF Semantic Vectorization
For a term $t$ in candidate text $d$ within document collection $D$:

$$\text{TF}(t, d) = \frac{f_{t, d}}{\sum_{t' \in d} f_{t', d}}$$

$$\text{IDF}(t, D) = \ln\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$

$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)$$

Cosine similarity between candidate representation $\mathbf{u}$ and internship requirement vector $\mathbf{v}$:

$$\text{Sim}_{\text{cosine}}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2} = \frac{\sum_{i=1}^n u_i v_i}{\sqrt{\sum_{i=1}^n u_i^2} \sqrt{\sum_{i=1}^n v_i^2}}$$

### B. Composite Explainable Scoring Function
The overall compatibility score $S \in [0, 100]$ is computed as:

$$S = w_{\text{skill}} \cdot S_{\text{skill}} + w_{\text{edu}} \cdot S_{\text{edu}} + w_{\text{loc}} \cdot S_{\text{loc}} + w_{\text{ind}} \cdot S_{\text{ind}}$$

Where prototype defaults are:
- $w_{\text{skill}} = 0.50$ (Technical skills)
- $w_{\text{edu}} = 0.20$ (Degree & branch compatibility)
- $w_{\text{loc}} = 0.15$ (Location preference: Remote = $100\%$, Exact city = $100\%$, Partial = $70\%$, Baseline = $20\%$)
- $w_{\text{ind}} = 0.15$ (Industry preference: Exact = $100\%$, Partial = $70\%$, Baseline = $30\%$)

The skill score $S_{\text{skill}}$ integrates both exact competence overlap and semantic context:

$$S_{\text{skill}} = \left( 0.70 \cdot \frac{|\text{StudentSkills} \cap \text{InternshipSkills}|}{|\text{InternshipSkills}|} + 0.30 \cdot \text{Sim}_{\text{cosine}}(\mathbf{u}, \mathbf{v}) \right) \times 100$$

### C. Concurrency-Safe Smart Allocation Algorithm

```
Algorithm: SmartAllocationEngine(Round R, MinScoreThreshold θ, AutoConfirm Flag)
Input: Candidate Applications A, Internships I, Round R
Output: Allocation Set Ω

1. CandidateList ← { a ∈ A | a.status ∈ {SUBMITTED, UNDER_REVIEW, SHORTLISTED} ∧ a.match_score ≥ θ }
2. Sort CandidateList by a.match_score DESCENDING (Merit ranking)
3. AllocatedStudentsSet ← { current active allocated student_ids }
4. Initialize Ω ← ∅

5. FOR EACH application a IN CandidateList DO:
6.    IF a.student_profile_id ∈ AllocatedStudentsSet THEN:
7.        CONTINUE (Skip duplicate allocation)
8.    
9.    LOCK internship row i ← SELECT * FROM internships WHERE id = a.internship_id FOR UPDATE
10.   
11.   IF i.available_seats ≤ 0 OR i.status ≠ 'OPEN' THEN:
12.       CONTINUE (No capacity)
13.   
14.   // Mandatory Eligibility Guard
15.   IF NOT EvaluateEligibility(a.student_profile, i) THEN:
16.       CONTINUE (Student fails mandatory eligibility)
17.   
18.   // Atomic Seat Assignment
19.   i.available_seats ← i.available_seats - 1
20.   a.status ← 'ALLOCATED'
21.   Create Allocation record with status = (AutoConfirm ? 'CONFIRMED' : 'PROVISIONAL')
22.   AllocatedStudentsSet ← AllocatedStudentsSet ∪ { a.student_profile_id }
23.   Ω ← Ω ∪ { new allocation }
24. END FOR

25. Record AuditLog entry with round metrics
26. Commit Database Transaction
27. RETURN Ω
```

### D. Gale-Shapley Multi-Capacity Deferred Acceptance Algorithm (Stable Matching)

To provide game-theoretic stability and eliminate student strategic manipulation, the platform implements the multi-capacity Gale-Shapley (Roth-Peranson) algorithm:

$$\forall (s, i) \in S \times I, \quad \neg \left( i \succ_s \mu(s) \quad \land \quad \left( |\mu(i)| < q(i) \;\lor\; s \succ_i \min_{\succ_i}(\mu(i)) \right) \right)$$

**Key Theoretical Guarantees:**
1. **Stability Guarantee**: Zero blocking pairs ($\text{Blocking Pairs} = 0$). No student and internship jointly prefer each other over their matched counterparts.
2. **Student-Optimality**: Among all possible stable matchings, every student receives the highest-ranked internship they can achieve in any stable outcome.
3. **Strategy-Proofness**: Truth-telling is a dominant strategy for students; students cannot gain by falsifying their preference rankings.

---

## 3. Database Normalization Proof (3NF)

The database schema is divided into 11 normalized tables:
- **1NF (First Normal Form)**: Every column holds atomic values. Multi-valued skills are extracted into separate normalized tables (`student_skills`, `internship_skills`).
- **2NF (Second Normal Form)**: All non-key attributes are fully functionally dependent on the primary key. In `student_skills` and `internship_skills`, proficiency and weights depend solely on their synthetic primary key with compound unique constraints (`uq_student_skill`, `uq_internship_skill`).
- **3NF (Third Normal Form)**: No transitive dependencies exist. Company metadata (name, industry, location) resides in `companies` rather than being redundantly duplicated across every `internship` row.

---

## 4. Live Viva Demonstration Script (Step-by-Step)

Follow this sequence during your project evaluation:

### Step 1: Landing Page & Public Catalog
1. Open `http://localhost:5173`.
2. Highlight the clean, responsive UI, the **Academic Prototype Notice**, and the metrics strip.
3. Click **Browse Internships** (`/internships`) to show real-time search, industry dropdown filtering, and stipend sliders.

### Step 2: Student Login & Explainable Recommendations
1. Click **Sign In**, and select the quick demo shortcut for **Rahul Sharma** (`rahul.sharma@pm-internship.edu.in`).
2. Show the **Student Dashboard** (`/dashboard`):
   - Point out the **Profile Completion Progress Bar** ($85\%$).
   - Show the **Top 3 AI Recommendations** with the green match score badge.
3. Navigate to **AI Recommendations** (`/recommendations`):
   - Show the **Tuning Weights** drawer. Adjust the Technical Skills slider from $50\%$ to $70\%$ and demonstrate that recommendations dynamically re-evaluate.
   - Point out the **AI Explanation Callout** on each card detailing exactly why the role was recommended.

### Step 3: Skill Gap Diagnosis
1. On a recommended internship card, click **View Skill Gap** (`/skill-gap/:id`).
2. Show the comparative matrix: **Matched Skills** (green) vs **Missing Competencies** (red).
3. Highlight the **Suggested Learning Curricula** showing specific topics (e.g. Docker layer caching, unit testing) and estimated study hours.

### Step 4: Resume NLP Parsing & Human-in-the-Loop
1. Navigate to **Resume & NLP Parser** (`/resume`).
2. Upload a sample PDF resume.
3. Show the parsed plain text snippet, detected degree, and the list of detected technical keywords.
4. Explain the **Human-in-the-Loop principle**: Rather than blindly updating candidate data, checkboxes require candidate review before saving.

### Step 5: Application Submission & Duplicate Prevention
1. Open an internship detail page (`/internships/1`) and click **Apply for Internship**.
2. Add a cover note and submit.
3. Demonstrate the duplicate guard: Attempting to apply to the same internship again immediately triggers a toast warning: *"You have already applied for this internship (Status: SUBMITTED)"*.

### Step 6: Admin Dashboard & Allocation Engine Execution
1. Log out, then log in using the **System Admin Demo shortcut** (`admin@pm-internship.edu.in` / `AdminSecurePass@2026`).
2. Show the **Admin Dashboard** (`/admin/dashboard`):
   - Review the 7 KPI cards.
   - Show the interactive Recharts (Applications by Status PieChart and Industry Distribution BarChart).
3. Navigate to **Smart Allocation Engine** (`/admin/allocations`):
   - Click **Execute Allocation Round**.
   - Set Round $1$, threshold $40\%$, and click **Run Round Now**.
   - Show that candidate applications are processed in merit order, seats are decremented from the internship, and the allocation appears with status `PROVISIONAL`.
4. Click **Confirm** on the allocation to simulate final administrative sign-off.
5. Click **Cancel** on another allocation to prove that **1 seat is automatically restored** to the internship.

### Step 7: Report Export & Terminal Live Walkthrough
1. On `/admin/allocations`, click **Export CSV**. The system generates a complete audit CSV containing candidate credentials, allocated company, match scores, and timestamps.
2. If the examination panel requests an automated script execution, run:
   ```powershell
   cd backend
   python demo_walkthrough.py
   ```
   This runs an 8-step live simulation of all 10 modules in under 5 seconds with zero configuration.

---

## 5. Frequently Asked Viva Questions & Model Answers

### Q1: Why did you choose TF-IDF and Cosine Similarity instead of fine-tuning a Deep Transformer (like BERT) for the baseline?
**Answer:**
> "For an academic prototype in public scheme allocation, **explainability and computational efficiency** are paramount. High-dimensional deep transformers suffer from the 'black-box' problem, making it difficult to generate transparent mathematical justifications to candidates about why they were or were not selected.
>
> Our hybrid model uses TF-IDF cosine similarity for semantic alignment ($30\%$) while grounding $70\%$ of the skill score in deterministic set-overlap. This allows us to produce exact natural language explanations. In Phase 6 of our roadmap, a fine-tuned sentence transformer can be integrated as an ensemble feature without altering the explainability layer."

### Q2: How does the system handle race conditions and concurrency during seat allocation?
**Answer:**
> "We implement **pessimistic row-level locking** using SQLAlchemy's `.with_for_update()` clause within an atomic database transaction. When the allocation algorithm evaluates an internship, that specific database row is locked at the database engine level. No other thread or simultaneous admin pass can modify `available_seats` until the transaction commits or aborts, ensuring that `available_seats` can never drop below zero."

### Q3: How do you prevent a student from being allocated to multiple internships in the same scheme cycle?
**Answer:**
> "We enforce duplicate prevention at two distinct layers:
> 1. **In-Memory Transactional Set**: During the allocation algorithm execution, we track an `already_allocated_student_ids` set. Once a student is assigned their highest-merit internship, all subsequent applications from that student are bypassed.
> 2. **Database Constraint & Filtering**: Active allocations with statuses `PROVISIONAL` or `CONFIRMED` are queried prior to processing, guaranteeing a student holds at most one active placement per allocation round."

### Q4: What happens if a student has high skill compatibility but fails a mandatory eligibility requirement like CGPA or deadline?
**Answer:**
> "Our architecture separates **scoring** from **eligibility validation**. The rule-based validator `InternshipService.evaluate_eligibility` runs first. If a candidate fails any mandatory criterion (e.g. CGPA below threshold, missing a mandatory required skill, or passing deadline), `is_eligible` is strictly set to `False`. The allocation engine explicitly checks `if not eligibility.is_eligible: continue`, ensuring ineligible candidates are never assigned seats regardless of high text similarity."

### Q5: What security safeguards are implemented in the API?
**Answer:**
> "We implement:
> 1. Native **Bcrypt hashing** with salt rounds for passwords.
> 2. **Stateless JWT tokens** (HS256) with short expiration periods and role claims (`STUDENT`, `ADMIN`, `COMPANY`).
> 3. **Role-Based Access Control (RBAC)** dependencies on FastAPI routes preventing students from modifying internship seats or running allocation routines.
> 4. **File validation** verifying PDF MIME headers and enforcing a strict 5MB size limit.
> 5. **Audit logging** recording critical administrative actions with IP and actor timestamps."

### Q6: How does your Greedy Merit Allocation compare with the Gale-Shapley Stable Marriage (Deferred Acceptance) algorithm?
**Answer:**
> "Our platform actually implements and compares **both** paradigms:
> 1. **Greedy Merit Ranking**: Allocates seats strictly to the highest composite scorers first. While fast ($O(N \log N)$) and transparent for quota policies, it is not immune to strategic manipulation by applicants.
> 2. **Gale-Shapley Student-Proposing Deferred Acceptance (Roth-Peranson Multi-Capacity Matching)**: Solves the two-sided college admissions problem. We prove mathematically that it achieves **zero blocking pairs** ($\text{Blocking Pairs} = 0$), guaranteeing that no candidate and employer mutually prefer each other over their assigned outcomes. Furthermore, by the Roth-Postlewaite theorem, it is **strategy-proof for students**, eliminating any incentive to strategically misrepresent their preferences."
