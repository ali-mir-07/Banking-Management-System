import streamlit as st
import pandas as pd
from db_connection import get_connection, get_dict_cursor

def users_module():
    st.header("Manage Users")

    conn = get_connection()
    cursor = get_dict_cursor(conn)

    # Fetch users data
    cursor.execute("SELECT user_id, full_name, cnic, e_mail, phone, address FROM users ORDER BY user_id")
    users_data = cursor.fetchall()
    users_df = pd.DataFrame(users_data, columns=["user_id", "full_name", "cnic", "e_mail", "phone", "address"])

    # Show users table
    st.subheader("All Users")
    st.dataframe(users_df)

    # Add new user form
    st.subheader("Add New User")
    with st.form(key="add_user_form"):
        new_full_name = st.text_input("Full Name")
        new_cnic = st.text_input("CNIC (Required)")
        new_email = st.text_input("Email")
        new_phone = st.text_input("Phone")
        new_address = st.text_area("Address")

        add_submitted = st.form_submit_button("Add User")

        if add_submitted:
            if not new_full_name or not new_email or not new_cnic:
                st.error("Full Name, Email, and CNIC are required!")
            else:
                try:
                    cursor.execute(
                        """
                        INSERT INTO users (full_name, cnic, e_mail, phone, address)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (new_full_name, new_cnic, new_email, new_phone, new_address)
                    )
                    conn.commit()
                    st.success("New user added successfully!")
                except Exception as e:
                    st.error(f"Error adding user: {e}")

    # Select user to update or delete
    st.subheader("Update or Delete Existing User")
    user_ids = users_df["user_id"].tolist()
    selected_user_id = st.selectbox("Select User ID", options=[None] + user_ids)

    if selected_user_id:
        user_data = users_df[users_df["user_id"] == selected_user_id].iloc[0]

        with st.form(key="edit_user_form"):
            full_name = st.text_input("Full Name", user_data["full_name"])
            cnic = st.text_input("CNIC", user_data["cnic"])
            email = st.text_input("Email", user_data["e_mail"])
            phone = st.text_input("Phone", user_data["phone"])
            address = st.text_area("Address", user_data["address"])

            update_submitted = st.form_submit_button("Update User")
            delete_submitted = st.form_submit_button("Delete User")

            if update_submitted:
                if not full_name or not email or not cnic:
                    st.error("Full Name, Email, and CNIC are required!")
                else:
                    try:
                        cursor.execute(
                            """
                            UPDATE users
                            SET full_name=%s, cnic=%s, e_mail=%s, phone=%s, address=%s
                            WHERE user_id=%s
                            """,
                            (full_name, cnic, email, phone, address, selected_user_id)
                        )
                        conn.commit()
                        st.success("User updated successfully!")
                    except Exception as e:
                        st.error(f"Error updating user: {e}")

            if delete_submitted:
                try:
                    cursor.execute("DELETE FROM users WHERE user_id=%s", (selected_user_id,))
                    conn.commit()
                    st.success("User deleted successfully!")
                    st.experimental_rerun()  # Refresh page after deletion
                except Exception as e:
                    st.error(f"Error deleting user: {e}")

    cursor.close()
    conn.close()
