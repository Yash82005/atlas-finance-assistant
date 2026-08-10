import sqlite3

from app.config.settings import settings

database_url = settings.DATABASE_URL

if not database_url.startswith("sqlite:///"):
    raise Exception("This script is intended for SQLite.")

db_path = database_url.replace(
    "sqlite:///",
    "",
    1
)

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

try:
    cursor.execute(
        """
        ALTER TABLE users
        ADD COLUMN last_alerts VARCHAR
        """
    )

    connection.commit()

    print("✅ last_alerts column added successfully.")

except sqlite3.OperationalError as e:

    if "duplicate column name" in str(e).lower():
        print("ℹ️ last_alerts already exists.")
    else:
        raise

finally:
    connection.close()