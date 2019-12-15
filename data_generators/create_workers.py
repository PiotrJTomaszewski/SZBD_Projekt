# Create test workers data
import random as rng


# Nie wiem, która wersja się przyda, więc wrzucam obie.
# Można utworzyć listę do 10000 pracowników

# Generuje listę pracowników
# Każdy pracownik reprezentowany jest przez osobny słownik
def gen_workers_dict(how_many):
    if how_many > 10000:
        how_many = 10000
    values = []
    with open('FakeNameGenerator.com_43849084.csv', 'r') as data:
        data.readline()
        for i, line in enumerate(data):
            if i >= how_many:
                break
            line_splitted = line.split(',')
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
            # Fix phone number
            tel = "".join(line_splitted[-1][:-1].split(" "))[1:-1]  # Remove spaces and quotation marks
            is_still_working = str(int(rng.randint(0, 100) < 90))
            values.append({"pesel": pesel, "imie": name, "nazwisko": surname, "numer_telefonu": tel,
                           "czy_nadal_pracuje": is_still_working, "adres_email": email})

    return values


# Generuje listę pracowników
# Każdy pracownik reprezentowany jest przez listę pól
def gen_workers_list(how_many):
    if how_many > 10000:
        how_many = 10000
    values = []
    with open('FakeNameGenerator.com_43849084.csv', 'r') as data:
        data.readline()
        for i, line in enumerate(data):
            if i >= how_many:
                break
            line_splitted = line.split(',')
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
            # Fix phone number
            tel = "".join(line_splitted[-1][:-1].split(" "))[1:-1]  # Remove spaces and quotation marks
            is_still_working = str(int(rng.randint(0, 100) < 90))
            values.append([pesel, name, surname, tel, is_still_working, email])

    return values


if __name__ == "__main__":
    print(gen_workers_dict(100))
    print(gen_workers_list(100))