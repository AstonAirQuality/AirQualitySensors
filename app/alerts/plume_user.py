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
        cursor.close()

    def save_owned_platform(self, serial_number):
        """Save users plume platform.
        This function may take a few seconds to execute due to request to plume backend.

        TODO: better error handling when saving invalid platforms
        """
        platform_id = PlumePlatform(serial_number).platform_id
        cursor = self.__connection.cursor(prepared=True)
        sql = f"""INSERT INTO main.ownedPlatforms(platformId, userId) VALUES (%s, %s)"""
        print(platform_id)
        print(self.user_id)
        cursor.execute(sql, (platform_id, self.user_id))
        self.__connection.commit()
        cursor.close()

    @property
    def user_id(self):
        if self.__user_id is None:
            cursor = self.__connection.cursor()
            sql = """SELECT userId FROM main.users WHERE userEmail = %s;"""
            cursor.execute(sql, (self.email,))
            self.__user_id = cursor.fetchone()[0]
            cursor.close()
        return self.__user_id

    @property
    def owned_platforms(self):
        cursor = self.__connection.cursor(prepared=True)
        sql = """SELECT plumePlatforms.platformId, plumeInternalPlatformId, plumePlatformSerialNumber, plumePlatformEmail, plumePlatformPassword FROM main.plumePlatforms
        JOIN main.ownedPlatforms oP on plumePlatforms.platformId = oP.platformId AND oP.userId = %s """
        cursor.execute(sql, (self.user_id,))
        for rs in cursor.fetchall():
            yield PlumePlatform(rs[2], email=rs[3], password=rs[4], _id=rs[0], internal_id=rs[1])
        cursor.close()
