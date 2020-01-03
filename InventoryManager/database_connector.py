import mysql.connector as db
from mysql.connector import pooling
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

        def execute_querry(self, querry, arguments=None):
            connection_object = self.connection_pool.get_connection()
            cursor = connection_object.cursor()
            if arguments is None:
                cursor.execute(querry)
            else:
                cursor.execute(querry, arguments)
            records = cursor.fetchall()
            cursor.close()
            connection_object.close()
            return records

        def get_all_branches(self):
            querry = """SELECT adres, nazwa FROM Oddzial ORDER BY adres"""
            records = self.execute_querry(querry)
            branches = []
            for record in records:
                branches.append({
                    'adres': record[0],
                    'nazwa': record[1]
                })
            return branches

        def get_all_buildings(self):
            pass

        def get_all_offices(self):
            pass

        def get_all_depts(self):
            pass

        def get_all_workers(self):
            querry = """SELECT p.pesel, p.imie, p.nazwisko, p.numer_telefonu, 
            p.czy_nadal_pracuje, p.adres_email, p.dzial_nazwa, d.skrot, d.oddzial_adres, p.biuro_numer
            FROM Pracownik p JOIN Dzial d ON p.dzial_nazwa = d.nazwa
            ORDER BY p.nazwisko, p.imie;"""
            records = self.execute_querry(querry)
            workers = []
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
            return workers

        # def get_all_access_cards(self):
        #     pass

        def get_all_magazines(self):
            pass

        def get_all_hardware(self):
            pass

        def get_all_software(self):
            pass
