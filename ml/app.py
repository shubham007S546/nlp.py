import streamlit as st
import mysql.connector
import pandas as pd

# Streamlit page title
st.title("🌾 Agriculture Management System Dashboard")

# ✅ Correct MySQL Workbench Connection Details
host = "localhost"
user = "root"  # ✅ Your actual MySQL username
password = "Shubham@25"
database = "ams"

# Create a connection
try:
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    if conn.is_connected():
        st.success("✅ Connected to MySQL Workbench database")
        cursor = conn.cursor()

        # Let user select a table
        cursor.execute("SHOW TABLES;")
        tables = [table[0] for table in cursor.fetchall()]

        if tables:
            selected_table = st.selectbox("Select a table to view data", tables)

            if selected_table:
                query = f"SELECT * FROM {selected_table};"
                df = pd.read_sql(query, conn)
                st.write(f"Showing data from `{selected_table}`:")
                st.dataframe(df)
        else:
            st.warning("⚠️ No tables found in the database.")

except mysql.connector.Error as e:
    st.error(f"❌ MySQL connection failed: {e}")

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
