import json
import os

class Storage(object):
    '''
    use this snippet when getting your current file path! Python is stupid

    str(os.path.dirname(os.path.abspath(__file__)))
    '''
    def __init__(self, path: str) -> None:
        self.path = path

    def write(self, filename: str, data: dict) -> None:
        path = self.path + "\\" + filename
        with open(path, "w") as file:
            json.dump(data, file, indent=4)

    def read(self, filename: str) -> dict:
        path = self.path + "\\" + filename
        with open(path, "r") as file:
            data = json.load(file)
        return data

    def edit(self, filename: str, key: str, value) -> None:
        path = self.path + "\\" + filename
        with open(path, "r") as file:
            data = json.load(file)
        if key in data:
            data[key] = value
        with open(path, "w") as file:
            json.dump(data, file, indent=4)

    def subEdit(self, filename: str, key: str, subKey: str, value) -> None:
        path = self.path + "\\" + filename
        with open(path, "r") as file:
            data = json.load(file)
        if key in data:
            data[key][subKey] = value
        with open(path, "w") as file:
            json.dump(data, file, indent=4)

    def delete(self, filename: str, key):
        path = self.path + "\\" + filename
        with open(path, "r") as file:
            data = json.load(file)
        if key in data:
            del data[key]
        with open(path, "w") as file:
            json.dump(data, file, indent=4)

    def subDelete(self, filename: str, key, subKey):
        path = self.path + "\\" + filename
        with open(path, "r") as file:
            data = json.load(file)
        if key in data:
            if subKey in data[key]:
                del data[key][subKey]
        with open(path, "w") as file:
            json.dump(data, file, indent=4)