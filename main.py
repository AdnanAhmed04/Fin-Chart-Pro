pip install pandas matplotlib
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from datetime import date

CSV_FILE = "expenses.csv"

# Create CSV with headers if not exists
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["Date", "Category", "Amount"])
    df.to_csv(CSV_FILE, index=False)

def add_expense():
    date_val = date_entry.get()
    category = category_entry.get()
    amount = amount_entry.get()

    if not (date_val and category and amount):
        messagebox.showerror("Error", "Please fill all fields")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number")
        return

    new_row = pd.DataFrame([[date_val, category, amount]], columns=["Date", "Category", "Amount"])
    df = pd.read_csv(CSV_FILE)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    clear_entries()
    update_table()
    messagebox.showinfo("Success", "Expense added successfully!")

def delete_selected():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "No row selected!")
        return

    index = tree.index(selected[0])
    df = pd.read_csv(CSV_FILE)
    df = df.drop(index)
    df.to_csv(CSV_FILE, index=False)
    update_table()
    messagebox.showinfo("Deleted", "Expense deleted successfully!")

def edit_selected():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "No row selected to edit!")
        return

    index = tree.index(selected[0])
    df = pd.read_csv(CSV_FILE)

    new_date = date_entry.get()
    new_category = category_entry.get()
    new_amount = amount_entry.get()

    if not (new_date and new_category and new_amount):
        messagebox.showerror("Error", "Please fill all fields")
        return

    try:
        new_amount = float(new_amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number")
        return

    df.at[index, "Date"] = new_date
    df.at[index, "Category"] = new_category
    df.at[index, "Amount"] = new_amount
    df.to_csv(CSV_FILE, index=False)
    update_table()
    clear_entries()
    messagebox.showinfo("Updated", "Expense updated successfully!")

def on_row_select(event):
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0], 'values')
        date_entry.delete(0, tk.END)
        category_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)
        date_entry.insert(0, values[0])
        category_entry.insert(0, values[1])
        amount_entry.insert(0, values[2])

def clear_entries():
    date_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)

def update_table():
    for row in tree.get_children():
        tree.delete(row)
    df = pd.read_csv(CSV_FILE)
    for _, row in df.iterrows():
        tree.insert("", tk.END, values=(row["Date"], row["Category"], row["Amount"]))
    update_total()

def update_total():
    try:
        df = pd.read_csv(CSV_FILE)
        total = df["Amount"].astype(float).sum()
        total_label.config(text=f"Total Expense: ${total:.2f}")
    except:
        total_label.config(text="Total Expense: $0.00")

def show_pie_chart():
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        messagebox.showinfo("Info", "No data to visualize.")
        return
    summary = df.groupby("Category")["Amount"].sum()

    fig, ax = plt.subplots()
    summary.plot.pie(ax=ax, autopct="%1.1f%%", startangle=90)
    ax.set_ylabel("")
    ax.set_title("Expenses by Category")

    chart_window = tk.Toplevel(root)
    chart_window.title("Expense Chart")
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

# GUI Setup
root = tk.Tk()
root.title("🧾 Expense Tracker")
root.geometry("720x580")

# Input Frame
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Date (YYYY-MM-DD)").grid(row=0, column=0, padx=5)
tk.Label(input_frame, text="Category").grid(row=0, column=1, padx=5)
tk.Label(input_frame, text="Amount").grid(row=0, column=2, padx=5)

date_entry = tk.Entry(input_frame)
category_entry = tk.Entry(input_frame)
amount_entry = tk.Entry(input_frame)

date_entry.insert(0, str(date.today()))

date_entry.grid(row=1, column=0, padx=5)
category_entry.grid(row=1, column=1, padx=5)
amount_entry.grid(row=1, column=2, padx=5)

tk.Button(input_frame, text="Add Expense", command=add_expense).grid(row=1, column=3, padx=10)

# Table
tree = ttk.Treeview(root, columns=("Date", "Category", "Amount"), show="headings", height=12)
tree.heading("Date", text="Date")
tree.heading("Category", text="Category")
tree.heading("Amount", text="Amount")
tree.pack(pady=10, fill=tk.BOTH, expand=True)
tree.bind("<<TreeviewSelect>>", on_row_select)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="📊 Show Chart", command=show_pie_chart).grid(row=0, column=0, padx=10)
tk.Button(button_frame, text="🗑️ Delete Selected", command=delete_selected).grid(row=0, column=1, padx=10)
tk.Button(button_frame, text="✏️ Edit Selected", command=edit_selected).grid(row=0, column=2, padx=10)

# Total Label
total_label = tk.Label(root, text="Total Expense: $0.00", font=("Arial", 12, "bold"), fg="green")
total_label.pack(pady=10)

# Load data
update_table()

root.mainloop()
