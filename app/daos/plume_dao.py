from typing import List

from app.models.plume_platform import PlumePlatform


class PlumeDAO:
    def __init__(self, connection):
        self.connection = connection

    def get_platforms(self) -> List[PlumePlatform]:
        cursor = self.connection.cursor()
        sql = """SELECT s.sensorId, s.sensorName, p.serialNumber, p.email, p.password, o.ownerEmail
        FROM main.plumePlatforms p
         JOIN sensors s on s.sensorId = p.sensorId
         LEFT JOIN ownedSensors oS on s.sensorId = oS.sensorId
         LEFT JOIN owners o on o.ownerId = oS.ownerId"""

        cursor.execute(sql)
        for rs in cursor.fetchall():
            yield PlumePlatform(id=rs[0], name=rs[1], serial_number=rs[2], email=rs[3], password=rs[4],
                                owner_email=rs[5])
        cursor.close()

    def add_platform(self, platform: PlumePlatform):
        cursor = self.connection.cursor(prepared=True)
        sql = """INSERT INTO sensors(sensorName) VALUES (%s);"""
        cursor.execute(sql, (platform.name,))
        self.connection.commit()

        sensor_id = cursor.lastrowid
        if sensor_id is None:
            raise IOError("Unable to insert into database")

        cursor = self.connection.cursor(prepared=True)
        sql = """ INSERT INTO plumePlatforms(sensorId, serialNumber, email, password)
                VALUES (%s, %s, %s, %s);"""
        cursor.execute(sql, (sensor_id, platform.serial_number, platform.email, platform.password))

        if platform.owner_id != -1:
            sql = """INSERT INTO ownedSensors(sensorid, ownerId) VALUES (%s, %s);"""
            cursor.execute(sql, (sensor_id, platform.owner_id))

        self.connection.commit()
        cursor.close()
