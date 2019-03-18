from app.models.model import Model


class Tweet(Model):
    def __init__(self, name: str):
        self.name = name
