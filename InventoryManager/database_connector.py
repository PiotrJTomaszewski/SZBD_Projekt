import mysql.connector as db
from mysql.connector import pooling, errorcode


class DatabaseConnector:
    # A singleton used to connect to the database
    instance = None

    def __init__(self):
        if not DatabaseConnector.instance:
            print('Creating new connection instance')
            DatabaseConnector.instance = DatabaseConnector.__DatabaseConnectorSingleton()
        else:
            print('Using existing connection instance')

    def get_instance(self):
        return DatabaseConnector.instance

    class __DatabaseConnectorSingleton:
        def __init__(self):
            conn_args = {'host': 'localhost', 'database': 'sbdbazadanych', 'user': 'db_projekt',
                         'password': 'db_projekt'}
            self.connection_pool = db.pooling.MySQLConnectionPool(
                pool_size=5,
                pool_reset_session=True,
                **conn_args
            )
            print('Database connected')

        def execute_query_fetch(self, query, arguments=None):
            """
            Executes query and then fetches the result
            :param query:
            :param arguments:
            :return:
            """
            error = None
            connection_object = self.connection_pool.get_connection()
            cursor = connection_object.cursor()
            try:
                if arguments is None:
                    cursor.execute(query)
                else:
                    cursor.execute(query, arguments)
            except db.Error as err:
                error = err

            records = []
            if error is None:
                records = cursor.fetchall()
            cursor.close()
            connection_object.close()
            return records, error

        def execute_query_add_edit_delete(self, query, arguments=None):
            error = None
            connection_object = self.connection_pool.get_connection()
            cursor = connection_object.cursor()
            try:
                if arguments is None:
                    cursor.execute(query)
                else:
                    cursor.execute(query, arguments)
                connection_object.commit()
            except db.Error as err:
                error = err
            cursor.close()
            connection_object.close()
            return error

        def execute_query_add_edit_delete_with_fetch(self, query, arguments=None):
            error = None
            connection_object = self.connection_pool.get_connection()
            cursor = connection_object.cursor()
            try:
                if arguments is None:
                    cursor.execute(query)
                else:
                    cursor.execute(query, arguments)
            except db.Error as err:
                error = err

            records = []
            if error is None:
                records = cursor.fetchall()
                connection_object.commit()
            cursor.close()
            connection_object.close()
            return records, error

        def execute_query_add_edit_delete_with_fetch_last_id(self, query, arguments=None):
            error = None
            connection_object = self.connection_pool.get_connection()
            cursor = connection_object.cursor()
            try:
                if arguments is None:
                    cursor.execute(query)
                else:
                    cursor.execute(query, arguments)

                cursor.execute("""SELECT LAST_INSERT_ID();""")
            except db.Error as err:
                error = err

            records = []
            if error is None:
                records = cursor.fetchall()
                connection_object.commit()
            cursor.close()
            connection_object.close()
            return records, error
