import mysql.connector

from app.api_wrappers.plume_wrapper import PlumeWrapper


class PlumePlatform:
    _connection = mysql.connector.connect(
        host="0.0.0.0",
        user="root",
        password="aston1234",
        database="main"
    )

    def __init__(self, serial_number, email=None, password=None, _id=None, internal_id=None):

        self.__id = _id
        self.__internal_platform_id = internal_id  # refers to the ID assigned by plume

        self.serial_number = serial_number
        self.email = email
        self.password = password

    def save(self):
        # will raise a ProgrammingError on duplicate insertions
        con = self._connection
        cursor = con.cursor(prepared=True)
        sql = """INSERT INTO main.plumePlatforms(plumeInternalPlatformId, plumePlatformSerialNumber, plumePlatformEmail, plumePlatformPassword) VALUES (%s, %s, %s, %s);"""
        cursor.execute(sql, (self.plume_internal_platform_id, self.serial_number, self.email, self.password))
        con.commit()
        self.__id = cursor.lastrowid
        cursor.close()

    @property
    def plume_internal_platform_id(self):
        # only access api if sensor is not saved in a database
        if self.__internal_platform_id is None:
            cursor = self._connection.cursor(prepared=True)
            sql = """SELECT plumeInternalPlatformId FROM main.plumePlatforms WHERE plumePlatformSerialNumber = %s"""
            cursor.execute(sql, (self.serial_number,))
            result = cursor.fetchone()
            if result is None:
                self.__internal_platform_id = next(
                    PlumeWrapper.env_factory().convert_serial_number_to_platform_id((self.serial_number,)))
            else:
                self.__internal_platform_id = result
            cursor.close()
        return self.__internal_platform_id

    @property
    def platform_id(self):
        if self.__id is None:
            cursor = self._connection.cursor()
            sql = """SELECT platformId FROM main.plumePlatforms WHERE plumePlatformSerialNumber = %s"""
            cursor.execute(sql, (self.serial_number,))
            result = cursor.fetchone()[0]
            if result is None:
                # meaning id has not been created
                self.__id = -1
            self.__id = result
            cursor.close()
        return self.__id

    def __repr__(self):
        return f"ID: {self.__id}, SERIAL_NUMBER: {self.serial_number}"

    @staticmethod
    def get_platforms():
        cursor = PlumePlatform._connection.cursor()
        sql = """SELECT platformId, plumeInternalPlatformId, plumePlatformSerialNumber, plumePlatformEmail, plumePlatformPassword FROM main.plumePlatforms"""
        cursor.execute(sql)
        for rs in cursor.fetchall():
            yield PlumePlatform(rs[2], email=rs[3], password=rs[4], _id=rs[0], internal_id=rs[1])
        cursor.close()
