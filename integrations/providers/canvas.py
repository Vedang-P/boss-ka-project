from django.utils import timezone

from .base import BaseLMSProvider


class CanvasProvider(BaseLMSProvider):
    fixture_name = "canvas_demo.json"

    def fetch_live_payload(self):
        courses = self.get("api/v1/courses", params={"enrollment_state": "active", "per_page": 100})
        normalized_courses = []
        normalized_tasks = []
        grade_components = {}

        for course in courses:
            course_id = str(course["id"])
            normalized_courses.append(
                {
                    "id": course_id,
                    "code": course.get("course_code") or course.get("name", "CANVAS"),
                    "title": course.get("name", "Canvas Course"),
                    "instructor": course.get("teacher", ""),
                    "current_grade_percent": course.get("enrollments", [{}])[0].get("computed_current_score", 0),
                }
            )
            assignments = self.get(
                f"api/v1/courses/{course_id}/assignments",
                params={"per_page": 100, "include[]": "submission"},
            )
            grade_components[course_id] = []
            for assignment in assignments:
                group_id = str(assignment.get("assignment_group_id", "default"))
                if group_id not in {item["id"] for item in grade_components[course_id]}:
                    grade_components[course_id].append(
                        {
                            "id": group_id,
                            "name": assignment.get("submission_types", ["Assignments"])[0].title(),
                            "weight_percent": assignment.get("points_possible", 0) or 0,
                        }
                    )

                due_at = assignment.get("due_at") or timezone.now().isoformat()
                normalized_tasks.append(
                    {
                        "id": str(assignment["id"]),
                        "course_id": course_id,
                        "component_id": group_id,
                        "title": assignment.get("name", "Canvas Assignment"),
                        "type": "assignment",
                        "description": assignment.get("description", ""),
                        "due_at": due_at,
                        "weight_percent": assignment.get("points_possible", 0) or 0,
                        "difficulty": "medium",
                        "estimated_hours": 2,
                        "max_points": assignment.get("points_possible", 100) or 100,
                        "earned_score_percent": None,
                        "is_completed": False,
                    }
                )

        return {
            "courses": normalized_courses,
            "grade_components": grade_components,
            "tasks": normalized_tasks,
        }
