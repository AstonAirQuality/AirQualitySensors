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
        LEFT JOIN owners o on o.ownerId = s.ownerId"""

        cursor.execute(sql)
        for rs in cursor.fetchall():
            yield PlumePlatform(id=rs[0], name=rs[1], serial_number=rs[2], email=rs[3], password=rs[4],
                                owner_email=rs[5])
        cursor.close()

    def get_platform(self, platform_id: int):
        cursor = self.connection.cursor(prepared=True)
        sql = """SELECT s.sensorId, s.sensorName, p.serialNumber, p.email, p.password, o.ownerEmail, s.ownerId
        FROM main.plumePlatforms p
        JOIN sensors s on s.sensorId = p.sensorId
        LEFT JOIN owners o on o.ownerId = s.ownerId
        WHERE p.sensorId = %s"""
        cursor.execute(sql, (platform_id,))
        rs = cursor.fetchone()
        cursor.close()
        if rs is not None:
            return PlumePlatform(id=rs[0], name=rs[1], serial_number=rs[2], email=rs[3], password=rs[4],
                                 owner_email=rs[5], owner_id=rs[6])
        raise IOError("Unable to retrieve platform")

    def add_platform(self, platform: PlumePlatform):
        cursor = self.connection.cursor(prepared=True)
        if platform.owner_id == -1:
            sql = """INSERT INTO sensors(sensorName) VALUES (%s);"""
            cursor.execute(sql, (platform.name,))
        else:
            sql = """INSERT INTO sensors(sensorName, ownerId) VALUES (%s, %s);"""
            cursor.execute(sql, (platform.name, platform.owner_id))
        self.connection.commit()

        sensor_id = cursor.lastrowid

        if not sensor_id:
            raise IOError("Unable to insert into database")

        cursor = self.connection.cursor(prepared=True)
        sql = """ INSERT INTO plumePlatforms(sensorId, serialNumber, email, password)
                VALUES (%s, %s, %s, %s);"""
        cursor.execute(sql, (sensor_id, platform.serial_number, platform.email, platform.password))

        self.connection.commit()
        cursor.close()

    def update_platform(self, platform: PlumePlatform):
        cursor = self.connection.cursor(prepared=True)
        sql = """UPDATE plumePlatforms SET email = %s, password = %s, serialNumber = %s WHERE sensorId = %s"""
        cursor.execute(sql, (platform.email, platform.password, platform.serial_number, platform.id))
        self.connection.commit()

        sql = """UPDATE sensors SET sensorName = %s WHERE sensorId = %s"""
        cursor.execute(sql, (platform.name, platform.id))
        self.connection.commit()

        sql = """UPDATE sensors SET ownerId = %s WHERE sensorId = %s"""
        if platform.owner_id == -1:
            cursor.execute(sql, (None, platform.id))
        else:
            cursor.execute(sql, (platform.owner_id, platform.id))
        self.connection.commit()
