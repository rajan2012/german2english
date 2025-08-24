import streamlit as st
import mysql.connector
from mysql.connector import Error
import hashlib

# ---------------- MySQL Connection ----------------
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",      # your host
            user="root",           # your DB user
            password="password",   # your DB password
            database="users" # your database name
        )
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
    return connection

# ---------------- Helper Functions ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    connection = create_connection()
    cursor = connection.cursor()
    hashed_password = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        connection.commit()
        st.success("User registered successfully!")
    except mysql.connector.Error as e:
        st.error(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

def login_user(username, password):
    connection = create_connection()
    cursor = connection.cursor()
    hashed_password = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, hashed_password))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user

# ---------------- Streamlit Interface ----------------
st.title("Login/Register Demo")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    st.subheader("Create a New Account")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    if st.button("Register"):
        if new_user and new_password:
            register_user(new_user, new_password)
        else:
            st.warning("Please provide both username and password")

elif choice == "Login":
    st.subheader("Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username and password:
            user = login_user(username, password)
            if user:
                st.success(f"Logged in as {username}")
            else:
                st.error("Invalid username or password")
        else:
            st.warning("Please provide both username and password")
