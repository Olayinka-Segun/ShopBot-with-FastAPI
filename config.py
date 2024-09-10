import os

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "sdwsbbuseuwsdbciss284yyewdsey82hxadasa")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:sege%20d%20boy@localhost/product_search_db")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

settings = Settings()
