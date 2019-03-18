class Model:
    _id = ''

    def to_json(self):
        return self.__dict__

    def from_json(self, json):
        self.__dict__ = json
