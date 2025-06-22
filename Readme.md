# 💰 AI-Powered Personal Finance Manager

This is a full-featured Flask-based web application to help users track their **income**, **expenses**, set **monthly budget goals**, and monitor **recurring expenses**. It also provides interactive **data visualizations**, **PDF/Excel export**, and **financial tips** to improve budgeting habits.

---

## 🚀 Features

* 🔐 User Authentication (Register/Login/Logout)
* 📥 Add & track income and expenses
* 🎯 Set and manage monthly budget goals
* 🔁 Add & edit recurring expenses with daily/weekly/monthly frequency
* 📊 Visualizations (Pie, Bar, Line) using Plotly
* 📤 Export to Excel or PDF
* ⚠️ Smart alerts when budget is exceeded
* 📋 Expense history and recurring table
* 🌗 Dark mode toggle
* 💡 Financial education tips (50/30/20 rule, overspending control)

---

## 🗂️ Project Structure

```
.
├── app.py                    # Main Flask application
├── requirements.txt         # Python dependencies
├── create_tables.py         # Script to initialize DB tables
├── add_recurring_table.py   # Script to add recurring_expenses table
├── schema.sql               # SQL schema for all tables
├── static/
│   └── styles.css           # Custom styles (optional)
│   └── tips/                # Financial education images
├── templates/
│   ├── layout.html          # Base layout with dark mode toggle
│   ├── login.html           # Login form
│   ├── register.html        # Registration form
│   ├── dashboard.html       # Main dashboard
│   ├── charts.html          # Visualizations
│   ├── edit_recurring.html  # Edit recurring expense form
│   └── tips.html            # Financial education tips
├── LICENSE                  # MIT License
└── README.md                # Project documentation
```

---

## 🛠️ Installation

### ⚙️ Prerequisites

* Python 3.10+
* pip

### 📦 Setup Steps

```bash
# Clone the repository
$ git clone https://github.com/yourusername/finance-manager.git
$ cd finance-manager

# Create virtual environment (optional but recommended)
$ python -m venv venv
$ source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
$ pip install -r requirements.txt

# Initialize the database
$ python create_tables.py
$ python add_recurring_table.py

# Run the app
$ python app.py
```

Visit: `http://localhost:5000`

---

## 🧾 Deployment (Render Example)

### `render.yaml`

```yaml
services:
- type: web
  name: Finance_Manager_Web_Flask_APP
  env: python
  buildCommand: pip install -r requirements.txt
  startCommand: gunicorn app:app
  plan: Free
```

Place `render.yaml` in the root and connect the GitHub repo to Render.

---

## 📊 Visualizations

* 🥧 Pie chart: Expenses by Category
* 📊 Bar chart: Category-wise breakdown
* 📈 Line chart: Daily spending trend

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

---

## 🙋‍♂️ Author

Developed by **Aamir**

---

## ✨ Future Enhancements

* Email notifications for recurring expenses
* Monthly report summaries
* More charts (e.g., income vs expenses trend)
* REST API support for mobile integration
