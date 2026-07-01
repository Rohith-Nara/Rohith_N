from datetime import datetime


def validate_description(description):
    return bool(description and description.strip())


def validate_category(category):
    return bool(category and category.strip())


def validate_amount(amount_input):
    try:
        amount = float(amount_input)
    except (TypeError, ValueError):
        return None, "Amount must be numeric."

    if amount < 0:
        return None, "Amount cannot be negative."

    return amount, None


def normalize_category(category):
    return category.strip().title()


def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")


def normalize_date(date_input):
    if date_input is None:
        return get_current_date()

    value = date_input.strip()
    if not value:
        return get_current_date()

    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return None


def format_currency(amount):
    return f"${amount:,.2f}"
