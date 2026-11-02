class Config:
    DB_USER = "postgres"
    DB_PASSWORD = "369gmail.com"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "gamenews"

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

API_URL = "http://192.168.1.19:8000"

config = Config()
