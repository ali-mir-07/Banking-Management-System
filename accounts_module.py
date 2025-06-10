import streamlit as st
from db_connection import get_connection, get_dict_cursor
import pandas as pd

def accounts_module():
    st.header("Accounts Management")

    conn = get_connection()
    cursor = get_dict_cursor(conn)

    # Load accounts
    cursor.execute("""
        SELECT a.account_id, a.user_id, u.full_name, a.branch_id, b.branch_name, 
               a.account_type, a.balance, a.status, a.created_at
        FROM accounts a
        LEFT JOIN users u ON a.user_id = u.user_id
        LEFT JOIN branch b ON a.branch_id = b.branch_id
        ORDER BY a.account_id
    """)
    accounts = cursor.fetchall()
    df = pd.DataFrame(accounts)

    if not df.empty:
        st.dataframe(df)

        # Select account for update/delete/history/balance check
        account_ids = df['account_id'].tolist()
        selected_account = st.selectbox("Select Account ID", account_ids)

        if selected_account:
            account_data = df[df['account_id'] == selected_account].iloc[0]

            # Update form
            with st.form("update_account_form"):
                account_type = st.selectbox("Account Type", ["Savings", "Checking", "Credit"], index=["Savings", "Checking", "Credit"].index(account_data['account_type']))
                status = st.selectbox("Status", ["Active", "Inactive", "Closed"], index=["Active", "Inactive", "Closed"].index(account_data['status']))

                submitted = st.form_submit_button("Update Account")
                if submitted:
                    try:
                        cursor.execute("""
                            UPDATE accounts SET account_type=%s, status=%s WHERE account_id=%s
                        """, (account_type, status, selected_account))
                        conn.commit()
                        st.success("Account updated successfully!")
                    except Exception as e:
                        st.error(f"Error updating account: {e}")

            if st.button("Delete Account"):
                try:
                    cursor.execute("DELETE FROM accounts WHERE account_id=%s", (selected_account,))
                    conn.commit()
                    st.success("Account deleted successfully!")
                except Exception as e:
                    st.error(f"Error deleting account: {e}")

            # Balance check
            st.subheader("Balance Check")
            st.write(f"Current Balance: ${account_data['balance']:,.2f}")

            # Transaction history
            st.subheader("Transaction History (Last 50)")
            cursor.execute("""
                SELECT trans_id, from_account_id, to_account_id, amount, trans_type, time_stamp
                FROM transactions
                WHERE from_account_id = %s OR to_account_id = %s
                ORDER BY time_stamp DESC
                LIMIT 50
            """, (selected_account, selected_account))
            transactions = cursor.fetchall()
            if transactions:
                st.dataframe(pd.DataFrame(transactions))
            else:
                st.info("No transactions found for this account.")

    else:
        st.info("No accounts found.")

    # Add new account
    st.subheader("Add New Account")
    with st.form("add_account_form"):
        user_id = st.number_input("User ID", min_value=1)
        branch_id = st.number_input("Branch ID", min_value=1)
        account_type = st.selectbox("Account Type", ["Savings", "Checking", "Credit"])
        balance = st.number_input("Initial Balance", min_value=0.0, format="%.2f")
        status = st.selectbox("Status", ["Active", "Inactive", "Closed"])

        submitted = st.form_submit_button("Add Account")
        if submitted:
            try:
                cursor.execute("""
                    INSERT INTO accounts (user_id, branch_id, account_type, balance, status)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, branch_id, account_type, balance, status))
                conn.commit()
                st.success("Account added successfully!")
            except Exception as e:
                st.error(f"Error adding account: {e}")

    cursor.close()
    conn.close()
