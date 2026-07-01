import csv
import sqlite3
from pathlib import Path

FIELDS = ["Date", "Category", "Amount", "Description", "Type"]


def get_storage_path(path=None):
    if path:
        return Path(path)
    return Path(__file__).resolve().parent / "expenses.csv"


def _is_sqlite_path(storage_path):
    return storage_path.suffix.lower() in {".db", ".sqlite", ".sqlite3"}


def initialize_csv(storage_path):
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    if storage_path.exists() and storage_path.stat().st_size > 0:
        with storage_path.open("r", newline="", encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
        if rows and rows[0] != FIELDS:
            with storage_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(FIELDS)
                for row in rows:
                    writer.writerow(row)
        return storage_path

    with storage_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(FIELDS)
    return storage_path


def initialize_sqlite(storage_path):
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(storage_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                date TEXT,
                category TEXT,
                amount REAL,
                description TEXT,
                type TEXT
            )
            """
        )
        connection.commit()
    finally:
        connection.close()
    return storage_path


def initialize_file(path=None):
    storage_path = get_storage_path(path)
    if _is_sqlite_path(storage_path):
        return initialize_sqlite(storage_path)
    return initialize_csv(storage_path)


def _expense_from_row(row):
    if not row:
        return None
    date = row.get("Date") or row.get("date") or ""
    category = row.get("Category") or row.get("category") or ""
    amount = row.get("Amount") or row.get("amount") or 0
    description = row.get("Description") or row.get("description") or ""
    transaction_type = row.get("Type") or row.get("type") or "expense"
    return {
        "date": str(date),
        "category": str(category),
        "amount": float(amount),
        "description": str(description),
        "type": str(transaction_type),
    }


def _row_from_expense(expense):
    return [
        expense.get("date", ""),
        expense.get("category", ""),
        expense.get("amount", 0),
        expense.get("description", ""),
        expense.get("type", "expense"),
    ]


def save_expense(expense, path=None):
    storage_path = initialize_file(path)
    expenses = load_expenses(storage_path)
    expenses.append(expense)
    return save_expenses(expenses, storage_path)


def load_expenses(path=None):
    storage_path = initialize_file(path)
    if _is_sqlite_path(storage_path):
        connection = sqlite3.connect(storage_path)
        try:
            rows = connection.execute(
                "SELECT date, category, amount, description, type FROM transactions ORDER BY rowid"
            ).fetchall()
        finally:
            connection.close()
        return [
            {
                "date": row[0] or "",
                "category": row[1] or "",
                "amount": float(row[2] or 0),
                "description": row[3] or "",
                "type": row[4] or "expense",
            }
            for row in rows
        ]

    if not storage_path.exists() or storage_path.stat().st_size == 0:
        return []

    with storage_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return []
        return [_expense_from_row(row) for row in reader if row and any(str(cell).strip() for cell in row.values())]


def save_expenses(expenses, path=None):
    storage_path = initialize_file(path)
    if _is_sqlite_path(storage_path):
        connection = sqlite3.connect(storage_path)
        try:
            connection.execute("DELETE FROM transactions")
            connection.executemany(
                "INSERT INTO transactions (date, category, amount, description, type) VALUES (?, ?, ?, ?, ?)",
                [
                    (
                        expense.get("date", ""),
                        expense.get("category", ""),
                        expense.get("amount", 0),
                        expense.get("description", ""),
                        expense.get("type", "expense"),
                    )
                    for expense in expenses
                ],
            )
            connection.commit()
        finally:
            connection.close()
        return storage_path

    with storage_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(FIELDS)
        for expense in expenses:
            writer.writerow(_row_from_expense(expense))
    return storage_path


def search_transactions_by_category(category, path=None):
    expenses = load_expenses(path)
    return [expense for expense in expenses if expense.get("category", "").lower() == category.lower()]


def filter_transactions_by_date_range(start_date, end_date, path=None):
    expenses = load_expenses(path)
    return [expense for expense in expenses if start_date <= expense.get("date", "") <= end_date]


def export_monthly_report(output_path, month, path=None):
    expenses = load_expenses(path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "category", "amount", "description", "type"])
        writer.writeheader()
        for expense in expenses:
            if str(expense.get("date", ""))[:7] == month:
                writer.writerow(
                    {
                        "date": expense.get("date", ""),
                        "category": expense.get("category", ""),
                        "amount": expense.get("amount", 0),
                        "description": expense.get("description", ""),
                        "type": expense.get("type", "expense"),
                    }
                )
    return output_path


def export_transactions_to_csv(output_path, path=None):
    expenses = load_expenses(path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "category", "amount", "description", "type"])
        writer.writeheader()
        for expense in expenses:
            writer.writerow(
                {
                    "date": expense.get("date", ""),
                    "category": expense.get("category", ""),
                    "amount": expense.get("amount", 0),
                    "description": expense.get("description", ""),
                    "type": expense.get("type", "expense"),
                }
            )
    return output_path


def upgrade_to_sqlite(target_path, source_path=None):
    storage_path = initialize_sqlite(Path(target_path))
    expenses = load_expenses(source_path)
    save_expenses(expenses, storage_path)
    return storage_path
