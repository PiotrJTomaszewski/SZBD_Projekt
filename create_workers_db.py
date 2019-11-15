# Tworzenie testowej bazy pracowników
import mysql.connector as db
conn_args = {'host': 'localhost', 'database': 'db_projekt', 'user': 'db_projekt', 'password': 'db_projekt'}
with open('FakeNameGenerator.com_43849084.csv', 'r') as data:
    conn = db.connect(**conn_args)
    cursor = conn.cursor()
    try:
        cursor.execute('DROP TABLE WORKERS')
    except db.Error as error:
        print(error)
    try:
        cursor.execute("""CREATE TABLE WORKERS(
      WORK_ID INTEGER PRIMARY KEY,
      FIRST_NAME VARCHAR(30),
      LAST_NAME VARCHAR(30),
      GENDER VARCHAR(1),
      EMAIL VARCHAR(50),
      PESEL VARCHAR(11),
      BIRTHDAY DATE,
      TEL_NUMBER VARCHAR(9)
    )""")
    except db.Error as error:
        print(error)
    # First line is not important
    data.readline()
    for line in data:
        line_splitted = line.split(',')
        work_id = line_splitted[0]
        name = line_splitted[2]
        if name[0] == '"':
            name = name[1:-1]
        if name[-1] == ' ':
            name = name[:-1]
        surname = line_splitted[3]
        if surname[0] == '"':
            surname = surname[1:-1]
        if surname[-1] == ' ':
            surname = surname[:-1]
        pesel = line_splitted[5]
        # Change email to Polish one
        tmp = line_splitted[4].split('.')
        email = ".".join([tmp[0], 'pl'])
        # Gender
        if line_splitted[1] == 'female':
            gender = 'F'
        else:
            gender = 'M'
        # Birthday
        tmp = line_splitted[6].split('/')
        bday = "-".join([tmp[2], tmp[0], tmp[1]])
        # Fix phone number
        tel = "".join(line_splitted[-1][:-1].split(" "))[1:-1]  # Remove spaces and quotation marks
        # Values to insert
        values = (work_id, name, surname, gender, email, pesel, bday, tel)
        cursor.execute("""INSERT INTO WORKERS(WORK_ID, FIRST_NAME, LAST_NAME, GENDER, EMAIL, PESEL, BIRTHDAY, TEL_NUMBER)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s)""", values)
    conn.commit()
    conn.close()
