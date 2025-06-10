import streamlit as st
from db_connection import get_connection, get_dict_cursor
import pandas as pd

def branch_module():
    st.header("Branches Management")

    conn = get_connection()
    cursor = get_dict_cursor(conn)

    # Load all branches
    cursor.execute("SELECT * FROM branch ORDER BY branch_id")
    branches = cursor.fetchall()
    df = pd.DataFrame(branches)

    if not df.empty:
        st.dataframe(df)

        # Select branch for update/delete
        branch_ids = df['branch_id'].tolist()
        selected_branch = st.selectbox("Select Branch ID to Update/Delete", branch_ids)

        if selected_branch:
            branch_data = df[df['branch_id'] == selected_branch].iloc[0]

            with st.form("update_branch_form"):
                branch_name = st.text_input("Branch Name", branch_data['branch_name'])
                branch_code = st.text_input("Branch Code", branch_data['branch_code'])
                address = st.text_area("Address", branch_data['address'])
                phone = st.text_input("Phone", branch_data['phone'])

                submitted = st.form_submit_button("Update Branch")
                if submitted:
                    try:
                        cursor.execute("""
                            UPDATE branch 
                            SET branch_name=%s, branch_code=%s, address=%s, phone=%s
                            WHERE branch_id=%s
                        """, (branch_name, branch_code, address, phone, selected_branch))
                        conn.commit()
                        st.success("Branch updated successfully!")
                    except Exception as e:
                        st.error(f"Error updating branch: {e}")

            if st.button("Delete Branch"):
                try:
                    cursor.execute("DELETE FROM branch WHERE branch_id=%s", (selected_branch,))
                    conn.commit()
                    st.success("Branch deleted successfully!")
                except Exception as e:
                    st.error(f"Error deleting branch: {e}")
    else:
        st.info("No branches found.")

    # Add new branch
    st.subheader("Add New Branch")
    with st.form("add_branch_form"):
        branch_name = st.text_input("Branch Name")
        branch_code = st.text_input("Branch Code")
        address = st.text_area("Address")
        phone = st.text_input("Phone")

        submitted = st.form_submit_button("Add Branch")
        if submitted:
            try:
                cursor.execute("""
                    INSERT INTO branch (branch_name, branch_code, address, phone)
                    VALUES (%s, %s, %s, %s)
                """, (branch_name, branch_code, address, phone))
                conn.commit()
                st.success("Branch added successfully!")
            except Exception as e:
                st.error(f"Error adding branch: {e}")

    cursor.close()
    conn.close()
