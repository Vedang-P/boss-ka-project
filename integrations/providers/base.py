import json
from abc import ABC, abstractmethod
from pathlib import Path

import requests
from django.conf import settings

from integrations.exceptions import ProviderError


class BaseLMSProvider(ABC):
    fixture_name = ""

    def __init__(self, connection):
        self.connection = connection

    @property
    def headers(self):
        if self.connection.access_token:
            return {"Authorization": f"Bearer {self.connection.access_token}"}
        return {}

    def load_demo_payload(self):
        fixture_path = Path(settings.BASE_DIR) / "integrations" / "demo_data" / self.fixture_name
        with fixture_path.open("r", encoding="utf-8") as fixture_file:
            return json.load(fixture_file)

    def validate_credentials(self):
        if self.connection.mode == "demo":
            return True, "Demo mode uses built-in seeded data."

        if not self.connection.base_url:
            return False, "Live mode requires a base URL."
        if self.connection.auth_type == "token" and not self.connection.access_token:
            return False, "Token mode requires an access token."
        if self.connection.auth_type == "oauth" and not (self.connection.client_id and self.connection.client_secret):
            return False, "OAuth mode requires both client ID and client secret."
        return True, "Live credentials look complete."

    def get(self, path, params=None):
        url = f"{self.connection.base_url.rstrip('/')}/{path.lstrip('/')}"
        response = requests.get(url, headers=self.headers, params=params, timeout=15)
        response.raise_for_status()
        return response.json()

    def fetch_payload(self):
        valid, message = self.validate_credentials()
        if not valid:
            raise ProviderError(message)
        if self.connection.mode == "demo":
            return self.load_demo_payload()
        return self.fetch_live_payload()

    @abstractmethod
    def fetch_live_payload(self):
        raise NotImplementedError
