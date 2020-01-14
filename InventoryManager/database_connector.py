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

        # # Get all
        # def get_all_branches(self, get_all_data=True):
        #     if get_all_data:  # Get all of the fields
        #         query = """SELECT adres, nazwa FROM Oddzial ORDER BY adres"""
        #
        #     else:  # Get only basic data
        #         query = """SELECT adres FROM Oddzial ORDER BY adres"""
        #     records, error = self.execute_query_fetch(query)
        #     branches = []
        #     if error is None:
        #         if get_all_data:
        #             for record in records:
        #                 branches.append({
        #                     'adres': record[0],
        #                     'nazwa': record[1]
        #                 })
        #         else:
        #             for record in records:
        #                 branches.append({'adres': record[0]})
        #     return branches, error
        #
        # def get_all_buildings(self, get_all_data=True):
        #     if get_all_data:  # Get all of the fields
        #         query = """SELECT adres, nazwa, ilosc_pieter, oddzial_adres FROM Budynek ORDER BY adres"""
        #
        #     else:  # Get only basic data
        #         query = """SELECT adres FROM Oddzial ORDER BY adres"""
        #     records, error = self.execute_query_fetch(query)
        #     buildings = []
        #     if error is None:
        #         if get_all_data:
        #             for record in records:
        #                 buildings.append({
        #                     'adres': record[0],
        #                     'nazwa': record[1],
        #                     'liczba_pieter': record[2],
        #                     'oddzial': {'adres': record[3]}
        #                 })
        #         else:
        #             for record in records:
        #                 buildings.append({
        #                     'adres': record[0],
        #                     'nazwa': record[1]
        #                 })
        #     return buildings, error
        #
        # def get_all_offices(self, get_all_data=True):
        #     if get_all_data:  # Get all of the fields
        #         query = """SELECT numer, liczba_stanowisk, pietro, budynek_adres FROM Biuro ORDER BY numer"""
        #
        #     else:  # Get only basic data
        #         query = """SELECT numer, budynek_adres FROM Biuro ORDER BY numer"""
        #     records, error = self.execute_query_fetch(query)
        #     offices = []
        #     if error is None:
        #         if get_all_data:
        #             for record in records:
        #                 offices.append({
        #                     'numer': record[0],
        #                     'liczba_stanowisk': record[1],
        #                     'pietro': record[2],
        #                     'budynek': {'adres': record[3]}
        #                 })
        #         else:
        #             for record in records:
        #                 offices.append({
        #                     'numer': record[0],
        #                     'budynek': {'adres': record[1]}
        #                 })
        #     return offices, error
        #
        # def get_all_depts(self, get_all_data=True):
        #     if get_all_data:  # Get all of the fields
        #         query = """SELECT nazwa, skrot, oddzial_adres FROM Dzial ORDER BY nazwa"""
        #
        #     else:  # Get only basic data
        #         query = """SELECT nazwa, skrot FROM Dzial ORDER BY nazwa"""
        #     records, error = self.execute_query_fetch(query)
        #     depts = []
        #     if error is None:
        #         if get_all_data:
        #             for record in records:
        #                 depts.append({
        #                     'nazwa': record[0],
        #                     'skrot': record[1],
        #                     'oddzial': {'adres': record[2]}
        #                 })
        #         else:
        #             for record in records:
        #                 depts.append({
        #                     'nazwa': record[0],
        #                     'skrot': record[1]
        #                 })
        #     return depts, error
        #
        # def get_all_workers(self, get_all_data=True):
        #     if get_all_data:  # Get all of the fields
        #         query = """SELECT p.pesel, p.imie, p.nazwisko, p.numer_telefonu,
        #         p.czy_nadal_pracuje, p.adres_email, p.dzial_nazwa, d.skrot, d.oddzial_adres, p.biuro_numer
        #         FROM Pracownik p JOIN Dzial d ON p.dzial_nazwa = d.nazwa
        #         ORDER BY p.nazwisko, p.imie"""
        #     else:  # Get only basic data
        #         query = """SELECT pesel, imie, nazwisko FROM Pracownik ORDER BY nazwisko, imie"""
        #     records, error = self.execute_query_fetch(query)
        #     workers = []
        #     if error is None:
        #         if get_all_data:
        #             for record in records:
        #                 workers.append({
        #                     'pesel': record[0],
        #                     'imie': record[1],
        #                     'nazwisko': record[2],
        #                     'numer_telefonu': record[3],
        #                     'czy_nadal_pracuje': (lambda x: 'Tak' if x == '1' else 'Nie')(record[4]),
        #                     'adres_email': record[5],
        #                     'dzial': {'nazwa': record[6], 'skrot': record[7]},
        #                     'oddzial': {'adres': record[8]},
        #                     'biuro': {'numer': record[9]}
        #                 })
        #             else:
        #                 for record in records:
        #                     workers.append({
        #                         'pesel': record[0],
        #                         'imie': record[1],
        #                         'nazwisko': record[2]
        #                     })
        #     return workers, error
        #
        # # def get_all_access_cards(self):
        # #     pass
        #
        # def get_all_magazines(self, get_all_data=True):
        #     if get_all_data:  # Get all of the fields
        #         query = """SELECT numer, pojemnosc, oddzial_adres, WolnaPojemnoscMagazynu(numer) FROM Magazyn ORDER BY numer"""
        #
        #     else:  # Get only basic data
        #         query = """SELECT numer, oddzial_adres FROM Magazyn ORDER BY numer"""
        #     records, error = self.execute_query_fetch(query)
        #     magazines = []
        #     if error is None:
        #         if get_all_data:
        #             for record in records:
        #                 magazines.append({
        #                     'numer': record[0],
        #                     'pojemnosc': record[1],
        #                     'oddzial': {'adres': record[2]},
        #                     'wolne_miejsce': record[3]
        #                 })
        #         else:
        #             for record in records:
        #                 magazines.append({
        #                     'numer': record[0],
        #                     'oddzial': {'adres': record[1]},
        #                 })
        #     return magazines, error
        #
        # def get_all_nonfull_magazines(self, get_all_data=True):
        #     if get_all_data:  # Get all of the fields
        #         query = """SELECT numer, pojemnosc, oddzial_adres, WolnaPojemnoscMagazynu(numer)
        #         FROM Magazyn
        #         WHERE WolnaPojemnoscMagazynu > 0
        #         ORDER BY numer"""
        #
        #     else:  # Get only basic data
        #         query = """SELECT numer, oddzial_adres FROM Magazyn
        #          WHERE WolnaPojemnoscMagazynu > 0
        #          ORDER BY numer"""
        #     records, error = self.execute_query_fetch(query)
        #     magazines = []
        #     if error is None:
        #         if get_all_data:
        #             for record in records:
        #                 magazines.append({
        #                     'numer': record[0],
        #                     'pojemnosc': record[1],
        #                     'oddzial': {'adres': record[2]},
        #                     'wolne_miejsce': record[3]
        #                 })
        #         else:
        #             for record in records:
        #                 magazines.append({
        #                     'numer': record[0],
        #                     'oddzial': {'adres': record[1]},
        #                 })
        #     return magazines, error
        #
        # def get_all_hardware(self, get_all_data=True):
        #     pass
        #
        # def get_all_software(self):
        #     pass
        #
        # # Get specific
        # def get_branch(self, address):
        #     query = """SELECT nazwa, adres FROM Oddzial WHERE adres = %s"""
        #     result, error = self.execute_query_fetch(query, [address])
        #     branch_info = None
        #     if not result:  # Result is empty
        #         error = db.Error
        #         error.msg = 'Nie znaleziono oddziału!'
        #     elif error is None:
        #         branch_info = {
        #             'nazwa': result[0][0],
        #             'adres': result[0][1]
        #         }
        #     return branch_info, error
        #
        # def get_building(self, address):
        #     query = """SELECT adres, nazwa, ilosc_pieter, oddzial_adres FROM Budynek WHERE adres = %s"""
        #     result, error = self.execute_query_fetch(query, [address])
        #     building_info = None
        #     if not result:  # Result is empty
        #         error = db.Error
        #         error.msg = 'Nie znaleziono budynku!'
        #     elif error is None:
        #         building_info = {
        #             'adres': result[0],
        #             'nazwa': result[1],
        #             'liczba_pieter': result[2],
        #             'oddzial': {'adres': result[3]}
        #         }
        #     return building_info, error
        #
        # # Add
        # def add_branch(self, address, name):
        #     query = """INSERT INTO Oddzial (adres, nazwa) VALUES (%s, %s)"""
        #     error = self.execute_query_add_edit_delete(query, (address, name))
        #     if error is not None:
        #         print(error)
        #         # Translate errors to Polish
        #         if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
        #             error.msg = 'Oddział o podanym adresie już istnieje!'
        #     return error
        #
        # def add_building(self, address, name, number_of_floors, branch_address):
        #     query = """INSERT INTO Budynek (adres, nazwa, ilosc_pieter, oddzial_adres)
        #         VALUES (%s, %s, %s, %s)"""
        #     error = self.execute_query_add_edit_delete(query, (address, name, number_of_floors, branch_address))
        #     if error is not None:
        #         print(error)
        #         # Translate errors to Polish
        #         if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
        #             error.msg = 'Budynek o podanym adresie już istnieje!'
        #     return error
        #
        # # Edit
        # def edit_branch(self, current_address, new_address, new_name):
        #     query = """UPDATE Oddzial SET adres=%s, nazwa=%s WHERE adres = %s"""
        #     error = self.execute_query_add_edit_delete(query, (new_address, new_name, current_address))
        #     if error is not None:
        #         print(error)
        #         if error.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
        #             error.msg = 'Nie można zmienić adresu, jeśli oddział posiada podrzędny dział, magazyn lub budynek!'
        #     return error
        #
        # # Delete
        # def delete_branch(self, address):
        #     query = """DELETE FROM Oddzial WHERE adres = %s"""
        #     error = self.execute_query_add_edit_delete(query, [address])
        #     if error is not None:
        #         print(error)
        #     return error
