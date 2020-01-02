import mysql.connector as db
from mysql.connector import pooling

class DatabaseConnector:
    def __init__(self, host, database, user, password):
        self.connection_pool = db.pooling.MySQLConnectionPool(
            pool_size=5,
            pool_reset_session=True,
            host=host,
            database=database,
            user=user,
            password=password
        )

    def get_workers(self):
        connection_object = self.connection_pool.get_connection()
        print(connection_object.is_connected())

    # def read_from_database(what):
    #     conn = db.connect(**conn_args)
    #     cursor = conn.cursor()
    #     cursor.execute('SELECT * FROM ' + what)
    #     cols = [i[0].upper() for i in cursor.description]
    #     rows = cursor.fetchall()
    #     conn.close()
    #     return cols, rows
