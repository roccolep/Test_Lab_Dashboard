from locust import HttpUser, between, task


class DashboardUser(HttpUser):
    wait_time = between(0.5, 2)

    @task(3)
    def view_home(self):
        self.client.get("/")

    @task(1)
    def create_command(self):
        self.client.post(
            "/api/commands/",
            json={"name": "move", "payload": {"unit": "A1"}, "priority": 1},
        )