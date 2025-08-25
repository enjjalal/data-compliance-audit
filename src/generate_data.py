import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker
import pandas as pd
from sqlalchemy import create_engine


def ensure_dirs():
    Path("data").mkdir(parents=True, exist_ok=True)


def generate_users(fake: Faker, num_rows: int) -> pd.DataFrame:
    rows = []
    for i in range(1, num_rows + 1):
        rows.append(
            {
                "id": i,
                "full_name": fake.name(),
                "email": fake.unique.email(),
                "phone_number": fake.phone_number(),
                "dob": fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat(),
            }
        )
    return pd.DataFrame(rows)


def generate_transactions(fake: Faker, num_rows: int, user_max_id: int) -> pd.DataFrame:
    rows = []
    for i in range(1, num_rows + 1):
        rows.append(
            {
                "transaction_id": i,
                "user_id": random.randint(1, user_max_id),
                "amount": round(random.uniform(5, 5000), 2),
                "ip_address": fake.ipv4_public(),
            }
        )
    return pd.DataFrame(rows)


def generate_logs(fake: Faker, num_rows: int, user_max_id: int) -> pd.DataFrame:
    event_types = ["LOGIN", "LOGOUT", "VIEW", "EXPORT", "DOWNLOAD"]
    rows = []
    start = datetime.now() - timedelta(days=30)
    for _ in range(num_rows):
        ts = start + timedelta(seconds=random.randint(0, 30 * 24 * 3600))
        rows.append(
            {
                "timestamp": ts.isoformat(timespec="seconds"),
                "user_id": random.randint(1, user_max_id),
                "event_type": random.choice(event_types),
                "page_url": fake.uri_path(),
            }
        )
    return pd.DataFrame(rows)


def generate_marketing_emails(fake: Faker, num_rows: int) -> pd.DataFrame:
    rows = []
    for _ in range(num_rows):
        rows.append(
            {
                "email": fake.unique.email(),
                "open_rate": round(random.uniform(0, 1), 2),
                "unsubscribe_date": (fake.date_between("-90d", "today") if random.random() < 0.2 else None),
            }
        )
    return pd.DataFrame(rows)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)


def write_sqlite(tables: dict, db_path: Path) -> None:
    engine = create_engine(f"sqlite:///{db_path.as_posix()}")
    with engine.begin() as conn:
        for name, df in tables.items():
            df.to_sql(name, con=conn, index=False, if_exists="replace")


def main() -> None:
    ensure_dirs()
    fake = Faker()
    Faker.seed(42)
    random.seed(42)

    users = generate_users(fake, 500)
    transactions = generate_transactions(fake, 1000, users.shape[0])
    logs = generate_logs(fake, 800, users.shape[0])
    marketing = generate_marketing_emails(fake, 300)

    write_csv(users, Path("data/users.csv"))
    write_csv(transactions, Path("data/transactions.csv"))
    write_csv(logs, Path("data/logs.csv"))
    write_csv(marketing, Path("data/marketing_emails.csv"))

    write_sqlite(
        {
            "users": users,
            "transactions": transactions,
            "logs": logs,
            "marketing_emails": marketing,
        },
        Path("data/compliance.db"),
    )

    print("Generated CSVs in data/ and SQLite DB at data/compliance.db")


if __name__ == "__main__":
    main()


