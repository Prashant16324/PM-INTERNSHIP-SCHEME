"""Unit tests for Resume text and skill extraction."""

from io import BytesIO
from pypdf import PdfWriter
from app.services.resume_service import ResumeService


def test_detect_skills_from_text():
    sample_resume_text = """
    John Doe
    B.Tech in Computer Science and Engineering
    Technical Skills:
    Proficient in Python, SQL, Docker, and React.js.
    Hands-on experience with Machine Learning, Pandas, and Scikit-Learn.
    Strong Communication and Teamwork skills.
    """
    skills = ResumeService.detect_skills(sample_resume_text)
    assert "Python" in skills
    assert "SQL" in skills
    assert "Docker" in skills
    assert "React" in skills
    assert "Machine Learning" in skills
    assert "Pandas" in skills
    assert "Communication" in skills
    assert "Teamwork" in skills


def test_detect_degree_from_text():
    text = "Candidate has completed B.Tech in Electronics and Communication Engineering."
    deg = ResumeService.detect_education(text)
    assert deg == "B.Tech"

    text2 = "Education: Master of Technology (M.Tech) in AI."
    deg2 = ResumeService.detect_education(text2)
    assert deg2 in ["M.Tech", "Master of Technology"]


def test_extract_text_from_pdf_stream():
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    stream = BytesIO()
    writer.write(stream)
    pdf_bytes = stream.getvalue()

    # Verify blank page parses safely without crashing
    text = ResumeService.extract_text_from_pdf_bytes(pdf_bytes)
    assert isinstance(text, str)
