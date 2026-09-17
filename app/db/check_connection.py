from sqlalchemy import text

from app.db.database import engine


def check_database():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))

            print("PostgreSQL connection successful")
            print("Result:", result.scalar())

    except Exception as error:
        print("PostgreSQL connection failed")
        print(error)


if __name__ == "__main__":
    check_database()