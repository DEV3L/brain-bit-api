import csv

from app.daos.env import env

DEFAULT_SCHOOL_FILE = env("SCHOOL_FILE", default="./data/school-DEV3L.csv")


def load_csv(path: str = DEFAULT_SCHOOL_FILE) -> []:
    return _read_csv_file(path)


def _read_csv_file(file_path: str) -> []:
    with open(file_path, mode="r", encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        _file_contents = [row for row in csv_reader]
        for row in _file_contents:
            for key, value in row.items():
                row[key] = value.strip()
        return _file_contents
