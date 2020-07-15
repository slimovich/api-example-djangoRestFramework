import csv
import os

from src.api.models.towns import Towns


DATA_FILE = "src/data/French_Towns_Data.csv"


def create_towns():
    with open(DATA_FILE, errors='ignore') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=',')
        for row in spamreader:
            print(row)

            Towns.objects.update_or_create(region_code=row['region_code'], region_name=row['region_name'], 
                                            dept_code=row['dept_code'], distr_code=row['distr_code'], 
                                            code=row['code'], name=row['name'], 
                                            population=row['population'], average_age=row['average_age'])