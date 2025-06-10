import streamlit as st
import pandas as pd
from db_connection import get_connection, get_dict_cursor

def transactions_module():
    st.header("All Transactions (Latest 100)")

    conn = get_connection()
    cursor = get_dict_cursor(conn)

    # Show latest 100 transactions
    cursor.execute("""
        SELECT trans_id, from_account_id, to_account_id, amount, trans_type, time_stamp
        FROM transactions
        ORDER BY time_stamp DESC
        LIMIT 100
    """)
    rows = cursor.fetchall()
    if rows:
        df = pd.DataFrame(rows)  # <-- just create DataFrame from dicts directly
        st.dataframe(df)
    else:
        st.info("No transactions found.")

    st.markdown("---")
    st.header("Filter Transactions by Account ID")

    account_id_filter = st.text_input("Enter Account ID to filter transactions:")

    if account_id_filter.strip().isdigit():
        account_id = int(account_id_filter.strip())
        cursor.execute("""
            SELECT trans_id, from_account_id, to_account_id, amount, trans_type, time_stamp
            FROM transactions
            WHERE from_account_id = %s OR to_account_id = %s
            ORDER BY time_stamp DESC
            LIMIT 200
        """, (account_id, account_id))

        filtered_rows = cursor.fetchall()
        if filtered_rows:
            df_filtered = pd.DataFrame(filtered_rows)  # <-- same here
            st.dataframe(df_filtered)
            st.markdown(f"**Total transactions involving account {account_id}: {len(df_filtered)}**")
        else:
            st.info(f"No transactions found for account ID {account_id}.")
    elif account_id_filter.strip():
        st.warning("Please enter a valid numeric Account ID.")

    cursor.close()
    conn.close()
