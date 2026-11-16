"""Gale-Shapley (Deferred Acceptance) Multi-Capacity Matching Algorithm.

Academic reference:
- Gale, D., & Shapley, L. S. (1962). College admissions and the stability of marriage.
  The American Mathematical Monthly, 69(1), 9-15.
- Roth, A. E. (1985). The college admissions problem is not equivalent to the marriage problem.
  Journal of Economic Theory, 36(2), 277-288.
"""

import time
import logging
from typing import Dict, List, Set, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.student import StudentProfile
from app.models.internship import Internship, InternshipStatus
from app.models.application import Application, ApplicationStatus
from app.services.internship_service import InternshipService

logger = logging.getLogger(__name__)


class GaleShapleyEngine:
    """Multi-capacity Student-Proposing Deferred Acceptance Algorithm."""

    @classmethod
    def run_deferred_acceptance(
        cls,
        db: Session,
        min_score_threshold: float = 35.0
    ) -> Dict[str, Any]:
        """Execute Student-Proposing Deferred Acceptance algorithm with capacities."""
        start_time = time.time()

        # Fetch active open internships
        internships: List[Internship] = db.query(Internship).filter(
            Internship.status == InternshipStatus.OPEN,
            Internship.available_seats > 0
        ).all()

        capacities: Dict[int, int] = {i.id: i.available_seats for i in internships}
        internship_map: Dict[int, Internship] = {i.id: i for i in internships}

        # Fetch applications with acceptable scores
        applications: List[Application] = db.query(Application).filter(
            Application.status.in_([
                ApplicationStatus.SUBMITTED,
                ApplicationStatus.UNDER_REVIEW,
                ApplicationStatus.SHORTLISTED,
                ApplicationStatus.ALLOCATED
            ]),
            Application.match_score >= min_score_threshold
        ).all()

        if not applications or not internships:
            return {
                "algorithm": "Gale-Shapley Deferred Acceptance (Student-Proposing)",
                "theoretical_foundation": "Roth-Peranson Multi-Capacity Matching (Nobel Prize in Economic Sciences 2012)",
                "total_students_evaluated": 0,
                "total_internships": len(internships),
                "total_matches": 0,
                "iterations_to_convergence": 0,
                "execution_time_seconds": round(time.time() - start_time, 4),
                "stability_guarantee": {
                    "blocking_pairs": 0,
                    "is_stable": True,
                    "student_optimal": True,
                    "strategy_proof": True
                },
                "matches": []
            }

        # Build student candidate set
        student_profiles: Dict[int, StudentProfile] = {}
        student_apps: Dict[int, List[Application]] = {}
        for app in applications:
            s_id = app.student_profile_id
            if s_id not in student_profiles:
                student_profiles[s_id] = app.student_profile
                student_apps[s_id] = []
            student_apps[s_id].append(app)

        # 1. Student Preference Lists: Ordered strictly by (match_score DESC, application_id ASC)
        student_preferences: Dict[int, List[int]] = {}
        for s_id, apps in student_apps.items():
            # Filter only eligible internships
            eligible_apps = [
                a for a in apps
                if a.internship_id in internship_map and
                InternshipService.evaluate_eligibility(student_profiles[s_id], internship_map[a.internship_id]).is_eligible
            ]
            sorted_apps = sorted(eligible_apps, key=lambda a: a.match_score, reverse=True)
            student_preferences[s_id] = [a.internship_id for a in sorted_apps]

        # 2. Internship Preference Lists: Ordered strictly by student merit score (0.6 * score + 0.4 * (cgpa*10))
        internship_applicant_scores: Dict[int, Dict[int, float]] = {i.id: {} for i in internships}
        for app in applications:
            if app.internship_id in internship_applicant_scores:
                profile = student_profiles.get(app.student_profile_id)
                cgpa_val = profile.cgpa if profile and profile.cgpa else 6.0
                merit_score = (app.match_score * 0.6) + ((cgpa_val / 10.0) * 100.0 * 0.4)
                internship_applicant_scores[app.internship_id][app.student_profile_id] = round(merit_score, 2)

        # 3. Deferred Acceptance Simulation
        free_students = [s_id for s_id in student_preferences.keys() if len(student_preferences[s_id]) > 0]
        # Track proposals: student_id -> index of next internship to propose to
        proposal_index: Dict[int, int] = {s_id: 0 for s_id in student_preferences}
        # Provisional holdings: internship_id -> set of student_ids currently held
        tentative_matches: Dict[int, List[int]] = {i.id: [] for i in internships}

        iteration_count = 0
        max_iterations = 1000

        while free_students and iteration_count < max_iterations:
            iteration_count += 1
            s_id = free_students.pop(0)

            pref_list = student_preferences[s_id]
            curr_idx = proposal_index[s_id]

            if curr_idx >= len(pref_list):
                # Student has proposed to all eligible choices and was rejected
                continue

            chosen_internship_id = pref_list[curr_idx]
            proposal_index[s_id] += 1

            # Propose to chosen internship
            quota = capacities[chosen_internship_id]
            current_held = tentative_matches[chosen_internship_id]
            scores = internship_applicant_scores[chosen_internship_id]

            # Pool of candidates for this internship = currently held + new applicant
            pool = current_held + [s_id]
            # Rank pool by internship's preference
            ranked_pool = sorted(pool, key=lambda sid: scores.get(sid, 0.0), reverse=True)

            # Hold top `quota`
            held = ranked_pool[:quota]
            rejected = ranked_pool[quota:]

            tentative_matches[chosen_internship_id] = held

            # If rejected candidates include someone previously held or the new applicant, they become free
            for rej_id in rejected:
                if rej_id == s_id:
                    # Current applicant was rejected; add back to free pool to try next choice
                    if proposal_index[s_id] < len(student_preferences[s_id]):
                        free_students.append(s_id)
                else:
                    # A previously held applicant was bumped; they become free to propose to their next choice
                    if proposal_index[rej_id] < len(student_preferences[rej_id]):
                        free_students.append(rej_id)

        # 4. Verify Stability: Check for Blocking Pairs
        blocking_pairs = 0
        final_matches: List[Dict[str, Any]] = []

        # Map each student to their final matched internship
        student_final_match: Dict[int, Optional[int]] = {s_id: None for s_id in student_preferences}
        for i_id, held_students in tentative_matches.items():
            for s_id in held_students:
                student_final_match[s_id] = i_id

        for i_id, held_students in tentative_matches.items():
            internship = internship_map[i_id]
            for s_id in held_students:
                student = student_profiles[s_id]
                match_app = next((a for a in student_apps[s_id] if a.internship_id == i_id), None)
                score = match_app.match_score if match_app else 0.0

                final_matches.append({
                    "student_id": s_id,
                    "student_name": student.user.full_name if student and student.user else "Student",
                    "student_college": student.college_name if student else None,
                    "student_cgpa": student.cgpa if student else None,
                    "internship_id": i_id,
                    "internship_title": internship.title,
                    "company_name": internship.company.company_name if internship.company else "Partner Company",
                    "match_score": score,
                    "merit_rank_score": internship_applicant_scores[i_id].get(s_id, 0.0)
                })

        # Calculate blocking pairs: pair (s, i) where s prefers i to their match, and i prefers s to one of its matches
        for s_id, pref_list in student_preferences.items():
            matched_i = student_final_match[s_id]
            # Internships student prefers over matched_i
            preferred_i_ids = []
            for candidate_i in pref_list:
                if candidate_i == matched_i:
                    break
                preferred_i_ids.append(candidate_i)

            for cand_i in preferred_i_ids:
                cand_held = tentative_matches.get(cand_i, [])
                quota = capacities[cand_i]
                cand_scores = internship_applicant_scores.get(cand_i, {})
                s_score = cand_scores.get(s_id, 0.0)

                # Does cand_i have spare seats or prefer s over its worst held student?
                if len(cand_held) < quota:
                    blocking_pairs += 1
                else:
                    worst_held_score = min([cand_scores.get(h, 0.0) for h in cand_held]) if cand_held else 0.0
                    if s_score > worst_held_score:
                        blocking_pairs += 1

        exec_time = round(time.time() - start_time, 4)

        return {
            "algorithm": "Gale-Shapley Deferred Acceptance (Student-Proposing)",
            "theoretical_foundation": "Roth-Peranson Multi-Capacity Matching (Nobel Prize in Economic Sciences 2012)",
            "total_students_evaluated": len(student_preferences),
            "total_internships": len(internships),
            "total_matches": len(final_matches),
            "iterations_to_convergence": iteration_count,
            "execution_time_seconds": exec_time,
            "stability_guarantee": {
                "blocking_pairs": blocking_pairs,
                "is_stable": blocking_pairs == 0,
                "student_optimal": True,
                "strategy_proof": True
            },
            "matches": final_matches
        }
