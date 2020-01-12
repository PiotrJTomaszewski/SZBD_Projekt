import mysql.connector as db
from mysql.connector import pooling, errorcode
from pprint import pprint


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

            records = None
            if error is None:
                records = cursor.fetchall()
            cursor.close()
            connection_object.close()
            return records, error

        def execute_query_add_edit(self, query, arguments=None):
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

        # Get all
        def get_all_branches(self):
            query = """SELECT adres, nazwa FROM Oddzial ORDER BY adres"""
            records, error = self.execute_query_fetch(query)
            branches = []
            if error is None:
                for record in records:
                    branches.append({
                        'adres': record[0],
                        'nazwa': record[1]
                    })
            return branches, error

        def get_all_buildings(self):
            pass

        def get_all_offices(self):
            pass

        def get_all_depts(self):
            pass

        def get_all_workers(self):
            query = """SELECT p.pesel, p.imie, p.nazwisko, p.numer_telefonu, 
            p.czy_nadal_pracuje, p.adres_email, p.dzial_nazwa, d.skrot, d.oddzial_adres, p.biuro_numer
            FROM Pracownik p JOIN Dzial d ON p.dzial_nazwa = d.nazwa
            ORDER BY p.nazwisko, p.imie"""
            records, error = self.execute_query_fetch(query)
            workers = []
            if error is None:
                for record in records:
                    workers.append({
                        'pesel': record[0],
                        'imie': record[1],
                        'nazwisko': record[2],
                        'numer_telefonu': record[3],
                        'czy_nadal_pracuje': (lambda x: 'Tak' if x == '1' else 'Nie')(record[4]),
                        'adres_email': record[5],
                        'dzial': {'nazwa': record[6], 'skrot': record[7]},
                        'oddzial': {'adres': record[8]},
                        'biuro': {'numer': record[9]}
                    })
            return workers, error

        # def get_all_access_cards(self):
        #     pass

        def get_all_magazines(self):
            pass

        def get_all_hardware(self):
            pass

        def get_all_software(self):
            pass

        # Get specific
        def get_branch(self, address):
            query = """SELECT nazwa, adres FROM Oddzial WHERE adres = %s"""
            result, error = self.execute_query_fetch(query, [address])
            print(error)
            branch_info = None
            if not result:  # Result is empty
                error = db.Error
                error.msg = 'Nie znaleziono oddziału!'
            elif error is None:
                branch_info = {
                    'nazwa': result[0][0],
                    'adres': result[0][1]
                }
            return branch_info, error

        # Add
        def add_branch(self, address, name):
            query = """INSERT INTO Oddzial (adres, nazwa) VALUES (%s, %s)"""
            error = self.execute_query_add_edit(query, (address, name))
            if error is not None:
                print(error)
                # Translate errors to Polish
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Oddział o podanym adresie już istnieje!'
            return error

        # Edit
        def edit_branch(self, current_address, new_address, new_name):
            query = """UPDATE Oddzial SET adres=%s, nazwa=%s WHERE adres = %s"""
            error = self.execute_query_add_edit(query, (new_address, new_name, current_address))
            if error is not None:
                print(error)
                if error.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
                    error.msg = 'Nie można zmienić adresu, jeśli oddział posiada podrzędny dział, magazyn lub budynek!'
            return error
        # Delete
