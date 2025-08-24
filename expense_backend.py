import pymongo
from datetime import datetime
from fpdf import FPDF

client = pymongo.MongoClient("mongodb://localhost:27017/")
db     = client["expense_db"]

expense_collection = db["expenses"]
income_collection  = db["income"]
user_collection    = db["users"]
goals_collection   = db["goals"]
savings_collection = db["savings"]

def register_user(username, password):
    if user_collection.find_one({"username": username}):
        return False
    user_collection.insert_one({"username": username, "password": password})
    return True

def login_user(username, password):
    return bool(user_collection.find_one({"username": username, "password": password}))

def add_expense(username, category, amount, date, description):
    expense_collection.insert_one({
        "username":    username,
        "category":    category,
        "amount":      amount,
        "date":        date,
        "description": description
    })

def add_income(username, source, amount, date):
    income_collection.insert_one({
        "username": username,
        "source":   source,
        "amount":   amount,
        "date":     date
    })

def view_expenses(username):
    return list(expense_collection.find({"username": username}))

def view_income(username):
    return list(income_collection.find({"username": username}))

def delete_expense(username, detail):
    expense_collection.delete_one({
        "username": username,
        "category": detail["category"],
        "amount":   detail["amount"],
        "date":     detail["date"]
    })

def delete_income(username, detail):
    income_collection.delete_one({
        "username": username,
        "source":   detail["source"],
        "amount":   detail["amount"],
        "date":     detail["date"]
    })

def set_goals(username, monthly=None, yearly=None):
    update = {}
    if monthly is not None: update["monthly"] = monthly
    if yearly  is not None: update["yearly"]  = yearly
    goals_collection.update_one({"username": username}, {"$set": update}, upsert=True)

def get_goals(username):
    return goals_collection.find_one({"username": username}) or {}

def add_saving(username, title, amount, date):
    savings_collection.insert_one({
        "username": username,
        "title":    title,
        "amount":   amount,
        "date":     date
    })

def view_savings(username):
    return list(savings_collection.find({"username": username}))

def total_income(username):
    return sum(i["amount"] for i in view_income(username))

def total_expense(username):
    return sum(e["amount"] for e in view_expenses(username))

def get_monthly_expense(username, year=None, month=None):
    now = datetime.now()
    y, m = year or now.year, month or now.month
    total = 0
    for e in view_expenses(username):
        try:
            dt = datetime.strptime(e["date"], "%d-%m-%Y")
        except:
            dt = _parse_date(e["date"])
        if dt.year == y and dt.month == m:
            total += e["amount"]
    return total

def get_yearly_expense(username, year=None):
    y = year or datetime.now().year
    total = 0
    for e in view_expenses(username):
        try:
            dt = datetime.strptime(e["date"], "%d-%m-%Y")
        except:
            dt = _parse_date(e["date"])
        if dt.year == y:
            total += e["amount"]
    return total

def get_category_breakdown(username):
    breakdown = {}
    for e in view_expenses(username):
        cat = e["category"]
        breakdown[cat] = breakdown.get(cat, 0) + e["amount"]
    return breakdown

def _parse_date(dstr):
    for fmt in ("%d-%m-%Y","%d-%m-%y"):
        try:
            return datetime.strptime(dstr,fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {dstr}")

def generate_pdf(username: str, file_path: str) -> bool:
    try:
        now = datetime.now()
        y, m = now.year, now.month

        inc_docs = [d for d in view_income(username)
                    if (_dt := _parse_date(d["date"])).year==y and _dt.month==m]
        exp_docs = [d for d in view_expenses(username)
                    if (_dt := _parse_date(d["date"])).year==y and _dt.month==m]

        pdf = FPDF()
        pdf.set_auto_page_break(True, margin=15)
        pdf.add_page()

        pdf.set_font("Arial","B",16)
        pdf.cell(0,10, f"Expense Report - {username}", ln=True, align="C")
        pdf.ln(5)

        pdf.set_font("Arial",size=12)
        pdf.cell(0,8,f"Month: {y}-{m:02d}", ln=True); pdf.ln(5)

        pdf.set_font("Arial","B",12); pdf.cell(0,8,"Income:", ln=True)
        pdf.set_font("Arial",size=11)
        if inc_docs:
            for d in inc_docs:
                pdf.cell(0,6, f"{d['date']} | {d['source']:<15} | Rs{d['amount']}", ln=True)
        else:
            pdf.cell(0,6,"None",ln=True)
        pdf.ln(5)

        pdf.set_font("Arial","B",12); pdf.cell(0,8,"Expense:", ln=True)
        pdf.set_font("Arial",size=11)
        if exp_docs:
            for d in exp_docs:
                pdf.cell(0,6, f"{d['date']} | {d['category']:<15} | Rs{d['amount']}", ln=True)
        else:
            pdf.cell(0,6,"None",ln=True)
        pdf.ln(5)

        total_inc = sum(d["amount"] for d in inc_docs)
        total_exp = sum(d["amount"] for d in exp_docs)
        pdf.set_font("Arial","B",12)
        pdf.cell(0,8, f"Total Income : Rs{total_inc}", ln=True)
        pdf.cell(0,8, f"Total Expense: Rs{total_exp}", ln=True)
        pdf.cell(0,8, f"Net Balance  : Rs{(total_inc-total_exp)}", ln=True)

        pdf.output(file_path)
        return True
    except Exception as e:
        print("PDF error:", e)
        return False
