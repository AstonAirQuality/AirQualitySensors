from app.models.owner import Owner


class OwnerDAO:
    def __init__(self, connection):
        self.connection = connection

    def get_owner(self, owner_id: int) -> Owner:
        cursor = self.connection.cursor(prepared=True)
        sql = """SELECT ownerEmail FROM owners WHERE ownerId = %s"""
        cursor.execute(sql, (owner_id,))
        rs = cursor.fetchone()
        cursor.close()
        if rs is not None:
            return Owner(id=owner_id, email=rs[0])
        raise IOError("Unable to retrieve owner")

    def get_owners(self):
        cursor = self.connection.cursor()
        sql = """SELECT ownerId, ownerEmail FROM owners"""
        cursor.execute(sql)
        for rs in cursor.fetchall():
            yield Owner(id=rs[0], email=rs[1])
        cursor.close()

    def add_owner(self, owner: Owner):
        cursor = self.connection.cursor(prepared=True)
        sql = """INSERT INTO owners(ownerEmail) VALUES (%s);"""
        cursor.execute(sql, (owner.email,))
        self.connection.commit()
        cursor.close()
        if cursor.lastrowid is None:
            raise IOError("Unable to insert into database")

    def replace_owner(self, owner: Owner):
        cursor = self.connection.cursor(prepared=True)
        sql = """UPDATE owners SET ownerEmail = %s WHERE ownerId = %s"""
        cursor.execute(sql, (owner.email, owner.id))
        self.connection.commit()
        cursor.close()
        if cursor.lastrowid is None:
            raise IOError("Unable to update database")

    def delete_owner(self, owner_id: int):
        cursor = self.connection.cursor(prepared=True)
        sql = """DELETE FROM owners WHERE ownerId = %s"""
        cursor.execute(sql, (owner_id,))
        self.connection.commit()
        cursor.close()
