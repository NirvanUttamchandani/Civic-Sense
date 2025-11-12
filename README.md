# 🏛️ CivicVoice - Intelligent City Issue Management System

This is a full-stack web application built as a 2nd-year Database and Data Structures Lab project. It's a "Civic Sense" portal that allows citizens to report civic issues (like potholes or broken streetlights) and empowers municipal staff to manage, track, and resolve them efficiently.

The application is built with a **Streamlit** (Python) frontend and a **MySQL** database backend, connected using the `mysql.connector` library.

---

## 📸 Pages

### 1. Citizen Dashboard
Citizens get a personal dashboard showing the status of *only* their reported issues.


### 2. Staff Dashboard & Management
Staff see a global dashboard with live analytics for all issues. They can filter, manage, and update the status of any issue in the system.


### 3. Reporting a New Issue
A simple, clean form for citizens to report new issues with categories and locations populated from the database.


### 4. Authentication
Secure login and registration pages with separate roles for "Citizen" and "Staff".


---

## ✨ Key Features

* **Dual Dashboards:** Separate, tailored interfaces for "Citizen" and "Staff" roles.
* **Secure Authentication:** User registration and login system with password hashing (using Python's `hashlib`).
* **Live Analytics:** The staff dashboard features interactive charts (built with `Plotly`) showing issue statuses, category breakdowns, and issue timelines.
* **Full Accountability:** A complete `resolution_history` table logs every status change, including the staff member who made the change and the timestamp.
* **Database-Driven UI:** All dropdown menus (like categories and locations) are populated dynamically from the MySQL database.
* **Robust Backend Logic:** All database queries are handled in Python using `try...except...finally` blocks to ensure data integrity and prevent connection leaks.

---

## 🛠️ Tech Stack

* **Backend:** MySQL
* **Frontend / App Logic:** Python
* **Framework:** Streamlit
* **Core Libraries:** `mysql-connector-python`, `pandas`, `plotly`

---

## 🚀 How to Run This Project

### 1. Prerequisites
* Python 3.8+
* A running MySQL server (like XAMPP, WAMP, or MySQL Community Server).

### 2. Set Up the Database
1.  Log in to your MySQL server (e.g., in phpMyAdmin or the command line).
2.  Create a new database. The name **must be `final_dcdsl_project`** (or you must change it in the `get_db_connection` function in the code).
3.  Execute all the SQL scripts from your project to `CREATE` the 10 tables (`users`, `issues`, etc.) and `INSERT` all the sample data.

### 3. Set Up the Local Project
1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/YOUR_USERNAME/Civic-Sense.git](https://github.com/YOUR_USERNAME/Civic-Sense.git)
    cd Civic-Sense
    ```
2.  **Create a virtual environment (Recommended):**
    ```sh
    python -m venv .venv
    ```
3.  **Activate the environment:**
    * **Windows:** `.\.venv\Scripts\activate`
    * **Mac/Linux:** `source .venv/bin/activate`

4.  **Install the required libraries:**
    ```sh
    pip install -r requirements.txt
    ```
5.  **Update the database password:**
    * Open `civic_issue.py`.
    * Go to the `get_db_connection` function (around line 141).
    * Change the `password='NiRvAn_*99'` to **your own** MySQL root password.

### 4. Run the App
With your virtual environment still active, run:
```sh
streamlit run civic_issue.py
```
Open your browser to `http://localhost:8501` to see the app!

---

## 👥 Project Team

* Nihar Ranjan Mishra 
* Nikumbh Aaviraj 
* Nirvan Uttamchandani 
````http://googleusercontent.com/image_generation_content/0
