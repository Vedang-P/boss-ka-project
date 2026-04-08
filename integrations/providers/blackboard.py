from django.utils import timezone

from .base import BaseLMSProvider


class BlackboardProvider(BaseLMSProvider):
    fixture_name = "blackboard_demo.json"

    def fetch_live_payload(self):
        courses_response = self.get("learn/api/public/v3/courses", params={"limit": 100})
        courses = courses_response.get("results", [])
        normalized_courses = []
        normalized_tasks = []
        grade_components = {}

        for course in courses:
            course_id = course["id"]
            normalized_courses.append(
                {
                    "id": course_id,
                    "code": course.get("courseId", "BLACKBOARD"),
                    "title": course.get("name", "Blackboard Course"),
                    "instructor": "",
                    "current_grade_percent": 0,
                }
            )
            columns_response = self.get(f"learn/api/public/v2/courses/{course_id}/gradebook/columns")
            columns = columns_response.get("results", [])
            grade_components[course_id] = []
            for column in columns:
                component_id = column["id"]
                grade_components[course_id].append(
                    {
                        "id": component_id,
                        "name": column.get("name", "Assessment"),
                        "weight_percent": column.get("score", {}).get("possible", 0),
                    }
                )
                normalized_tasks.append(
                    {
                        "id": component_id,
                        "course_id": course_id,
                        "component_id": component_id,
                        "title": column.get("name", "Blackboard Item"),
                        "type": "assignment",
                        "description": column.get("description", ""),
                        "due_at": timezone.now().isoformat(),
                        "weight_percent": column.get("score", {}).get("possible", 0),
                        "difficulty": "medium",
                        "estimated_hours": 2,
                        "max_points": column.get("score", {}).get("possible", 100),
                        "earned_score_percent": None,
                        "is_completed": False,
                    }
                )

        return {
            "courses": normalized_courses,
            "grade_components": grade_components,
            "tasks": normalized_tasks,
        }
