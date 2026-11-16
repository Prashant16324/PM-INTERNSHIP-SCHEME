"""AI matching engine: TF-IDF vectorization, cosine similarity, explainable scoring, and skill-gap analysis."""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.student import StudentProfile
from app.models.internship import Internship, InternshipStatus
from app.models.allocation import Recommendation
from app.schemas.matching import (
    MatchWeightConfig,
    RecommendationOut,
    SkillGapDetail,
    LearningTopicSuggestion,
)
from app.services.internship_service import InternshipService

logger = logging.getLogger(__name__)

# Curated syllabus topic suggestions for skill gaps
LEARNING_TOPICS_MAP = {
    "python": ["Object-Oriented Programming", "Decorators & Generators", "Data Structures", "Unit Testing with pytest"],
    "machine learning": ["Supervised vs Unsupervised Learning", "Linear & Logistic Regression", "Decision Trees & Random Forests", "Cross-Validation & ROC-AUC"],
    "deep learning": ["Neural Network Architectures", "Backpropagation & Optimizers", "Convolutional Neural Networks (CNNs)", "PyTorch & Tensor Basics"],
    "nlp": ["Text Tokenization & Lemmatization", "TF-IDF Vectorization", "Word Embeddings (Word2Vec, GloVe)", "Transformers & HuggingFace"],
    "fastapi": ["Dependency Injection", "Pydantic V2 Schemas", "Asynchronous Endpoint Handlers", "OpenAPI & Swagger Documentation"],
    "react": ["React Hooks (useState, useEffect)", "State Management with Context/Redux", "Component Lifecycle", "Tailwind CSS Integration"],
    "sql": ["Complex JOINs & Subqueries", "Indexing & Query Optimization", "ACID Transactions", "Database Normalization (1NF-3NF)"],
    "docker": ["Dockerfiles & Layer Caching", "Container Lifecycle", "Docker Compose for Multi-Container Apps", "Networking & Volumes"],
    "kubernetes": ["Pods, Deployments, and Services", "ConfigMaps & Secrets", "Ingress Controllers", "Horizontal Pod Autoscaling"],
    "git": ["Branching Strategies (Git Flow)", "Resolving Merge Conflicts", "Interactive Rebase", "Pull Request Workflows"],
    "aws": ["EC2 & S3 Basics", "IAM Roles & Security Groups", "AWS Lambda Serverless", "RDS Relational Databases"],
}


class MatchingEngine:
    """Explainable AI-based recommendation and skill gap analysis engine."""

    @staticmethod
    def _compute_tfidf_similarity(doc1: str, doc2: str) -> float:
        """Compute TF-IDF cosine similarity between two text descriptions."""
        if not doc1.strip() or not doc2.strip():
            return 0.0
        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf_matrix = vectorizer.fit_transform([doc1, doc2])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(max(0.0, min(1.0, sim)))
        except Exception as e:
            logger.warning(f"TF-IDF similarity calculation fallback to 0.0: {e}")
            return 0.0

    @classmethod
    def evaluate_match(
        cls,
        profile: StudentProfile,
        internship: Internship,
        weights: MatchWeightConfig = MatchWeightConfig()
    ) -> Tuple[float, float, float, float, float, bool, List[str], List[str], str]:
        """Compute multidimensional explainable match score between student and internship."""
        # 1. Evaluate Rule-Based Mandatory Eligibility
        eligibility_result = InternshipService.evaluate_eligibility(profile, internship)
        is_eligible = eligibility_result.is_eligible

        # 2. Skill Matching Factor
        student_skills = [s.skill_name.strip() for s in profile.skills]
        student_skills_lower = {s.lower() for s in student_skills}

        internship_skills = [s.skill_name.strip() for s in internship.skills]
        matched_skills = []
        missing_skills = []

        for req_skill in internship_skills:
            if req_skill.lower() in student_skills_lower:
                matched_skills.append(req_skill)
            else:
                missing_skills.append(req_skill)

        # Discrete skill overlap ratio
        if internship_skills:
            overlap_ratio = len(matched_skills) / len(internship_skills)
        else:
            overlap_ratio = 1.0  # No specific skills required

        # TF-IDF semantic similarity between student profile text and internship description
        student_text = f"{' '.join(student_skills)} {profile.bio or ''} {profile.degree or ''} {profile.branch or ''}"
        internship_text = f"{internship.title} {internship.description} {' '.join(internship_skills)} {internship.industry}"
        nlp_similarity = cls._compute_tfidf_similarity(student_text, internship_text)

        # Composite skill score: 70% direct skill overlap + 30% semantic context
        skill_score = (0.7 * overlap_ratio + 0.3 * nlp_similarity) * 100.0

        # 3. Education Compatibility Factor
        education_score = 50.0  # Baseline
        if internship.preferred_education and profile.degree:
            pref_degrees = [d.strip().lower() for d in internship.preferred_education.split(",")]
            student_deg = profile.degree.strip().lower()
            if any(deg in student_deg or student_deg in deg for deg in pref_degrees):
                education_score = 100.0
            else:
                education_score = 30.0
        elif profile.degree:
            education_score = 80.0

        # 4. Location Preference Factor
        loc_score = 20.0  # Baseline default
        intern_loc = internship.location.strip().lower()
        if intern_loc in ["remote", "virtual", "work from home"]:
            loc_score = 100.0
        elif profile.preferred_locations:
            for pref in profile.preferred_locations:
                pref_lower = pref.strip().lower()
                if pref_lower in intern_loc or intern_loc in pref_lower:
                    loc_score = 100.0
                    break
                elif any(word in intern_loc for word in pref_lower.split()):
                    loc_score = 70.0

        # 5. Industry Preference Factor
        ind_score = 30.0  # Baseline default
        intern_ind = internship.industry.strip().lower()
        if profile.preferred_industries:
            for pref in profile.preferred_industries:
                pref_lower = pref.strip().lower()
                if pref_lower in intern_ind or intern_ind in pref_lower:
                    ind_score = 100.0
                    break
                elif any(word in intern_ind for word in pref_lower.split()):
                    ind_score = 70.0

        # 6. Overall Weighted Score Calculation
        overall_score = (
            weights.skill_weight * skill_score +
            weights.education_weight * education_score +
            weights.location_weight * loc_score +
            weights.industry_weight * ind_score
        )
        overall_score = round(max(0.0, min(100.0, overall_score)), 2)

        # 7. Generate Explainable Reasoning
        explanation_bullets = []
        if is_eligible:
            explanation_bullets.append(f"Eligible for application (Seats available: {internship.available_seats}).")
        else:
            explanation_bullets.append(f"Ineligible: {'; '.join(eligibility_result.reasons)}")

        explanation_bullets.append(
            f"Skills Match: {round(skill_score, 1)}% ({len(matched_skills)}/{len(internship_skills)} skills matched)."
        )
        if matched_skills:
            explanation_bullets.append(f"Matched Skills: {', '.join(matched_skills)}.")
        if missing_skills:
            explanation_bullets.append(f"Missing Skills: {', '.join(missing_skills)}.")

        if loc_score >= 90.0:
            explanation_bullets.append(f"Location aligns with your preference ({internship.location}).")
        if ind_score >= 90.0:
            explanation_bullets.append(f"Industry aligns with your target field ({internship.industry}).")

        explanation = " | ".join(explanation_bullets)

        return (
            overall_score,
            round(skill_score, 2),
            round(education_score, 2),
            round(loc_score, 2),
            round(ind_score, 2),
            is_eligible,
            matched_skills,
            missing_skills,
            explanation
        )

    @classmethod
    def generate_recommendations_for_student(
        cls,
        db: Session,
        profile: StudentProfile,
        weights: MatchWeightConfig = MatchWeightConfig(),
        limit: int = 20
    ) -> List[RecommendationOut]:
        """Generate and cache ranked recommendations for a student profile."""
        # Query open internships with available seats
        internships = db.query(Internship).filter(
            Internship.status == InternshipStatus.OPEN
        ).all()

        recommendations = []

        for internship in internships:
            (
                overall,
                skill_s,
                edu_s,
                loc_s,
                ind_s,
                is_elig,
                matched,
                missing,
                explanation
            ) = cls.evaluate_match(profile, internship, weights)

            # Persist / update cached recommendation in DB
            rec_record = db.query(Recommendation).filter(
                Recommendation.student_profile_id == profile.id,
                Recommendation.internship_id == internship.id
            ).first()

            if not rec_record:
                rec_record = Recommendation(
                    student_profile_id=profile.id,
                    internship_id=internship.id
                )
                db.add(rec_record)

            rec_record.overall_score = overall
            rec_record.skill_score = skill_s
            rec_record.education_score = edu_s
            rec_record.location_score = loc_s
            rec_record.industry_score = ind_s
            rec_record.is_eligible = is_elig
            rec_record.matched_skills = matched
            rec_record.missing_skills = missing
            rec_record.explanation = explanation
            rec_record.generated_at = datetime.now(timezone.utc)

            recommendations.append(
                RecommendationOut(
                    internship_id=internship.id,
                    internship_title=internship.title,
                    company_name=internship.company.company_name if internship.company else "Partner Organization",
                    location=internship.location,
                    industry=internship.industry,
                    stipend=internship.stipend,
                    overall_score=overall,
                    skill_score=skill_s,
                    education_score=edu_s,
                    location_score=loc_s,
                    industry_score=ind_s,
                    is_eligible=is_elig,
                    matched_skills=matched,
                    missing_skills=missing,
                    explanation=explanation,
                    generated_at=rec_record.generated_at
                )
            )

        db.commit()

        # Rank recommendations: eligible internships first, then highest overall score
        recommendations.sort(key=lambda r: (r.is_eligible, r.overall_score), reverse=True)
        return recommendations[:limit]

    @classmethod
    def get_skill_gap_analysis(
        cls,
        profile: StudentProfile,
        internship: Internship
    ) -> SkillGapDetail:
        """Perform granular skill gap analysis with recommended learning curricula."""
        student_skills = [s.skill_name.strip() for s in profile.skills]
        student_skills_lower = {s.lower() for s in student_skills}

        internship_skills = [s.skill_name.strip() for s in internship.skills]
        matched_skills = []
        missing_skills = []

        for req in internship_skills:
            if req.lower() in student_skills_lower:
                matched_skills.append(req)
            else:
                missing_skills.append(req)

        match_pct = round((len(matched_skills) / len(internship_skills) * 100.0), 1) if internship_skills else 100.0

        # Build learning recommendations for missing skills
        learning_recs: List[LearningTopicSuggestion] = []
        for missing in missing_skills:
            lookup = missing.lower().strip()
            suggested_topics = LEARNING_TOPICS_MAP.get(
                lookup,
                [
                    f"Core principles of {missing}",
                    f"Practical project implementation using {missing}",
                    f"Industry best practices and standard documentation for {missing}"
                ]
            )
            learning_recs.append(
                LearningTopicSuggestion(
                    skill_name=missing,
                    suggested_topics=suggested_topics,
                    estimated_hours=15
                )
            )

        return SkillGapDetail(
            internship_id=internship.id,
            internship_title=internship.title,
            company_name=internship.company.company_name if internship.company else "Partner Organization",
            student_skills=student_skills,
            required_skills=internship_skills,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            skill_match_percentage=match_pct,
            learning_recommendations=learning_recs
        )
