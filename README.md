# Expense Tracker

## Features

### Core Features
- Add new expenses with date, category, amount, and description.
- View all recorded expenses in a clear list or table.
- Delete an expense by selecting its index or record.
- Show total spending across all recorded expenses.
- Generate category-wise spending summaries.
- Generate monthly spending summaries.

### Data Storage
- Save expenses persistently so data remains available after restarting the program.
- Use CSV-based storage in the initial version for simplicity and easy inspection.
- Upgrade to SQLite in the advanced version for more reliable structured storage.
- Automatically create the required data file or database if it does not already exist.

### Validation and Reliability
- Validate user input to prevent empty fields, invalid numbers, and negative amounts.
- Handle missing files and empty data safely without crashing.
- Prevent invalid delete operations with proper error handling.
- Format output clearly for better readability in the CLI version.

### Budgeting
- Set a custom budget limit.
- Track the remaining budget after expenses are recorded.
- Show a warning when total spending exceeds the budget.

### Filtering and Analysis
- Filter expenses by category.
- Filter expenses by date or date range in later versions.
- Analyze spending patterns with summaries and reports.

### Advanced Version
- Upgrade the project to a GUI version using Tkinter.
- Display expenses in a GUI table or Treeview.
- Add edit and update functionality for existing expense records.
- Export expense data to CSV in the GUI or database-backed version.
- Visualize spending with charts such as pie charts or monthly/category graphs.

### Code Quality
- Organize the project into separate modules for logic, storage, and utility functions.
- Use a menu-driven command-line interface in the first version.
- Structure the repository clearly for GitHub with clean commits and documentation.
