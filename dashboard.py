import streamlit as st
from utils import set_page_style
from users_module import users_module
from accounts_module import accounts_module
from branch_module import branch_module
from transactions_module import transactions_module
from db_connection import get_connection, get_dict_cursor

st.set_page_config(page_title="Banking Management Dashboard", layout="wide")
set_page_style()

st.title("✨ Banking Management Dashboard")

menu = ["Users", "Accounts", "Branches", "Transactions", "Statistics"]
choice = st.sidebar.selectbox("Navigate", menu)

def show_stats():
    st.header("Dashboard Statistics")

    conn = get_connection()
    cursor = get_dict_cursor(conn)

    # Query stats
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*), COALESCE(SUM(balance),0) AS total_balance FROM accounts")
    accounts_data = cursor.fetchone()
    total_accounts = accounts_data['count']
    total_balance = accounts_data['total_balance']

    cursor.execute("SELECT COUNT(*) FROM branch")
    total_branches = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) FROM transactions")
    total_transactions = cursor.fetchone()['count']

    cursor.close()
    conn.close()

    # Use Streamlit columns for responsive cards
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Users", total_users)
    col2.metric("Total Accounts", total_accounts)
    col3.metric("Total Branches", total_branches)
    col4.metric("Total Transactions", total_transactions)
    col5.metric("Total Balance", f"${total_balance:,.2f}")

# Routing to modules
if choice == "Users":
    users_module()
elif choice == "Accounts":
    accounts_module()
elif choice == "Branches":
    branch_module()
elif choice == "Transactions":
    transactions_module()
elif choice == "Statistics":
    show_stats()
else:
    st.write("Select a module from the sidebar to start.")
