import os

from locust import HttpUser, between, task


class FleetManagementUser(HttpUser):
    username: str
    password: str
    token: str | None = None

    wait_time = between(1, 3)

    def on_start(self):
        self.username = os.getenv("LOCUST_USERNAME", "loadtest_user")
        self.password = os.getenv("LOCUST_PASSWORD", "")

        response = self.client.post(
            "/auth/login",
            json={
                "username": self.username,
                "password": self.password,
            },
            name="/auth/login",
        )

        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            self.token = None
            response.failure(f"Login failed: HTTP {response.status_code}")

    @task(3)
    def view_home(self):
        self.client.get("/", name="/")

    @task(2)
    def view_vehicles(self):
        if self.token:
            self.client.get("/vehicles", name="/vehicles")
