from mysql.connector.pooling import MySQLConnectionPool

from app.daos.base_dao import BaseDAO
from app.models.owner import Owner


class OwnerDAO(BaseDAO):
    def __init__(self, cnx_pool: MySQLConnectionPool):
        super().__init__(cnx_pool)

    def get_owner(self, owner_id: int) -> Owner:
        with self.connection as connection:
            with connection.cursor(prepared=True) as cursor:
                sql = """SELECT ownerEmail FROM owners WHERE ownerId = %s"""
                cursor.execute(sql, (owner_id,))
                rs = cursor.fetchone()
        if rs is not None:
            return Owner(id=owner_id, email=rs[0])
        raise IOError("Unable to retrieve owner")

    def get_owners(self):
        with self.connection as connection:
            with connection.cursor() as cursor:
                sql = """SELECT ownerId, ownerEmail FROM owners"""
                cursor.execute(sql)
                res_set = cursor.fetchall()

        for rs in res_set:
            yield Owner(id=rs[0], email=rs[1])

    def add_owner(self, owner: Owner):
        with self.connection as connection:
            with connection.cursor(prepared=True) as cursor:
                sql = """INSERT INTO owners(ownerEmail) VALUES (%s);"""
                cursor.execute(sql, (owner.email,))
                connection.commit()

        if cursor.lastrowid is None:
            raise IOError("Unable to insert into database")

    def replace_owner(self, owner: Owner):
        with self.connection as connection:
            with connection.cursor(prepared=True) as cursor:
                sql = """UPDATE owners SET ownerEmail = %s WHERE ownerId = %s"""
                cursor.execute(sql, (owner.email, owner.id))
                connection.commit()

        if cursor.lastrowid is None:
            raise IOError("Unable to update database")

    def delete_owner(self, owner_id: int):
        with self.connection as connection:
            with connection.cursor(prepared=True) as cursor:
                sql = """DELETE FROM owners WHERE ownerId = %s"""
                cursor.execute(sql, (owner_id,))
                connection.commit()
