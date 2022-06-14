import os

from app.alerts.plume_user import PlumeUser

os.environ["PLUME_EMAIL"] = "180086320@aston.ac.uk"
os.environ["PLUME_PASSWORD"] = "aston1234"


def test_platform_insert():
    PlumeUser("test@test.com").save_owned_platform("020000004358")


if __name__ == '__main__':
    test_platform_insert()
