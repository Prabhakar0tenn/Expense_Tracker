import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import expense_backend

current_user = None

class LoginWindow:
    def __init__(self, master):
        self.master = master
        master.title("Expense Tracker - Login")
        master.geometry("400x280")
        master.configure(bg="#2C3E50")
        frame = tk.Frame(master, bg="#2C3E50"); frame.pack(pady=30)

        lbl_font = ("Helvetica", 12)
        ent_font = ("Helvetica", 12)
        btn_font = ("Helvetica", 12, "bold")

        tk.Label(frame, text="Username:", font=lbl_font, bg="#2C3E50", fg="white")\
          .grid(row=0, column=0, sticky="e", pady=5)
        self.u = tk.Entry(frame, font=ent_font, width=20); self.u.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Password:", font=lbl_font, bg="#2C3E50", fg="white")\
          .grid(row=1, column=0, sticky="e", pady=5)
        self.p = tk.Entry(frame, font=ent_font, show="*", width=20); self.p.grid(row=1, column=1, pady=5)

        btn_frame = tk.Frame(master, bg="#2C3E50"); btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="Login", font=btn_font, bg="#27AE60", fg="white",
                  width=12, bd=0, relief="ridge", command=self.login)\
          .grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Register", font=btn_font, bg="#2980B9", fg="white",
                  width=12, bd=0, relief="ridge", command=self.register)\
          .grid(row=0, column=1, padx=10)

    def login(self):
        u, p = self.u.get().strip(), self.p.get().strip()
        if not u or not p:
            messagebox.showerror("Error", "Both fields required!"); return
        if expense_backend.login_user(u, p):
            global current_user; current_user = u
            self.master.destroy(); MainAppWindow()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials!")

    def register(self):
        u, p = self.u.get().strip(), self.p.get().strip()
        if not u or not p:
            messagebox.showerror("Error", "Both fields required!"); return
        if expense_backend.register_user(u, p):
            messagebox.showinfo("Success", "Registered! Please login.")
        else:
            messagebox.showerror("Error", "Username exists!")

class MainAppWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Expense Tracker - {current_user}")
        self.root.geometry("1000x650")
        self.root.configure(bg="#34495E")

        self.last_graph_mode = "both"

        # ─── Top Menu ─────────────────────────────
        menu_frame = tk.Frame(self.root, bg="#34495E"); menu_frame.pack(fill="x", pady=10)
        btn_font = ("Helvetica", 12, "bold")
        for txt, cmd in [
            ("Main",       lambda: self.show_section("main")),
            ("Goals",      self.popup_goals),
            ("Graph",      lambda: [self.show_section("graph"), self.draw_graph(self.last_graph_mode)]),
            ("Export PDF", self.export_pdf),
            ("Logout",     self.logout),
        ]:
            bgc = {
                "Main":       "#2980B9",
                "Goals":      "#16A085",
                "Graph":      "#2471A3",
                "Export PDF": "#1ABC9C",
                "Logout":     "#C0392B"
            }[txt]
            tk.Button(menu_frame, text=txt, font=btn_font, bg=bgc, fg="white",
                      width=12, height=2, bd=0, relief="ridge", command=cmd)\
              .pack(side="left", padx=5)

        # ─── Section Frames ───────────────────────
        self.frames = {}
        for name in ("main","graph"):
            self.frames[name] = tk.Frame(self.root, bg="#34495E")
        self.build_main(self.frames["main"])
        self.build_graph(self.frames["graph"])

        # Balance label
        self.bal_var = tk.StringVar()
        tk.Label(self.root, textvariable=self.bal_var,
                 font=("Helvetica",14,"bold"), fg="white", bg="#34495E")\
          .pack(pady=5)

        self.show_section("main")
        self.refresh_all()
        self.root.mainloop()

    def export_pdf(self):
        now = datetime.now()
        default = f"{current_user}_{now.year}-{now.month:02d}_report.pdf"
        path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                            initialfile=default,
                                            filetypes=[("PDF Files","*.pdf")])
        if not path: return
        ok = expense_backend.generate_pdf(current_user, path)
        if ok:
            messagebox.showinfo("PDF Saved", f"Report saved to:\n{path}")
        else:
            messagebox.showerror("Error", "Failed to export PDF.")

    def logout(self):
        self.root.destroy()
        root = tk.Tk()
        LoginWindow(root)
        root.mainloop()

    def show_section(self, name):
        for fr in self.frames.values():
            fr.pack_forget()
        self.frames[name].pack(fill="both", expand=True)

    # ─── Main Section ─────────────────────────
    def build_main(self, f):
        btn_font = ("Helvetica", 12, "bold")
        top = tk.Frame(f, bg="#34495E"); top.pack(pady=10)
        tk.Button(top, text="Add Income",  font=btn_font, bg="#2980B9", fg="white",
                  width=12, bd=0, relief="ridge", command=self.popup_add_income)\
          .grid(row=0, column=0, padx=5)
        tk.Button(top, text="Add Expense", font=btn_font, bg="#27AE60", fg="white",
                  width=12, bd=0, relief="ridge", command=self.popup_add_expense)\
          .grid(row=0, column=1, padx=5)
        tk.Button(top, text="Delete Selected", font=btn_font, bg="#C0392B", fg="white",
                  width=14, bd=0, relief="ridge", command=self.delete_selected)\
          .grid(row=0, column=2, padx=5)

        mid = tk.Frame(f, bg="#34495E"); mid.pack(fill="both", expand=True, padx=20, pady=10)
        incf = tk.LabelFrame(mid, text="Income", font=("Helvetica",12,"bold"),
                             bg="#2C3E50", fg="white"); incf.pack(side="left", fill="both", expand=True, padx=5)
        self.tv_inc = ttk.Treeview(incf, columns=("Date","Source","Amount"), show="headings")
        for c in ("Date","Source","Amount"): self.tv_inc.heading(c, text=c)
        self.tv_inc.pack(fill="both", expand=True, padx=5, pady=5)

        expf = tk.LabelFrame(mid, text="Expense", font=("Helvetica",12,"bold"),
                             bg="#2C3E50", fg="white"); expf.pack(side="right", fill="both", expand=True, padx=5)
        self.tv_exp = ttk.Treeview(expf, columns=("Date","Category","Amount"), show="headings")
        for c in ("Date","Category","Amount"): self.tv_exp.heading(c, text=c)
        self.tv_exp.pack(fill="both", expand=True, padx=5, pady=5)

    def delete_selected(self):
        sel = self.tv_inc.focus() or self.tv_exp.focus()
        if not sel: return
        tree = self.tv_inc if self.tv_inc.exists(sel) else self.tv_exp
        vals = tree.item(sel,"values")
        if tree == self.tv_inc:
            expense_backend.delete_income(current_user, {
                "source": vals[1], "amount": int(vals[2]), "date": vals[0]
            })
        else:
            expense_backend.delete_expense(current_user, {
                "category": vals[1], "amount": int(vals[2]), "date": vals[0]
            })
        self.refresh_all()

    def popup_add_income(self):
        d = tk.Toplevel(self.root); d.title("Add Income"); d.geometry("350x220"); d.configure(bg="#34495E")
        tk.Label(d, text="Source:", font=("Helvetica",12), bg="#34495E", fg="white").pack(pady=8)
        e1 = tk.Entry(d, font=("Helvetica",12)); e1.pack(pady=5)
        tk.Label(d, text="Amount:", font=("Helvetica",12), bg="#34495E", fg="white").pack(pady=8)
        e2 = tk.Entry(d, font=("Helvetica",12)); e2.pack(pady=5)
        def add():
            s,a = e1.get().strip(), e2.get().strip()
            if not s or not a.isdigit(): messagebox.showerror("Error","Invalid!"); return
            dt = datetime.now().strftime("%d-%m-%Y")
            expense_backend.add_income(current_user, s, int(a), dt)
            d.destroy(); self.refresh_all()
        tk.Button(d, text="Add Income", font=("Helvetica",12,"bold"),
                  bg="#2980B9", fg="white", bd=0, relief="ridge", command=add).pack(pady=15)

    def popup_add_expense(self):
        d = tk.Toplevel(self.root); d.title("Add Expense"); d.geometry("350x220"); d.configure(bg="#34495E")
        tk.Label(d, text="Category:", font=("Helvetica",12), bg="#34495E", fg="white").pack(pady=8)
        e1 = tk.Entry(d, font=("Helvetica",12)); e1.pack(pady=5)
        tk.Label(d, text="Amount:", font=("Helvetica",12), bg="#34495E", fg="white").pack(pady=8)
        e2 = tk.Entry(d, font=("Helvetica",12)); e2.pack(pady=5)
        def add():
            c,a = e1.get().strip(), e2.get().strip()
            if not c or not a.isdigit(): messagebox.showerror("Error","Invalid!"); return
            dt = datetime.now().strftime("%d-%m-%Y")
            # 1) add the expense
            expense_backend.add_expense(current_user, c, int(a), dt, "")
            self.refresh_all()
            d.destroy()
            # 2) now check goals
            goals = expense_backend.get_goals(current_user)
            # monthly check
            mon_goal = goals.get("monthly")
            if mon_goal is not None:
                total_mon = expense_backend.get_monthly_expense(current_user)
                if total_mon > mon_goal:
                    over = total_mon - mon_goal
                    messagebox.showwarning("Monthly Limit Exceeded",
                                           f"You have exceeded your monthly limit by ₹{over}!")
            # yearly check
            yr_goal = goals.get("yearly")
            if yr_goal is not None:
                total_yr = expense_backend.get_yearly_expense(current_user)
                if total_yr > yr_goal:
                    over = total_yr - yr_goal
                    messagebox.showwarning("Yearly Limit Exceeded",
                                           f"You have exceeded your yearly limit by ₹{over}!")
        tk.Button(d, text="Add Expense", font=("Helvetica",12,"bold"),
                  bg="#27AE60", fg="white", bd=0, relief="ridge", command=add).pack(pady=15)

    # ─── Goals pop-up ───────────────────────────
    def popup_goals(self):
        d = tk.Toplevel(self.root); d.title("Set Goals"); d.geometry("360x260"); d.configure(bg="#34495E")
        tk.Label(d, text="Monthly Limit:", font=("Helvetica",12), bg="#34495E", fg="white").pack(pady=10)
        mvar = tk.IntVar(value=expense_backend.get_goals(current_user).get("monthly",0))
        tk.Entry(d, textvariable=mvar, font=("Helvetica",12)).pack(pady=5)
        tk.Label(d, text="Yearly Limit:", font=("Helvetica",12), bg="#34495E", fg="white").pack(pady=10)
        yvar = tk.IntVar(value=expense_backend.get_goals(current_user).get("yearly",0))
        tk.Entry(d, textvariable=yvar, font=("Helvetica",12)).pack(pady=5)
        def save():
            expense_backend.set_goals(current_user,
                monthly=mvar.get() or None, yearly=yvar.get() or None)
            d.destroy(); self.refresh_all()
        tk.Button(d, text="Save Goals", font=("Helvetica",12,"bold"),
                  bg="#16A085", fg="white", bd=0, relief="ridge", command=save).pack(pady=20)

    # ─── Graph section ─────────────────────────
    def build_graph(self, f):
        btnf = tk.Frame(f, bg="#34495E"); btnf.pack(pady=10)
        for txt, mode in [("Inc vs Exp","both"), ("Yearly Exp","yearly"), ("Exp by Cat","pie")]:
            tk.Button(btnf, text=txt, font=("Helvetica",11,"bold"),
                      bg="#8E44AD", fg="white", width=14, bd=0, relief="ridge",
                      command=lambda m=mode: self._on_graph(m)).pack(side="left", padx=8)
        self.fig = plt.Figure(figsize=(6,4), dpi=85)
        self.canvas = FigureCanvasTkAgg(self.fig, master=f)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=15)

    def _on_graph(self, mode):
        self.last_graph_mode = mode; self.draw_graph(mode)

    def draw_graph(self, mode):
        self.fig.clear()
        if mode == "both":
            ax = self.fig.add_subplot(111)
            inc = expense_backend.total_income(current_user)
            exp = expense_backend.total_expense(current_user)
            ax.bar(["Income","Expense"], [inc, exp], color=["#2980B9","#C0392B"])
            ax.set_title("Income vs Expense", fontdict={"fontsize":14,"fontweight":"bold"})
        elif mode == "yearly":
            ax = self.fig.add_subplot(111)
            year = datetime.now().year
            months = list(range(1,13))
            vals = [expense_backend.get_monthly_expense(current_user, year, m) for m in months]
            ax.bar(months, vals, color="#27AE60")
            ax.set_title(f"Monthly Expenses ({year})", fontdict={"fontsize":14,"fontweight":"bold"})
            ax.set_xlabel("Month"); ax.set_ylabel("Amount"); ax.set_xticks(months)
        else:  # pie
            ax = self.fig.add_subplot(111)
            data = expense_backend.get_category_breakdown(current_user)
            wedges, _, _ = ax.pie(data.values(), autopct='%1.1f%%', startangle=90)
            ax.legend(wedges, data.keys(), title="Category", loc="center left", bbox_to_anchor=(1,0.5))
            ax.set_title("Expense by Category", fontdict={"fontsize":14,"fontweight":"bold"})
        self.canvas.draw()

    def refresh_all(self):
        self.tv_inc.delete(*self.tv_inc.get_children())
        self.tv_exp.delete(*self.tv_exp.get_children())
        for i in expense_backend.view_income(current_user):
            self.tv_inc.insert("", "end", values=(i["date"], i["source"], i["amount"]))
        for e in expense_backend.view_expenses(current_user):
            self.tv_exp.insert("", "end", values=(e["date"], e["category"], e["amount"]))

        bal = expense_backend.total_income(current_user) - expense_backend.total_expense(current_user)
        self.bal_var.set(f"Net Balance: {bal}")
        self.draw_graph(self.last_graph_mode)

if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
