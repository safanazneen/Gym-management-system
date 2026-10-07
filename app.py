from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3

app = Flask(__name__)

DATABASE = "gym.db"


# ---------------- DATABASE ----------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            membership TEXT NOT NULL,
            join_date TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (member_id) REFERENCES members(id)
        )
    """)

    conn.commit()
    conn.close()


# ---------------- HTML ----------------

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Gym Management System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background: #f4f4f4;
        }

        h1 {
            color: #222;
        }

        form {
            background: white;
            padding: 20px;
            margin-bottom: 25px;
            border-radius: 10px;
        }

        input, select, button {
            padding: 10px;
            margin: 5px;
        }

        button {
            background: #222;
            color: white;
            border: none;
            cursor: pointer;
        }

        table {
            width: 100%;
            background: white;
            border-collapse: collapse;
        }

        th, td {
            padding: 12px;
            border: 1px solid #ddd;
            text-align: left;
        }

        th {
            background: #222;
            color: white;
        }

        a {
            color: blue;
        }
    </style>
</head>

<body>

<h1>🏋️ Gym Management System</h1>

<h2>Add Member</h2>

<form method="POST" action="/add_member">

    <input type="text" name="name" placeholder="Name" required>

    <input type="number" name="age" placeholder="Age" required>

    <select name="gender" required>
        <option value="">Gender</option>
        <option value="Male">Male</option>
        <option value="Female">Female</option>
        <option value="Other">Other</option>
    </select>

    <input type="text" name="phone" placeholder="Phone" required>

    <input type="email" name="email" placeholder="Email">

    <select name="membership" required>
        <option value="">Membership</option>
        <option value="Monthly">Monthly</option>
        <option value="Quarterly">Quarterly</option>
        <option value="Yearly">Yearly</option>
    </select>

    <input type="date" name="join_date" required>

    <button type="submit">Add Member</button>

</form>


<h2>Members</h2>

<table>

<tr>
    <th>ID</th>
    <th>Name</th>
    <th>Age</th>
    <th>Gender</th>
    <th>Phone</th>
    <th>Email</th>
    <th>Membership</th>
    <th>Join Date</th>
</tr>

{% for member in members %}

<tr>
    <td>{{ member["id"] }}</td>
    <td>{{ member["name"] }}</td>
    <td>{{ member["age"] }}</td>
    <td>{{ member["gender"] }}</td>
    <td>{{ member["phone"] }}</td>
    <td>{{ member["email"] or "-" }}</td>
    <td>{{ member["membership"] }}</td>
    <td>{{ member["join_date"] }}</td>
</tr>

{% else %}

<tr>
    <td colspan="8">No members added yet.</td>
</tr>

{% endfor %}

</table>


<h2>Add Payment</h2>

<form method="POST" action="/add_payment">

    <select name="member_id" required>

        <option value="">Select Member</option>

        {% for member in members %}
            <option value="{{ member['id'] }}">
                {{ member['name'] }}
            </option>
        {% endfor %}

    </select>

    <input type="number"
           name="amount"
           step="0.01"
           placeholder="Amount"
           required>

    <input type="date"
           name="payment_date"
           required>

    <select name="status" required>
        <option value="Paid">Paid</option>
        <option value="Pending">Pending</option>
    </select>

    <button type="submit">Add Payment</button>

</form>


<h2>Payments</h2>

<table>

<tr>
    <th>ID</th>
    <th>Member</th>
    <th>Amount</th>
    <th>Date</th>
    <th>Status</th>
</tr>

{% for payment in payments %}

<tr>
    <td>{{ payment["id"] }}</td>
    <td>{{ payment["member_name"] }}</td>
    <td>₹{{ payment["amount"] }}</td>
    <td>{{ payment["payment_date"] }}</td>
    <td>{{ payment["status"] }}</td>
</tr>

{% else %}

<tr>
    <td colspan="5">No payments added yet.</td>
</tr>

{% endfor %}

</table>

</body>
</html>
"""


# ---------------- HOME ----------------

@app.route("/")
def home():

    conn = get_db_connection()

    members = conn.execute(
        "SELECT * FROM members ORDER BY id DESC"
    ).fetchall()

    payments = conn.execute("""
        SELECT payments.*,
               members.name AS member_name
        FROM payments
        JOIN members
        ON payments.member_id = members.id
        ORDER BY payments.id DESC
    """).fetchall()

    conn.close()

    return render_template_string(
        HTML,
        members=members,
        payments=payments
    )


# ---------------- ADD MEMBER ----------------

@app.route("/add_member", methods=["POST"])
def add_member():

    name = request.form["name"]
    age = request.form["age"]
    gender = request.form["gender"]
    phone = request.form["phone"]
    email = request.form.get("email", "")
    membership = request.form["membership"]
    join_date = request.form["join_date"]

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO members
        (name, age, gender, phone, email, membership, join_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        age,
        gender,
        phone,
        email,
        membership,
        join_date
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# ---------------- ADD PAYMENT ----------------

@app.route("/add_payment", methods=["POST"])
def add_payment():

    member_id = request.form["member_id"]
    amount = request.form["amount"]
    payment_date = request.form["payment_date"]
    status = request.form["status"]

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO payments
        (member_id, amount, payment_date, status)
        VALUES (?, ?, ?, ?)
    """, (
        member_id,
        amount,
        payment_date,
        status
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# ---------------- START APP ----------------

if __name__ == "__main__":

    create_database()

    print("Database created successfully!")
    print("Starting Gym Management System...")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )