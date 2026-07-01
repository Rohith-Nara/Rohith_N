from datetime import datetime

from storage import (
    export_monthly_report as export_monthly_report_file,
    export_transactions_to_csv as export_transactions_to_csv_file,
    filter_transactions_by_date_range,
    load_expenses,
    save_expense,
    save_expenses,
    search_transactions_by_category,
)
from utils import (
    format_currency,
    normalize_category,
    normalize_date,
    validate_amount,
    validate_category,
    validate_description,
)

expenses = []
budget_limit = None
savings_goal = None
active_storage_path = None


def _load_expenses_for_path(path=None):
    global expenses, active_storage_path
    if not path and active_storage_path is not None:
        path = active_storage_path

    if path is None or path != active_storage_path or not expenses:
        expenses = load_expenses(path)
        active_storage_path = path

    return expenses


def load_expenses_into_memory(path=None):
    return _load_expenses_for_path(path)


def _auto_categorize(description):
    description_lower = description.lower()
    if any(keyword in description_lower for keyword in ["coffee", "tea", "snack", "food", "lunch", "dinner", "pizza"]):
        return "Food"
    if any(keyword in description_lower for keyword in ["bus", "train", "uber", "taxi", "fuel", "metro"]):
        return "Transport"
    if any(keyword in description_lower for keyword in ["book", "course", "tuition", "printer", "stationery"]):
        return "Study"
    if any(keyword in description_lower for keyword in ["rent", "housing", "utility", "wifi"]):
        return "Housing"
    return "Other"


def add_expense(description, amount_input, category, date_input=None, path=None, transaction_type="expense"):
    description = description.strip()
    if not validate_description(description):
        return None, "Description cannot be empty."

    amount, amount_error = validate_amount(amount_input)
    if amount_error:
        return None, amount_error

    category = category.strip()
    if not validate_category(category):
        category = _auto_categorize(description)

    normalized_date = normalize_date(date_input)
    if normalized_date is None:
        return None, "Date must be in YYYY-MM-DD format."

    expense = {
        "date": normalized_date,
        "description": description,
        "amount": amount,
        "category": normalize_category(category),
        "type": transaction_type,
    }

    global expenses, active_storage_path
    _load_expenses_for_path(path)
    expenses.append(expense)
    save_expense(expense, path)
    active_storage_path = path
    return expense, None


def update_expense(index_input, description, amount_input, category, date_input=None, path=None, transaction_type="expense"):
    global expenses, active_storage_path
    _load_expenses_for_path(path)
    if not expenses:
        return None, "No expenses recorded yet."

    try:
        expense_index = int(index_input) - 1
    except (TypeError, ValueError):
        return None, "Invalid expense number."

    if not 0 <= expense_index < len(expenses):
        return None, "Invalid expense number."

    current_expense = expenses[expense_index]
    description = (description or current_expense.get("description", "")).strip()
    if not validate_description(description):
        return None, "Description cannot be empty."

    amount, amount_error = validate_amount(amount_input if amount_input is not None else current_expense.get("amount"))
    if amount_error:
        return None, amount_error

    category_value = (category or current_expense.get("category", "")).strip()
    if not validate_category(category_value):
        category_value = _auto_categorize(description)

    normalized_date = normalize_date(date_input if date_input not in (None, "") else current_expense.get("date"))
    if normalized_date is None:
        return None, "Date must be in YYYY-MM-DD format."

    updated_expense = {
        "date": normalized_date,
        "description": description,
        "amount": amount,
        "category": normalize_category(category_value),
        "type": transaction_type or current_expense.get("type", "expense"),
    }
    expenses[expense_index] = updated_expense
    save_expenses(expenses, path)
    active_storage_path = path
    return updated_expense, None


def view_expenses(path=None):
    global expenses
    _load_expenses_for_path(path)
    if not expenses:
        print("No expenses recorded yet.")
        return

    print(f"{'#':<4} {'Date':<12} {'Description':<20} {'Category':<12} {'Amount':>10}")
    print("-" * 70)
    for row_number, expense in enumerate(expenses, start=1):
        print(
            f"{row_number:<4} {expense['date']:<12} {expense['description']:<20} {expense['category']:<12} {format_currency(expense['amount']):>10}"
        )


def show_total(path=None):
    global expenses
    _load_expenses_for_path(path)
    total_spent = sum(expense["amount"] for expense in expenses if expense.get("type") != "income")
    total_income = sum(expense["amount"] for expense in expenses if expense.get("type") == "income")
    print(f"Total expenses: {format_currency(total_spent)}")
    print(f"Total income: {format_currency(total_income)}")


def show_spending_insights(path=None):
    global expenses
    _load_expenses_for_path(path)
    if not expenses:
        print("No expenses recorded yet.")
        return

    total_spent = sum(expense["amount"] for expense in expenses if expense.get("type") != "income")
    biggest_expense = max(
        (expense for expense in expenses if expense.get("type") != "income"),
        key=lambda item: item["amount"],
        default=None,
    )
    print(f"Student budget insight: total spending is {format_currency(total_spent)}")
    if biggest_expense:
        print(
            f"Largest expense: {biggest_expense['description']} ({format_currency(biggest_expense['amount'])})"
        )


def _build_category_summary(expense_list):
    summary_by_category = {}
    for expense in expense_list:
        category = expense["category"]
        summary_by_category[category] = summary_by_category.get(category, 0) + expense["amount"]
    return summary_by_category


def show_category_summary(path=None):
    global expenses
    _load_expenses_for_path(path)
    if not expenses:
        print("No expenses recorded yet.")
        return

    summary_by_category = _build_category_summary(expenses)

    print("Category Summary:")
    for category, total in sorted(summary_by_category.items()):
        print(f"{category}: {format_currency(total)}")

    highest_category, highest_total = max(summary_by_category.items(), key=lambda item: item[1])
    print(f"Highest spending category: {highest_category} ({format_currency(highest_total)})")


def _get_month_from_date(expense_date):
    if isinstance(expense_date, datetime):
        return expense_date.strftime("%Y-%m")
    return str(expense_date)[:7] if expense_date else ""


def show_monthly_total(path=None):
    global expenses
    _load_expenses_for_path(path)
    if not expenses:
        print("No expenses recorded yet.")
        return

    current_month = datetime.now().strftime("%Y-%m")
    monthly_total = 0.0
    for expense in expenses:
        expense_month = _get_month_from_date(expense.get("date"))
        if expense_month == current_month:
            monthly_total += expense.get("amount", 0)

    print(f"Monthly total ({current_month}): {format_currency(monthly_total)}")


def set_budget(limit_amount, path=None):
    global budget_limit
    try:
        budget_limit = float(limit_amount)
    except (TypeError, ValueError):
        print("Budget must be numeric.")
        return None

    print(f"Budget limit set to {format_currency(budget_limit)}")
    return budget_limit


def show_remaining_budget(path=None):
    global expenses, budget_limit
    _load_expenses_for_path(path)
    if budget_limit is None:
        print("No budget limit set.")
        return

    total_spent = sum(expense["amount"] for expense in expenses if expense.get("type") != "income")
    remaining_budget = budget_limit - total_spent
    if remaining_budget < 0:
        print(f"Overspending alert: {format_currency(abs(remaining_budget))} over budget")
    else:
        print(f"Remaining budget: {format_currency(remaining_budget)}")


def set_savings_goal(goal_amount, path=None):
    global savings_goal
    try:
        savings_goal = float(goal_amount)
    except (TypeError, ValueError):
        print("Savings goal must be numeric.")
        return None

    print(f"Savings goal set to {format_currency(savings_goal)}")
    return savings_goal


def show_savings_progress(path=None):
    global expenses, savings_goal
    _load_expenses_for_path(path)
    if savings_goal is None:
        print("No savings goal set.")
        return

    total_income = sum(expense["amount"] for expense in expenses if expense.get("type") == "income")
    remaining_to_goal = savings_goal - total_income
    print(f"Savings progress: {format_currency(remaining_to_goal)} left to reach your goal")


def search_expenses_by_category(category, path=None):
    return search_transactions_by_category(category, path)


def filter_expenses_by_date_range(start_date, end_date, path=None):
    return filter_transactions_by_date_range(start_date, end_date, path)


def export_monthly_report(output_path, month, path=None):
    return export_monthly_report_file(output_path, month, path)


def export_transactions_to_csv(output_path, path=None):
    return export_transactions_to_csv_file(output_path, path)


def delete_expense(index_input=None, path=None):
    global expenses, active_storage_path
    _load_expenses_for_path(path)
    if not expenses:
        print("No expenses to delete.")
        return None, None

    view_expenses(path)
    if index_input is None:
        index_input = input("Enter expense number to delete: ").strip()

    try:
        expense_index = int(index_input) - 1
    except ValueError:
        print("Invalid expense number.")
        return None, "Invalid expense number."

    if not 0 <= expense_index < len(expenses):
        print("Invalid expense number.")
        return None, "Invalid expense number."

    removed_expense = expenses.pop(expense_index)
    save_expenses(expenses, path)
    active_storage_path = path
    print(f"Deleted: {removed_expense['description']}")
    return removed_expense, None

