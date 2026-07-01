from tracker import (
    add_expense,
    delete_expense,
    export_transactions_to_csv,
    filter_expenses_by_date_range,
    load_expenses_into_memory,
    set_budget,
    set_savings_goal,
    show_category_summary,
    show_monthly_total,
    show_remaining_budget,
    show_savings_progress,
    show_spending_insights,
    show_total,
    update_expense,
    view_expenses,
)


def run_console_app():
    load_expenses_into_memory()

    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            description = input("Enter description: ").strip()
            amount_input = input("Enter amount: ").strip()
            category = input("Enter category: ").strip()
            date_input = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            expense, error = add_expense(description, amount_input, category, date_input)
            if error:
                print(error)
            else:
                print(f"Expense added for {expense['date']}.")
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            show_total()
        elif choice == "4":
            show_monthly_total()
        elif choice == "5":
            show_category_summary()
        elif choice == "6":
            budget_input = input("Enter budget limit: ").strip()
            set_budget(budget_input)
        elif choice == "7":
            show_remaining_budget()
        elif choice == "8":
            show_spending_insights()
        elif choice == "9":
            savings_goal_input = input("Enter savings goal: ").strip()
            set_savings_goal(savings_goal_input)
        elif choice == "10":
            show_savings_progress()
        elif choice == "11":
            delete_expense()
        elif choice == "12":
            export_path = input("Enter CSV export path (leave blank for monthly_report.csv): ").strip() or "monthly_report.csv"
            export_transactions_to_csv(export_path)
            print(f"Exported transactions to {export_path}")
        elif choice == "13":
            start_date = input("Start date (YYYY-MM-DD): ").strip()
            end_date = input("End date (YYYY-MM-DD): ").strip()
            expenses = filter_expenses_by_date_range(start_date, end_date)
            if not expenses:
                print("No expenses found in that date range.")
            else:
                for expense in expenses:
                    print(expense)
        elif choice == "14":
            index_input = input("Enter expense number to update: ").strip()
            description = input("Enter new description (leave blank to keep current): ").strip()
            amount_input = input("Enter new amount (leave blank to keep current): ").strip()
            category = input("Enter new category (leave blank to keep current): ").strip()
            date_input = input("Enter new date (YYYY-MM-DD, leave blank to keep current): ").strip()
            updated_expense, error = update_expense(index_input, description or None, amount_input or None, category or None, date_input or None)
            if error:
                print(error)
            else:
                print(f"Updated expense: {updated_expense['description']}")
        elif choice == "15":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


def show_menu():
    print("\nExpense Tracker Menu")
    print("1. Add expense")
    print("2. View expenses")
    print("3. Show total")
    print("4. Show monthly total")
    print("5. Show category summary")
    print("6. Set budget")
    print("7. Show remaining budget")
    print("8. Show spending insights")
    print("9. Set savings goal")
    print("10. Show savings progress")
    print("11. Delete expense")
    print("12. Export to CSV")
    print("13. Filter by date range")
    print("14. Update expense")
    print("15. Exit")


def main():
    run_console_app()


if __name__ == "__main__":
    main()