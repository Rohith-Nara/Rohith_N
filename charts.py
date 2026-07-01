from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tracker import load_expenses_into_memory


def save_category_chart(output_path="category_chart.png"):
    expenses = load_expenses_into_memory()
    summary = {}
    for expense in expenses:
        category = expense.get("category", "Uncategorized")
        summary[category] = summary.get(category, 0) + expense.get("amount", 0)

    if not summary:
        return None

    labels = list(summary.keys())
    values = list(summary.values())
    figure = plt.figure(figsize=(6, 4))
    figure.gca().pie(values, labels=labels, autopct="%1.1f%%")
    figure.gca().set_title("Category Overview")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path)
    plt.close(figure)
    return output_path
