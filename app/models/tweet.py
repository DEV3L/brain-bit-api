class Tweet:
    def __init__(self, name: str):
        self.name = name

    def to_json(self):
        json = {
            'name': self.name
        }

        return json

    def from_json(self, json: dict):
        self.name = json['name']

        return json
