import tkinter as tk
from tkinter import ttk

from charts import save_category_chart
from tracker import (
    add_expense,
    delete_expense,
    export_monthly_report,
    export_transactions_to_csv,
    load_expenses_into_memory,
    show_total,
    update_expense,
)


class ExpenseTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("900x600")
        self.expenses = []
        self._build_ui()
        self._refresh_transactions()

    def _build_ui(self):
        form = ttk.Frame(self, padding=10)
        form.grid(row=0, column=0, sticky="nsew")

        ttk.Label(form, text="Description").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.description_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.description_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Amount").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.amount_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Category").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.category_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.category_var).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form, text="Date").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.date_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.date_var).grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(form, text="Type").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.type_var = tk.StringVar(value="expense")
        ttk.Combobox(form, textvariable=self.type_var, values=["expense", "income"], state="readonly").grid(row=4, column=1, padx=5, pady=5)

        button_row = ttk.Frame(form)
        button_row.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(button_row, text="Add", command=self._add_transaction).pack(side="left", padx=5)
        ttk.Button(button_row, text="Update Selected", command=self._update_selected).pack(side="left", padx=5)
        ttk.Button(button_row, text="Delete Selected", command=self._delete_selected).pack(side="left", padx=5)
        ttk.Button(button_row, text="Refresh", command=self._refresh_transactions).pack(side="left", padx=5)
        ttk.Button(button_row, text="Show Summary", command=self._show_summary).pack(side="left", padx=5)
        ttk.Button(button_row, text="Export CSV", command=self._export_csv).pack(side="left", padx=5)
        ttk.Button(button_row, text="Save Chart", command=self._save_chart).pack(side="left", padx=5)

        self.result_var = tk.StringVar(value="")
        ttk.Label(form, textvariable=self.result_var, wraplength=800, justify="left").grid(row=6, column=0, columnspan=2, padx=5, pady=10)

        table_frame = ttk.Frame(self, padding=(10, 0, 10, 10))
        table_frame.grid(row=1, column=0, sticky="nsew")
        self.tree = ttk.Treeview(table_frame, columns=("Date", "Description", "Category", "Amount", "Type"), show="headings")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Type", text="Type")
        self.tree.column("Date", width=90)
        self.tree.column("Description", width=220)
        self.tree.column("Category", width=120)
        self.tree.column("Amount", width=90)
        self.tree.column("Type", width=80)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _refresh_transactions(self):
        self.expenses = load_expenses_into_memory()
        for row in self.tree.get_children():
            self.tree.delete(row)
        for index, expense in enumerate(self.expenses):
            self.tree.insert("", "end", iid=str(index), values=(expense.get("date", ""), expense.get("description", ""), expense.get("category", ""), expense.get("amount", 0), expense.get("type", "expense")))

    def _on_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        index = int(selected[0])
        expense = self.expenses[index]
        self.description_var.set(expense.get("description", ""))
        self.amount_var.set(expense.get("amount", ""))
        self.category_var.set(expense.get("category", ""))
        self.date_var.set(expense.get("date", ""))
        self.type_var.set(expense.get("type", "expense"))

    def _add_transaction(self):
        description = self.description_var.get().strip()
        amount = self.amount_var.get().strip()
        category = self.category_var.get().strip()
        date_value = self.date_var.get().strip()
        transaction_type = self.type_var.get()
        expense, error = add_expense(description, amount, category, date_value or None, None, transaction_type=transaction_type)
        if error:
            self.result_var.set(error)
        else:
            self.result_var.set(f"Added {transaction_type}: {description}")
            self._refresh_transactions()

    def _update_selected(self):
        selected = self.tree.selection()
        if not selected:
            self.result_var.set("Select an expense first.")
            return
        index = selected[0]
        description = self.description_var.get().strip()
        amount = self.amount_var.get().strip()
        category = self.category_var.get().strip()
        date_value = self.date_var.get().strip()
        transaction_type = self.type_var.get()
        updated, error = update_expense(index, description, amount or None, category, date_value or None, None, transaction_type=transaction_type)
        if error:
            self.result_var.set(error)
        else:
            self.result_var.set(f"Updated {updated['description']}")
            self._refresh_transactions()

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            self.result_var.set("Select an expense first.")
            return
        deleted, error = delete_expense(int(selected[0]) + 1)
        if error:
            self.result_var.set(error)
        else:
            self.result_var.set(f"Deleted {deleted['description']}")
            self._refresh_transactions()

    def _show_summary(self):
        output = []
        from io import StringIO
        import contextlib

        with contextlib.redirect_stdout(StringIO()) as stream:
            show_total()
            output.append(stream.getvalue())
        self.result_var.set(output[0].strip())

    def _export_csv(self):
        from pathlib import Path

        report_path = Path("monthly_report.csv")
        export_transactions_to_csv(report_path)
        self.result_var.set(f"Exported transactions to {report_path}")

    def _save_chart(self):
        chart_path = save_category_chart("category_chart.png")
        if chart_path:
            self.result_var.set(f"Saved chart to {chart_path}")
        else:
            self.result_var.set("No data available for chart")


def main():
    app = ExpenseTrackerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
