"""Resume processing service: PDF parsing, text extraction, and skill detection."""

import os
import re
import uuid
import logging
from typing import List, Dict, Tuple, Optional
from io import BytesIO
from pypdf import PdfReader
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.student import StudentProfile
from app.models.audit_log import ResumeFile

logger = logging.getLogger(__name__)

# Master dictionary of normalized skills for pattern matching
KNOWN_SKILLS = [
    # Programming Languages
    "Python", "Java", "C++", "C", "C#", "JavaScript", "TypeScript", "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin", "R",
    # Web & Full Stack Frameworks
    "React", "Angular", "Vue.js", "Node.js", "FastAPI", "Django", "Flask", "Express.js", "Next.js", "HTML5", "CSS3",
    "Tailwind CSS", "Bootstrap", "REST API", "GraphQL", "Redux",
    # Databases & Caching
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "SQLite", "Redis", "Elasticsearch", "Oracle",
    # Data Science & AI/ML
    "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing", "Computer Vision",
    "OpenCV", "Scikit-Learn", "Pandas", "NumPy", "TensorFlow", "PyTorch", "Keras",
    "Data Analysis", "Data Visualization", "Power BI", "Tableau", "Excel",
    # Cloud, DevOps & Tools
    "Git", "GitHub", "Docker", "Kubernetes", "Linux", "AWS", "Azure", "GCP", "CI/CD",
    # Soft & Foundational Skills
    "Problem Solving", "Critical Thinking", "Communication", "Leadership", "Teamwork",
    "Time Management", "Project Management", "Agile"
]

DEGREE_PATTERNS = [
    "B.Tech", "Bachelor of Technology", "M.Tech", "Master of Technology",
    "BCA", "MCA", "B.Sc", "M.Sc", "B.E", "Bachelor of Engineering",
    "M.E", "BBA", "MBA"
]


class ResumeService:
    """Handles secure PDF upload, text parsing, and explainable skill extraction."""

    @staticmethod
    def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
        """Extract plain text from PDF bytes using pypdf."""
        try:
            reader = PdfReader(BytesIO(pdf_bytes))
            text_parts = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_parts.append(extracted)
            return "\n".join(text_parts).strip()
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unable to parse the PDF document. Ensure the file is not corrupted or password-protected."
            )

    @classmethod
    def detect_skills(cls, text: str) -> List[str]:
        """Detect skills using case-insensitive boundary keyword matching."""
        detected = []
        text_lower = f" {text.lower()} "

        for skill in KNOWN_SKILLS:
            # Match whole words/phrases using regex word boundaries or punctuation guards
            escaped_skill = re.escape(skill.lower())
            pattern = rf"(?:\b|[^a-zA-Z0-9]){escaped_skill}(?:\b|[^a-zA-Z0-9])"
            if re.search(pattern, text_lower):
                detected.append(skill)

        return sorted(list(set(detected)))

    @classmethod
    def detect_education(cls, text: str) -> Optional[str]:
        """Detect probable degree title from resume text."""
        text_lower = text.lower()
        for deg in DEGREE_PATTERNS:
            if deg.lower() in text_lower:
                return deg
        return None

    @classmethod
    def process_and_save_resume(
        cls,
        db: Session,
        student_profile: StudentProfile,
        file: UploadFile
    ) -> Tuple[ResumeFile, List[str], Optional[str], str]:
        """Validate, store, extract, and record an uploaded resume."""
        # 1. Validation
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF resume files (.pdf) are supported."
            )

        content = file.file.read()
        file_size = len(content)
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Resume file size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )

        # 2. Secure file persistence
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        unique_prefix = uuid.uuid4().hex[:10]
        sanitized_filename = re.sub(r'[^a-zA-Z0-9_\.-]', '_', file.filename)
        stored_filename = f"{unique_prefix}_{sanitized_filename}"
        disk_path = os.path.join(settings.UPLOAD_DIR, stored_filename)

        with open(disk_path, "wb") as f:
            f.write(content)

        # 3. Extraction
        extracted_text = cls.extract_text_from_pdf_bytes(content)
        detected_skills = cls.detect_skills(extracted_text)
        detected_degree = cls.detect_education(extracted_text)

        # 4. Save metadata to resume_files table
        resume_record = ResumeFile(
            student_profile_id=student_profile.id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_path=disk_path,
            file_size_bytes=file_size,
            extracted_text=extracted_text,
            parsing_status="PROCESSED"
        )
        db.add(resume_record)

        # 5. Link resume path to student profile
        student_profile.resume_url = f"/api/v1/students/me/resume/download"
        db.commit()
        db.refresh(resume_record)

        preview = extracted_text[:300] + ("..." if len(extracted_text) > 300 else "")
        return resume_record, detected_skills, detected_degree, preview
