import base64

import requests as http_client
from django.utils import timezone

from integrations.exceptions import ProviderError

from .base import BaseLMSProvider


class BlackboardProvider(BaseLMSProvider):
    fixture_name = "blackboard_demo.json"

    # ------------------------------------------------------------------
    # OAuth2 helpers (live mode only)
    # ------------------------------------------------------------------

    def get_oauth2_token(self):
        """
        Exchange client_id + client_secret for a short-lived Bearer token
        using the Blackboard OAuth2 client_credentials grant.

        Blackboard token endpoint:
            POST {base_url}/learn/api/public/v1/oauth2/token
            Authorization: Basic base64(client_id:client_secret)
            Content-Type:  application/x-www-form-urlencoded
            Body:          grant_type=client_credentials
        """
        client_id = self.connection.client_id
        client_secret = self.connection.client_secret
        base_url = self.connection.base_url.rstrip("/")

        if not client_id or not client_secret:
            raise ProviderError(
                "Blackboard live mode requires a Client ID and Client Secret."
            )

        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

        try:
            response = http_client.post(
                f"{base_url}/learn/api/public/v1/oauth2/token",
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={"grant_type": "client_credentials"},
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
        except http_client.RequestException as exc:
            raise ProviderError(
                f"Blackboard OAuth2 token exchange failed: {exc}"
            ) from exc
        except ValueError as exc:
            raise ProviderError(
                "Blackboard OAuth2 response was not valid JSON."
            ) from exc

        token = data.get("access_token")
        if not token:
            raise ProviderError(
                "Blackboard OAuth2 response did not contain an access_token. "
                f"Response keys: {list(data.keys())}"
            )
        return token

    @property
    def _live_headers(self):
        """Headers using the OAuth2 Bearer token obtained at sync time."""
        token = getattr(self, "_oauth_token", None)
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

    def live_get(self, path, params=None):
        """
        Wrapper around the base class get() that injects the OAuth2 token
        instead of the stored access_token field (which is unused for
        Blackboard OAuth connections).
        """
        base_url = self.connection.base_url.rstrip("/")
        url = f"{base_url}/{path.lstrip('/')}"
        try:
            response = http_client.get(
                url,
                headers=self._live_headers,
                params=params,
                timeout=15,
            )
            response.raise_for_status()
            return response.json()
        except http_client.RequestException as exc:
            raise ProviderError(f"Blackboard API request failed: {exc}") from exc
        except ValueError as exc:
            raise ProviderError("Blackboard API response was not valid JSON.") from exc

    # ------------------------------------------------------------------
    # Provider interface
    # ------------------------------------------------------------------

    def fetch_live_payload(self):
        # Step 1: exchange client credentials for a Bearer token
        self._oauth_token = self.get_oauth2_token()

        # Step 2: fetch enrolled courses
        courses_response = self.live_get(
            "learn/api/public/v3/courses", params={"limit": 100}
        )
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

            # Step 3: fetch gradebook columns (= assessments) for each course
            try:
                columns_response = self.live_get(
                    f"learn/api/public/v2/courses/{course_id}/gradebook/columns"
                )
                columns = columns_response.get("results", [])
            except ProviderError:
                columns = []

            grade_components[course_id] = []

            for column in columns:
                component_id = column["id"]

                # Resolve due date — Blackboard columns carry a dueDate field
                raw_due = column.get("dueDate") or column.get("due_at")
                if raw_due:
                    due_at = raw_due
                else:
                    due_at = timezone.now().isoformat()

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
                        "due_at": due_at,
                        "weight_percent": column.get("score", {}).get("possible", 0),
                        "difficulty": "medium",
                        "estimated_hours": 2,
                        "max_points": column.get("score", {}).get("possible", 100)
                        or 100,
                        "earned_score_percent": None,
                        "is_completed": False,
                    }
                )

        return {
            "courses": normalized_courses,
            "grade_components": grade_components,
            "tasks": normalized_tasks,
        }
