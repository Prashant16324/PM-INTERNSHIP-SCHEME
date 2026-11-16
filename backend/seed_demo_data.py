"""Seed realistic academic prototype data for PM Internship Scheme demonstration."""

import os
import sys
from datetime import datetime, timedelta, timezone

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models.user import User, UserRole
from app.models.student import StudentProfile, StudentSkill
from app.models.company import Company
from app.models.internship import Internship, InternshipSkill, InternshipStatus
from app.models.application import Application, ApplicationStatus
from app.models.allocation import Allocation, AllocationStatus
from app.services.auth_service import AuthService
from app.services.matching_service import MatchingEngine
from app.utils.security import hash_password


def seed_data():
    print("Initializing Database schema...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Super Admin
        admin = AuthService.seed_initial_admin(db)
        print(f"[1/5] Super Admin verified: {admin.email}")

        # 2. Seed Partner Companies
        companies_data = [
            {
                "company_name": "Tata Consultancy Services",
                "industry": "Information Technology",
                "location": "Mumbai",
                "website": "https://www.tcs.com",
                "description": "Leading global IT services, consulting, and digital solutions organization.",
            },
            {
                "company_name": "Infosys AI Labs",
                "industry": "Artificial Intelligence",
                "location": "Bangalore",
                "website": "https://www.infosys.com",
                "description": "Enterprise artificial intelligence, cognitive automation, and digital core services.",
            },
            {
                "company_name": "Bharat Tech Solutions",
                "industry": "Data Analytics",
                "location": "Delhi",
                "website": "https://www.bharattech.edu.in",
                "description": "Public sector data analytics and digital public infrastructure engineering.",
            },
            {
                "company_name": "Jio Platforms Limited",
                "industry": "Cloud Computing",
                "location": "Pune",
                "website": "https://www.jio.com",
                "description": "Cloud native infrastructure, 5G applications, and massive scale digital platforms.",
            },
            {
                "company_name": "Wipro Digital Consulting",
                "industry": "Consulting",
                "location": "Hyderabad",
                "website": "https://www.wipro.com",
                "description": "Technology consulting, cyber security, and enterprise cloud modernization.",
            },
        ]

        companies = []
        for cdata in companies_data:
            c = db.query(Company).filter(Company.company_name == cdata["company_name"]).first()
            if not c:
                c = Company(**cdata, is_verified=True)
                db.add(c)
                db.flush()
            companies.append(c)
        db.commit()
        print(f"[2/5] Partner Companies seeded: {len(companies)}")

        # 3. Seed Internships with Required Skills
        internships_data = [
            {
                "company_id": companies[0].id,
                "title": "Python & Cloud Backend Intern",
                "description": "Architect and scale RESTful APIs, asynchronous worker tasks, and microservices supporting national data workflows.",
                "industry": "Information Technology",
                "location": "Mumbai",
                "duration_weeks": 12,
                "stipend": 22000.0,
                "total_seats": 5,
                "available_seats": 5,
                "min_cgpa": 7.0,
                "preferred_education": "B.Tech, BCA, MCA",
                "status": InternshipStatus.OPEN,
                "skills": [
                    ("Python", True, 2.0),
                    ("FastAPI", True, 1.5),
                    ("SQL", True, 1.0),
                    ("Docker", False, 1.0),
                ]
            },
            {
                "company_id": companies[1].id,
                "title": "NLP & Machine Learning Research Intern",
                "description": "Develop natural language processing pipelines, transformer embeddings, and recommendation algorithms for citizen services.",
                "industry": "Artificial Intelligence",
                "location": "Bangalore",
                "duration_weeks": 16,
                "stipend": 28000.0,
                "total_seats": 3,
                "available_seats": 3,
                "min_cgpa": 8.0,
                "preferred_education": "B.Tech, M.Tech, M.Sc",
                "status": InternshipStatus.OPEN,
                "skills": [
                    ("Python", True, 2.0),
                    ("Machine Learning", True, 2.0),
                    ("NLP", True, 1.5),
                    ("Pandas", False, 1.0),
                ]
            },
            {
                "company_id": companies[2].id,
                "title": "Public Scheme Data Analyst Intern",
                "description": "Analyze scheme metrics, build interactive dashboards, and perform statistical modeling on educational and welfare datasets.",
                "industry": "Data Analytics",
                "location": "Delhi",
                "duration_weeks": 10,
                "stipend": 20000.0,
                "total_seats": 4,
                "available_seats": 4,
                "min_cgpa": 6.8,
                "preferred_education": "B.Tech, B.Sc, BCA",
                "status": InternshipStatus.OPEN,
                "skills": [
                    ("SQL", True, 2.0),
                    ("Python", True, 1.5),
                    ("Excel", True, 1.0),
                    ("Power BI", False, 1.0),
                ]
            },
            {
                "company_id": companies[3].id,
                "title": "Cloud DevOps & Kubernetes Intern",
                "description": "Manage containerized deployments, Helm charts, and continuous integration pipelines across distributed edge clusters.",
                "industry": "Cloud Computing",
                "location": "Pune",
                "duration_weeks": 12,
                "stipend": 24000.0,
                "total_seats": 2,
                "available_seats": 2,
                "min_cgpa": 7.5,
                "preferred_education": "B.Tech",
                "status": InternshipStatus.OPEN,
                "skills": [
                    ("Docker", True, 2.0),
                    ("Kubernetes", True, 2.0),
                    ("Linux", True, 1.5),
                    ("Git", False, 1.0),
                ]
            },
            {
                "company_id": companies[4].id,
                "title": "Full Stack Web Engineering Intern",
                "description": "Design responsive, accessible user interfaces using React, TypeScript, and modern state management integrated with secure backends.",
                "industry": "Information Technology",
                "location": "Remote",
                "duration_weeks": 8,
                "stipend": 18000.0,
                "total_seats": 6,
                "available_seats": 6,
                "min_cgpa": 6.5,
                "preferred_education": "B.Tech, BCA",
                "status": InternshipStatus.OPEN,
                "skills": [
                    ("React", True, 2.0),
                    ("JavaScript", True, 1.5),
                    ("HTML5", True, 1.0),
                    ("CSS3", False, 1.0),
                ]
            },
        ]

        internships = []
        for idata in internships_data:
            skills = idata.pop("skills")
            intern = db.query(Internship).filter(Internship.title == idata["title"]).first()
            if not intern:
                intern = Internship(**idata)
                db.add(intern)
                db.flush()

                for sname, is_mand, w in skills:
                    db.add(InternshipSkill(
                        internship_id=intern.id,
                        skill_name=sname,
                        is_mandatory=is_mand,
                        weight=w
                    ))
            internships.append(intern)
        db.commit()
        print(f"[3/5] Internships & Required Skills seeded: {len(internships)}")

        # 4. Seed Demo Students
        students_demo = [
            {
                "email": "rahul.sharma@pm-internship.edu.in",
                "password": "StudentPass@2026",
                "full_name": "Rahul Sharma",
                "phone_number": "9876543210",
                "college_name": "Delhi Technological University",
                "degree": "B.Tech",
                "branch": "Computer Science & Engineering",
                "graduation_year": 2026,
                "cgpa": 8.7,
                "preferred_locations": ["Mumbai", "Delhi", "Remote"],
                "preferred_industries": ["Information Technology", "Artificial Intelligence"],
                "bio": "Passionate backend engineer with expertise in FastAPI, PostgreSQL, and scalable systems.",
                "skills": [
                    ("Python", "ADVANCED"),
                    ("FastAPI", "INTERMEDIATE"),
                    ("SQL", "INTERMEDIATE"),
                    ("Docker", "BEGINNER"),
                ]
            },
            {
                "email": "sneha.patel@pm-internship.edu.in",
                "password": "StudentPass@2026",
                "full_name": "Sneha Patel",
                "phone_number": "9123456780",
                "college_name": "IIT Bombay",
                "degree": "B.Tech",
                "branch": "AI & Data Science",
                "graduation_year": 2026,
                "cgpa": 9.3,
                "preferred_locations": ["Bangalore", "Pune"],
                "preferred_industries": ["Artificial Intelligence", "Data Analytics"],
                "bio": "AI/ML researcher focused on NLP embeddings and explainable recommendation architectures.",
                "skills": [
                    ("Python", "ADVANCED"),
                    ("Machine Learning", "ADVANCED"),
                    ("NLP", "INTERMEDIATE"),
                    ("Pandas", "ADVANCED"),
                    ("SQL", "INTERMEDIATE"),
                ]
            },
            {
                "email": "aman.verma@pm-internship.edu.in",
                "password": "StudentPass@2026",
                "full_name": "Aman Verma",
                "phone_number": "9988776655",
                "college_name": "GGSIPU Delhi",
                "degree": "BCA",
                "branch": "Computer Applications",
                "graduation_year": 2025,
                "cgpa": 7.6,
                "preferred_locations": ["Remote", "Delhi"],
                "preferred_industries": ["Information Technology"],
                "bio": "Front-end enthusiast building clean, accessible web components in React and TypeScript.",
                "skills": [
                    ("React", "INTERMEDIATE"),
                    ("JavaScript", "INTERMEDIATE"),
                    ("HTML5", "ADVANCED"),
                    ("CSS3", "ADVANCED"),
                ]
            }
        ]

        student_profiles = []
        for sdata in students_demo:
            skills = sdata.pop("skills")
            user = db.query(User).filter(User.email == sdata["email"]).first()
            if not user:
                user = User(
                    email=sdata["email"],
                    hashed_password=hash_password(sdata["password"]),
                    full_name=sdata["full_name"],
                    role=UserRole.STUDENT,
                    is_active=True,
                    is_verified=True
                )
                db.add(user)
                db.flush()

                profile = StudentProfile(
                    user_id=user.id,
                    phone_number=sdata["phone_number"],
                    college_name=sdata["college_name"],
                    degree=sdata["degree"],
                    branch=sdata["branch"],
                    graduation_year=sdata["graduation_year"],
                    cgpa=sdata["cgpa"],
                    preferred_locations=sdata["preferred_locations"],
                    preferred_industries=sdata["preferred_industries"],
                    bio=sdata["bio"],
                    profile_completion_percentage=85
                )
                db.add(profile)
                db.flush()

                for sname, lvl in skills:
                    db.add(StudentSkill(
                        student_profile_id=profile.id,
                        skill_name=sname,
                        proficiency_level=lvl,
                        source="MANUAL"
                    ))
                db.commit()
                student_profiles.append(profile)
            else:
                profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
                student_profiles.append(profile)

        print(f"[4/5] Demo Students & Profiles seeded: {len(student_profiles)}")

        # 5. Pre-generate recommendations and seed sample applications
        for profile in student_profiles:
            MatchingEngine.generate_recommendations_for_student(db, profile)

        # Seed sample application from Rahul to Python Backend
        if student_profiles and internships:
            existing_app = db.query(Application).filter(
                Application.student_profile_id == student_profiles[0].id,
                Application.internship_id == internships[0].id
            ).first()
            if not existing_app:
                db.add(Application(
                    student_profile_id=student_profiles[0].id,
                    internship_id=internships[0].id,
                    status=ApplicationStatus.SHORTLISTED,
                    match_score=88.5,
                    cover_letter="I have extensive experience building FastAPI backends with Docker."
                ))

            # Seed sample application from Sneha to NLP Research
            existing_app2 = db.query(Application).filter(
                Application.student_profile_id == student_profiles[1].id,
                Application.internship_id == internships[1].id
            ).first()
            if not existing_app2:
                db.add(Application(
                    student_profile_id=student_profiles[1].id,
                    internship_id=internships[1].id,
                    status=ApplicationStatus.SUBMITTED,
                    match_score=94.2,
                    cover_letter="Deeply passionate about transformers and natural language intelligence."
                ))
            db.commit()

        print("[5/5] Recommendations & initial applications seeded successfully!")
        print("\nDemo Seed Completed! Ready for presentation and viva demonstrations.")

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
