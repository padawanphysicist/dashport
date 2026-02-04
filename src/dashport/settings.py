from decouple import config


class Settings():
    def __init__(self):
        self.METABASE_URL_SOURCE = config('METABASE_URL_SOURCE')
        self.METABASE_URL_TARGET = config('METABASE_URL_TARGET')
        self.METABASE_TOKEN_SOURCE = config('METABASE_TOKEN_SOURCE')
        self.METABASE_TOKEN_TARGET = config('METABASE_TOKEN_TARGET')
        self.DEBUG = config('DEBUG', default=False, cast=bool)
        self.FORMAT = "%(name)-12s: %(levelname)-8s %(message)s"
        self.REQUEST_TIMEOUT = 20

settings = Settings()
