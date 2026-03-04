from flask import Flask, render_template, request, redirect, session
import mysql.connector
import time
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- DATABASE CONNECTION ----------------
def get_db_connection():
   while True:
        try:
            conn = mysql.connector.connect(
                host="mysql",
                user="root",
                password="root",
                database="student_db"
            )
            return conn
        except mysql.connector.Error:
            time.sleep(2)  # Wait before retrying
    


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        role = "student"

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, password, role)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect("/admin")
            else:
                return redirect("/dashboard")
        else:
            return "invalid credentials"

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- STUDENT DASHBOARD ----------------
@app.route("/dashboard")
def student_dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM applications WHERE user_id = %s",
        (session["user_id"],)
    )

    applications = cursor.fetchall()

    conn.close()

    return render_template(
        "student_dashboard.html",
        name=session["name"],
        applications=applications
    )

# ---------------- APPLY ----------------
@app.route("/apply", methods=["POST"])
def apply():
    if "user_id" not in session:
        return redirect("/login")

    course = request.form["course"]
    statement = request.form["statement"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO applications (user_id, course, statement, status) VALUES (%s, %s, %s, %s)",
        (session["user_id"], course, statement, "Pending")
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/dashboard")


# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
def admin_dashboard():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Statistics
    cursor.execute("SELECT COUNT(*) AS total FROM applications")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS pending FROM applications WHERE status='Pending'")
    pending = cursor.fetchone()["pending"]

    cursor.execute("SELECT COUNT(*) AS approved FROM applications WHERE status='Approved'")
    approved = cursor.fetchone()["approved"]

    cursor.execute("SELECT COUNT(*) AS rejected FROM applications WHERE status='Rejected'")
    rejected = cursor.fetchone()["rejected"]

    # Applications with student name
    cursor.execute("""
        SELECT applications.*, users.name AS student_name
        FROM applications
        JOIN users ON applications.user_id = users.id
    """)
    applications = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        name=session["name"],
        total=total,
        pending=pending,
        approved=approved,
        rejected=rejected,
        applications=applications
    )


# ---------------- APPROVE ----------------
@app.route("/update_status/<int:app_id>/<string:status>")
def update_status(app_id, status):

    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE applications SET status = %s WHERE id = %s",
        (status, app_id)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route("/approve/<int:id>")
def approve(id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE applications SET status='Approved' WHERE id=%s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin")


# ---------------- REJECT ----------------
@app.route("/reject/<int:id>")
def reject(id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE applications SET status='Rejected' WHERE id=%s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)