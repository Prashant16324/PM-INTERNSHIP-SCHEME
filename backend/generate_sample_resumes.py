"""Generate realistic, standards-compliant sample PDF resumes for demo & evaluation testing."""

import os

def create_pdf(filepath: str, title: str, sections: list):
    """Generate a clean single-page PDF with standard Helvetica Type1 font."""
    content_lines = []
    content_lines.append(f"BT /F1 16 Tf 50 770 Td ({title}) Tj ET\n")

    y = 740
    for header, items in sections:
        content_lines.append(f"BT /F1 12 Tf 50 {y} Td ({header}) Tj ET\n")
        y -= 16
        for item in items:
            escaped = item.replace("(", "\\(").replace(")", "\\)")
            content_lines.append(f"BT /F1 10 Tf 65 {y} Td ({escaped}) Tj ET\n")
            y -= 14
        y -= 8

    stream_content = "".join(content_lines).encode("latin1")
    stream_len = len(stream_content)

    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n",
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        f"5 0 obj\n<< /Length {stream_len} >>\nstream\n".encode("latin1") + stream_content + b"\nendstream\nendobj\n",
    ]

    pdf_data = b"%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf_data))
        pdf_data += obj

    xref_offset = len(pdf_data)
    pdf_data += b"xref\n0 6\n0000000000 65535 f \n"
    for o in offsets[1:]:
        pdf_data += f"{o:010d} 00000 n \n".encode("latin1")
    pdf_data += f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("latin1")

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(pdf_data)
    print(f"Generated: {filepath} ({len(pdf_data)} bytes)")


def generate_all_samples():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dest = os.path.join(base_dir, "sample_resumes")
    frontend_dest = os.path.join(base_dir, "..", "frontend", "public", "sample_resumes")

    # Sample 1: Rahul Sharma (Cloud Backend)
    rahul_sections = [
        ("Candidate Profile", [
            "Rahul Sharma | Email: rahul.sharma@pm-internship.edu.in | Phone: +91-9876543210",
            "Location: New Delhi, India | LinkedIn: linkedin.com/in/rahul-backend"
        ]),
        ("Education", [
            "Degree: Bachelor of Technology in Computer Science & Engineering (B.Tech CSE)",
            "Institution: Delhi Technological University (DTU) | Graduation: 2026",
            "Cumulative Grade Point Average (CGPA): 8.7 / 10.0"
        ]),
        ("Technical Competencies & Skills", [
            "Programming Languages: Python, SQL, C++, Bash",
            "Frameworks & APIs: FastAPI, Flask, SQLAlchemy, RESTful Architecture",
            "DevOps & Cloud Tools: Docker, Kubernetes, Git, GitHub Actions, AWS EC2",
            "Databases: PostgreSQL, SQLite, Redis caching"
        ]),
        ("Academic Projects", [
            "Project 1: Scalable Microservice Allocation API using FastAPI and PostgreSQL",
            "Project 2: Containerized Asynchronous Task Worker utilizing Docker and Redis"
        ])
    ]

    # Sample 2: Sneha Patel (AI & Data Science)
    sneha_sections = [
        ("Candidate Profile", [
            "Sneha Patel | Email: sneha.patel@pm-internship.edu.in | Phone: +91-9812345678",
            "Location: Mumbai, India | Portfolio: github.com/snehapatel-ai"
        ]),
        ("Education", [
            "Degree: Bachelor of Technology in Artificial Intelligence & Data Science (B.Tech AI & DS)",
            "Institution: Indian Institute of Technology Bombay | Graduation: 2026",
            "Cumulative Grade Point Average (CGPA): 9.3 / 10.0"
        ]),
        ("Technical Competencies & Skills", [
            "Machine Learning: Scikit-learn, PyTorch, TensorFlow, XGBoost, Pandas, NumPy",
            "Natural Language Processing: TF-IDF, HuggingFace Transformers, NLTK, Spacy",
            "Programming & Tools: Python, SQL, Jupyter Notebooks, Git, Docker",
            "Data Visualization: Matplotlib, Seaborn, Tableau"
        ]),
        ("Academic Projects", [
            "Project 1: Transformer-based Semantic Resume Matcher and Explainability Engine",
            "Project 2: End-to-End Predictive Analytics Dashboard on Healthcare Datasets"
        ])
    ]

    # Sample 3: Aman Verma (Web Frontend)
    aman_sections = [
        ("Candidate Profile", [
            "Aman Verma | Email: aman.verma@pm-internship.edu.in | Phone: +91-9988776655",
            "Location: Lucknow, India | Portfolio: amanverma.dev"
        ]),
        ("Education", [
            "Degree: Bachelor of Computer Applications (BCA)",
            "Institution: University of Lucknow | Graduation: 2025",
            "Cumulative Grade Point Average (CGPA): 7.6 / 10.0"
        ]),
        ("Technical Competencies & Skills", [
            "Frontend Development: React, JavaScript, TypeScript, HTML5, CSS3, Tailwind CSS",
            "State & Utilities: React Router, Axios, Redux Toolkit, Lucide Icons",
            "Backend Basics: Node.js, Express, MongoDB, REST APIs",
            "Tools: Git, Vite, npm, VS Code"
        ]),
        ("Academic Projects", [
            "Project 1: Responsive Single-Page Application for Academic Internships using Vite & React",
            "Project 2: Dynamic Analytics Dashboard with Recharts and Tailwind CSS"
        ])
    ]

    for dest in [backend_dest, frontend_dest]:
        create_pdf(os.path.join(dest, "Rahul_Sharma_Backend_Resume.pdf"), "Rahul Sharma - Software Engineering Resume", rahul_sections)
        create_pdf(os.path.join(dest, "Sneha_Patel_AI_Resume.pdf"), "Sneha Patel - AI & Data Science Resume", sneha_sections)
        create_pdf(os.path.join(dest, "Aman_Verma_Web_Resume.pdf"), "Aman Verma - Frontend Developer Resume", aman_sections)

    print("All sample PDF resumes successfully generated!")

if __name__ == "__main__":
    generate_all_samples()
