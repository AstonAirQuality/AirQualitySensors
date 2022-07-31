from mysql.connector.pooling import MySQLConnectionPool, PooledMySQLConnection


class BaseDAO:
    def __init__(self, cnx_pool: MySQLConnectionPool):
        self.__cnx_pool = cnx_pool

    @property
    def connection(self) -> PooledMySQLConnection:
        return self.__cnx_pool.get_connection()
