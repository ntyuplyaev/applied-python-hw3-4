from locust import HttpUser, task, between, events
import random
import requests
from datetime import datetime, timedelta

global_aliases = []


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("[Locust] Generating short links before test start...")

    for i in range(10):
        payload = {
            "original_url": f"https://example.com/test-{i}",
            "custom_alias": f"alias{i}",
            "expires_at": (datetime.utcnow() + timedelta(days=1)).isoformat()
        }

        try:
            response = requests.post("http://localhost:8000/links/shorten", json=payload)
            if response.status_code == 200:
                global_aliases.append(payload["custom_alias"])
            elif response.status_code == 409:
                global_aliases.append(payload["custom_alias"])
                print(f"[Locust] Alias '{payload['custom_alias']}' already exists. Using anyway.")
            else:
                print(f"[Locust] Failed to create alias{i}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[Locust] Error while creating alias{i}: {e}")

    print(f"[Locust] Prepared aliases: {global_aliases}")


class UrlShortenerUser(HttpUser):
    wait_time = between(1, 3)

    @task(2)
    def redirect_to_original_url(self):
        if global_aliases:
            short_code = random.choice(global_aliases)
            with self.client.get(f"/links/{short_code}", catch_response=True) as resp:
                if resp.status_code != 200:
                    resp.failure(f"Expected 200 OK but got {resp.status_code}")

    @task(1)
    def get_link_stats(self):
        if global_aliases:
            short_code = random.choice(global_aliases)
            self.client.get(f"/links/{short_code}/stats")

