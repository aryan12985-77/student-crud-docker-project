from flask import Flask, render_template, request, redirect
from config import get_db_connection

app = Flask(__name__)

# ======================
# READ (Display Students)
# ======================
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', students=students)


# ======================
# CREATE (Add Student)
# ======================
@app.route('/add', methods=['POST'])
def add_student():
    name = request.form['name']
    email = request.form['email']
    course = request.form['course']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, email, course) VALUES (%s, %s, %s)",
        (name, email, course)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/')


# ======================
# DELETE (Remove Student)
# ======================
@app.route('/delete/<int:id>')
def delete_student(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/')


# ======================
# UPDATE (Edit Student)
# ======================
@app.route('/update/<int:id>', methods=['POST'])
def update_student(id):
    name = request.form['name']
    email = request.form['email']
    course = request.form['course']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE students SET name=%s, email=%s, course=%s WHERE id=%s",
        (name, email, course, id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/')


# Run Flask App
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)