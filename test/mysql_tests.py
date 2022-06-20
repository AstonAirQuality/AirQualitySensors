import os

from app.alerts.plume_platform import PlumePlatform
from app.alerts.plume_user import PlumeUser

os.environ["PLUME_EMAIL"] = "180086320@aston.ac.uk"
os.environ["PLUME_PASSWORD"] = "aston1234"


def data_insert():
    PlumePlatform("02:00:00:00:4b:e4", email="020000004be4@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:4b:f2", email="020000004bf2@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:4b:df", email="020000004bdf@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:4b:9c", email="020000004b9c@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:49:ed", email="0200000049ed@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:4b:9e", email="020000004b9e@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:4b:cf", email="020000004bcf@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:4b:8b", email="020000004b8b@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:49:2e", email="02000000492e@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:4b:ed", email="020000004bed@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:4b:ba", email="020000004bba@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:4b:aa", email="020000004baa@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:48:a4", email="0200000048a4@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:4b:c5", email="020000004bc5@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:48:ec", email="0200000048ec@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:4b:7d", email="020000004b7d@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:49:3a", email="02000000493a@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:4b:d1", email="020000004bd1@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:4b:5e", email="020000004b5e@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:48:f7", email="0200000048f7@sensor.project", password="aston1234").save()
    PlumePlatform("02:00:00:00:48:13", email="l.bastin@aston.ac.uk", password="").save()

    asad = PlumeUser("Asad@sensor.project")
    asad.save_user()
    mathew = PlumeUser("Mathew@sensor.project")
    mathew.save_user()
    georgia = PlumeUser("Georgia@sensor.project")
    georgia.save_user()
    lucy = PlumeUser("Lucy@sensor.project")
    lucy.save_user()

    asad.save_owned_platform("02:00:00:00:4b:e4")
    asad.save_owned_platform("02:00:00:00:4b:f2")
    asad.save_owned_platform("02:00:00:00:4b:8b")
    asad.save_owned_platform("02:00:00:00:4b:ed")
    asad.save_owned_platform("02:00:00:00:48:a4")
    asad.save_owned_platform("02:00:00:00:49:3a")
    asad.save_owned_platform("02:00:00:00:4b:5e")

    mathew.save_owned_platform("02:00:00:00:4b:9c")
    mathew.save_owned_platform("02:00:00:00:49:ed")
    mathew.save_owned_platform("02:00:00:00:4b:9e")
    mathew.save_owned_platform("02:00:00:00:49:2e")
    mathew.save_owned_platform("02:00:00:00:4b:aa")
    mathew.save_owned_platform("02:00:00:00:48:ec")

    georgia.save_owned_platform("02:00:00:00:4b:df")
    georgia.save_owned_platform("02:00:00:00:4b:cf")
    georgia.save_owned_platform("02:00:00:00:4b:ba")
    georgia.save_owned_platform("02:00:00:00:4b:c5")
    georgia.save_owned_platform("02:00:00:00:4b:7d")
    georgia.save_owned_platform("02:00:00:00:4b:d1")

    lucy.save_owned_platform("02:00:00:00:48:13")


def test_user_insert():
    PlumeUser("test.user@sensor.project").save_user()


def test_platform_junction_insert():
    PlumeUser("test@test.com").save_owned_platform("020000004358")


def test_platform_insert():
    PlumePlatform("020000004358", email="plume1@test.com", password="aston1234").save()


def test_get_saved_platforms():
    for p in PlumePlatform.get_platforms():
        print(p)


def test_owned_platforms():
    for p in PlumeUser("Asad@sensor.project").owned_platforms:
        print(p)


if __name__ == '__main__':
    test_owned_platforms()
