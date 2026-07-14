# Expense Tracker Dashboard (Django)

A Django web app with a dashboard showing monthly spend, category breakdown
(doughnut chart), a 6-month trend (bar chart), budget progress, and full
CRUD for expenses and categories.

## Features
- Login / signup (per-user expenses)
- Dashboard: total this month, all-time total, transaction count, top category
- Charts (Chart.js): category doughnut chart + 6-month spending trend
- Optional monthly budget with progress bar
- Expense list with search + filter by category/date range
- Add / edit / delete expenses
- Manage categories (with custom colors used in charts)
- Django admin panel for power-user data management

## Setup in VS Code

1. **Open the folder** `expense_tracker` in VS Code.

2. **Create a virtual environment** (open a terminal in VS Code: `` Ctrl+` ``):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   In VS Code, select this venv as your Python interpreter
   (`Ctrl+Shift+P` → "Python: Select Interpreter" → pick `./venv`).

4. **Run migrations**:
   ```bash
   python manage.py makemigrations tracker
   python manage.py migrate
   ```

5. **(Optional) Seed default categories** (Food, Transport, Bills, etc.):
   ```bash
   python manage.py seed_categories
   ```

6. **Create an admin/superuser account**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the server**:
   ```bash
   python manage.py runserver
   ```

8. Open **http://127.0.0.1:8000/** — you'll be redirected to log in.
   Sign up for a new account, or log in with the superuser you created.
   Visit **http://127.0.0.1:8000/admin/** for the Django admin.

## Project structure
```
expense_tracker/
├── manage.py
├── requirements.txt
├── expense_tracker/       # project settings, urls
└── tracker/                # the app
    ├── models.py           # Expense, Category, Budget
    ├── views.py             # dashboard + CRUD views
    ├── forms.py
    ├── urls.py
    ├── admin.py
    ├── management/commands/seed_categories.py
    └── templates/tracker/   # dashboard.html, expense_list.html, etc.
```

## Next steps you might want
- Add pagination to the expense list for large datasets
- Export expenses to CSV
- Add recurring expenses
- Deploy to Render/Railway/Fly.io (set `DEBUG=False`, configure `ALLOWED_HOSTS`,
  and swap SQLite for Postgres)
