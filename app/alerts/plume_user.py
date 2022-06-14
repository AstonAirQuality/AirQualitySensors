import mysql.connector

from .plume_platform import PlumePlatform


class PlumeUser:
    def __init__(self, email):
        self.__connection = mysql.connector.connect(
            host="0.0.0.0",
            user="root",
            password="aston1234",
            database="main"
        )
        self.email = email
        self.__user_id = None

    def save_user(self):
        """Insert new user and any owned platforms into database"""
        cursor = self.__connection.cursor()
        sql = """INSERT INTO main.users(userEmail) VALUES (%s);"""
        cursor.execute(sql, (self.email,))
        self.__connection.commit()

    def save_owned_platform(self, serial_number):
        """Save users plume platform.
        This function may take a few seconds to execute due to request to plume backend.
        """
        platform_id = PlumePlatform(serial_number).platform_id
        cursor = self.__connection.cursor()
        sql = f"""INSERT INTO main.ownedPlatforms(platformid, userid) VALUES ({platform_id},  {self.user_id})"""
        cursor.execute(sql)
        self.__connection.commit()

    @property
    def user_id(self):
        if self.__user_id is None:
            cursor = self.__connection.cursor()
            sql = """SELECT userId FROM main.users WHERE userEmail = %s;"""
            cursor.execute(sql, (self.email,))
            self.__user_id = cursor.fetchone()[0]
        return self.__user_id
