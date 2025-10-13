import os


class ConfigManager:
    def __init__(self):
        self.env = dict(os.environ)

    def get(self, key, default=None):
        return self.env.get(key, default)

