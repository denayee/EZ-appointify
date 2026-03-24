import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from email.message import EmailMessage
import ssl
import smtplib
from datetime import date
import datetime

app = Flask(__name__)
now = datetime.datetime.now()


app.secret_key = "the appoinment system"

sender = "ezappointify@gmail.com"
password = "gczc aopa fhvj kjdn"

subject = "About Appointment"

em = EmailMessage()
em["From"] = sender


con = sqlite3.connect("database.db", check_same_thread=False)
cursor = con.cursor()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def homepage():
    return render_template("index.html")


@app.route("/authority_home")
def authority_home():
    return render_template("authority_home.html")


@app.route("/previous_appointments")
def previous_appointments():
    user = session["user_id"]

    appointments = cursor.execute(
        "SELECT name,office,date,time FROM appointments WHERE name = ?", (user,)
    )

    return render_template("previous_appointment.html", appointments=appointments)


@app.route("/pending")
def pending():
    officer = session["user_id"]

    pendings = cursor.execute(
        "SELECT name,email,date,time FROM appointments WHERE office = ?", (officer,)
    )

    return render_template("pending.html", pendings=pendings)


@app.route("/department")
def department():
    return render_template("department.html")


@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        office = request.form.get("office")
        name = request.form.get("name")
        email = request.form.get("email")
        # phone = request.form.get("phone")
        date = request.form.get("date")
        time = request.form.get("time")
        # today = date.today()
        # print("Today's date:", date.today())
        # print(now.time())

        due = cursor.execute(
            "SELECT * FROM appointments WHERE date = ? AND time = ? AND office = ?",
            (date, time, office),
        ).fetchone()

        if office == "" or name == "" or email == "" or date == "" or time == "":
            return render_template("apology.html", error="empty fields")
        elif due:
            return render_template("apology.html", error="Slot already booked")
        else:
            cursor.execute(
                "INSERT INTO appointments(office, name, email, date, time)VALUES(?, ?, ?, ?, ?)",
                (office, name, email, date, time),
            )
            con.commit()

            sender = "ezappointify@gmail.com"
            password = "gczc aopa fhvj kjdn"
            reciver = email

            subject = "About Appointment"
            body = f"""Your appointment for {office} of date {date} and of timing {time} is booked"""

            em = EmailMessage()
            em["From"] = sender
            em["To"] = email
            em["Subject"] = subject
            em.set_content(body)

            context = ssl.create_default_context()

            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(sender, password)
                smtp.sendmail(sender, reciver, em.as_string())

            pay = cursor.execute(
                "SELECT id FROM appointments WHERE date = ? AND time = ? AND office = ?",
                (date, time, office),
            ).fetchone()

            session["number"] = pay

            return redirect("/payment")

    else:
        return render_template("booking.html")


@app.route("/payment", methods=["GET", "POST"])
def payment():
    if request.method == "POST":
        pay_id = session["number"]

        for i in pay_id:
            cursor.execute("INSERT INTO payment (pay_id,pay) VALUES (?,?)", (i, 50))
            con.commit()

        return redirect("/previous_appointments")

    else:
        return render_template("payment.html")


@app.route("/authority_login", methods=["GET", "POST"])
def authority_login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("user_name"):
            return "no username"
        # Ensure password was submitted
        elif not request.form.get("password"):
            return "no password"

        username = request.form.get("user_name")
        password = request.form.get("password")
        office = request.form.get("office")
        auth_data = cursor.execute(
            "SELECT user_name,hash,office FROM auth_users WHERE user_name = ? AND hash = ? AND office = ?",
            (username, password, office),
        ).fetchone()

        # Ensure username exists and password is correct
        if not auth_data:
            return render_template(
                "apology.html", error="Incorrect password or Username or Category"
            )
        else:
            session["user_id"] = auth_data[2]

        # Remember which user has logged in

        # Redirect user to home page
        return redirect("/authority_home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("authority_login.html")


@app.route("/authority_register", methods=["GET", "POST"])
def authority_register():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")
        idCard = request.form.get("idCard")
        office = request.form.get("office")

        a = cursor.execute(
            "SELECT * FROM auth_users WHERE office = ?", (office,)
        ).fetchone()

        if password != confirmation:
            return render_template(
                "apology.html", error="Confirmation is not equal to password"
            )
        elif (
            user_name == ""
            or password == ""
            or confirmation == ""
            or email == ""
            or idCard == ""
            or office == ""
        ):
            return "empty fields"
        elif a:
            return render_template(
                "apology.html", error="Owner already have an account"
            )

        rows_office = cursor.execute(
            "SELECT * FROM auth_office WHERE office_name = ? AND idCard = ?",
            (office, idCard),
        ).fetchone()

        if rows_office == None:
            return render_template(
                "apology.html", error="office-name and job-id does not match"
            )

        rows_auth = cursor.execute(
            "SELECT * FROM auth_users WHERE user_name = ?", (user_name,)
        ).fetchone()

        if rows_auth == None:
            cursor.execute(
                "INSERT INTO auth_users (user_name, hash, email, office) VALUES (?, ?, ?, ?)",
                (user_name, password, email, office),
            )
            con.commit()
        else:
            return render_template("apology.html", error="Username alredy taken")

        rows_auth = cursor.execute(
            "SELECT * FROM auth_users WHERE user_name = ?", ("user_name",)
        )

        # session["user_id"] = rows[0]
        return redirect("/authority_login")
    else:
        return render_template("authority_register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("user_name"):
            return "no username"
        # Ensure password was submitted
        elif not request.form.get("password"):
            return "no password"

        username = request.form.get("user_name")
        password = request.form.get("password")
        sql_rows = cursor.execute(
            "SELECT user_name,hash FROM users WHERE user_name = ? AND hash = ?",
            (username, password),
        ).fetchone()

        # Ensure username exists and password is correct
        if not sql_rows:
            return render_template(
                "apology.html", error="Incorrect password or Username"
            )
        else:
            session["user_id"] = sql_rows[0]

        # Remember which user has logged in

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("Email")

        if password != confirmation:
            return "confirmation is not equal to password"
        elif user_name == "" or password == "" or confirmation == "" or email == "":
            return "empty fields"

        rows = cursor.execute(
            "SELECT * FROM users WHERE user_name = ?", (user_name,)
        ).fetchone()

        if rows == None:
            cursor.execute(
                "INSERT INTO users (user_name, hash, email) VALUES (?, ?, ?)",
                (user_name, password, email),
            )
            con.commit()

            sender = "ezappointify@gmail.com"
            password = "gczc aopa fhvj kjdn"
            reciver = email

            subject = "About Appointment"
            body = f"""You registered succsessfully"""

            em = EmailMessage()
            em["From"] = sender
            em["To"] = email
            em["Subject"] = subject
            em.set_content(body)

            context = ssl.create_default_context()

            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(sender, password)
                smtp.sendmail(sender, reciver, em.as_string())
        else:
            return render_template("apology.html", error="Username alredy taken")

        rows = cursor.execute("SELECT * FROM users WHERE user_name = ?", ("user_name",))

        # session["user_id"] = rows[0]
        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/cancel", methods=["GET", "POST"])
def cancel():
    if request.method == "POST":
        only_date = request.form.get("date_only")
        date = request.form.get("date")
        time = request.form.get("time")
        office = session["user_id"]

        if date == None and time == None:
            cancled = cursor.execute(
                "SELECT email FROM appointments WHERE date = ? AND office = ?",
                (only_date, office),
            ).fetchall()

            if not cancled:
                return render_template("apology.html", error="No match found")

            else:
                sender = "ezappointify@gmail.com"
                password = "gczc aopa fhvj kjdn"
                # reciver = email

                subject = "About Appointment"
                body = (
                    f"""your appointment for date {only_date} for {office} is cancled"""
                )

                for mail in cancled:
                    reciver = mail

                    em = EmailMessage()
                    em["From"] = sender
                    em["To"] = mail
                    em["Subject"] = subject
                    em.set_content(body)

                    context = ssl.create_default_context()

                    with smtplib.SMTP_SSL(
                        "smtp.gmail.com", 465, context=context
                    ) as smtp:
                        smtp.login(sender, password)
                        smtp.sendmail(sender, reciver, em.as_string())

                cursor.execute(
                    "DELETE FROM appointments WHERE date = ? AND office = ?",
                    (only_date, office),
                )
                con.commit()

                return redirect("/pending")

        else:
            cancled = cursor.execute(
                "SELECT email FROM appointments WHERE date = ? AND time = ? AND office = ?",
                (date, time, office),
            ).fetchall()

            if not cancled:
                return "no match"

            else:
                sender = "ezappointify@gmail.com"
                password = "gczc aopa fhvj kjdn"
                # reciver = email

                subject = "About Appointment"
                body = f"""your appointment for date {date} and time {time} for {office} is cancled"""

                for mail in cancled:
                    reciver = mail

                    em = EmailMessage()
                    em["From"] = sender
                    em["To"] = mail
                    em["Subject"] = subject
                    em.set_content(body)

                    context = ssl.create_default_context()

                    with smtplib.SMTP_SSL(
                        "smtp.gmail.com", 465, context=context
                    ) as smtp:
                        smtp.login(sender, password)
                        smtp.sendmail(sender, reciver, em.as_string())

                cursor.execute(
                    "DELETE FROM appointments WHERE date = ? AND time = ? AND office = ?",
                    (date, time, office),
                )
                con.commit()

                return redirect("/pending")

    else:
        return render_template("cancel.html")


@app.route("/cancel_user", methods=["GET", "POST"])
def cancel_user():
    if request.method == "POST":
        office = request.form.get("office")
        date = request.form.get("date")
        time = request.form.get("time")
        name = session["user_id"]

        cancled = cursor.execute(
            "SELECT email FROM appointments WHERE date = ? AND time = ? AND office = ? AND name = ?",
            (date, time, office, name),
        ).fetchall()

        if cancled == None:
            return render_template("apology.html", error="No match for appointment")
        else:
            sender = "ezappointify@gmail.com"
            password = "gczc aopa fhvj kjdn"

            subject = "About Appointment"
            body = f"""your appointment for date {date} and time {time} for {office} is cancled by you."""

            context = ssl.create_default_context()

            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(sender, password)

                for mail in cancled:
                    reciver = mail

                    em = EmailMessage()
                    em["From"] = sender
                    em["To"] = mail
                    em["Subject"] = subject
                    em.set_content(body)

                    smtp.sendmail(sender, reciver, em.as_string())

            cursor.execute(
                "DELETE FROM appointments WHERE date = ? AND time = ? AND office = ? AND name = ?",
                (date, time, office, name),
            )
            con.commit()

            return redirect("/previous_appointments")

    else:
        return render_template("cancel_user.html")


@app.route("/reschedule", methods=["GET", "POST"])
def reschedule():

    # use update query with replacing old data with new data and then send email

    if request.method == "POST":
        office = request.form.get("office")

        old_date = request.form.get("old_date")
        old_time = request.form.get("old_time")

        new_date = request.form.get("new_date")
        new_time = request.form.get("new_time")

        name = session["user_id"]

        old_data = cursor.execute(
            "SELECT email FROM appointments WHERE date = ? AND time = ? AND office = ? AND name = ?",
            (old_date, old_time, office, name),
        ).fetchall()

        if not old_data:
            return render_template("apology.html", error="No match for appoitment")
        else:
            data = cursor.execute(
                "SELECT * FROM appointments WHERE date = ? AND time = ? AND office = ? AND name = ?",
                (old_date, old_time, office, name),
            ).fetchone()

            email_n = data[3]
            # phone_n = data[4]

            due = cursor.execute(
                "SELECT * FROM appointments WHERE date = ? AND time = ? AND office = ?",
                (new_date, new_time, office),
            ).fetchone()

            if due:
                return "slot already booked"

            sender = "ezappointify@gmail.com"
            password = "gczc aopa fhvj kjdn"

            subject = "About Appointment"
            body = f"""your appointment for date {old_date} and time {old_time} for {office} is rescheduled to date {new_date} and time {new_time} by you."""

            context = ssl.create_default_context()

            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(sender, password)

                for mail in old_data:
                    reciver = mail

                    em = EmailMessage()
                    em["From"] = sender
                    em["To"] = mail
                    em["Subject"] = subject
                    em.set_content(body)

                    smtp.sendmail(sender, reciver, em.as_string())

            cursor.execute(
                "DELETE FROM appointments WHERE date = ? AND time = ? AND office = ? AND name = ?",
                (old_date, old_time, office, name),
            )
            con.commit()

            cursor.execute(
                "INSERT INTO appointments (office, name, email, date, time)VALUES(?, ?, ?, ?, ?)",
                (office, name, email_n, new_date, new_time),
            )
            con.commit()

            return redirect("/previous_appointments")

    else:
        return render_template("reschedule.html")


@app.route("/admin_home", methods=["GET", "POST"])
def admin_home():
    return render_template("admin_home.html")


@app.route("/users", methods=["GET", "POST"])
def users():
    if request.method == "POST":
        name = request.form.get("user_name")

        cursor.execute("DELETE FROM users WHERE user_name = ?", (name,))
        con.commit()

        return redirect("users")

    else:
        users = cursor.execute("SELECT id,user_name FROM users").fetchall()

        return render_template("users.html", users=users)


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("user_name"):
            return "no username"
        # Ensure password was submitted
        elif not request.form.get("password"):
            return "no password"

        username = request.form.get("user_name")
        password = request.form.get("password")
        sql_rows = cursor.execute(
            "SELECT user_name,hash FROM admin_users WHERE user_name = ? AND hash = ?",
            (username, password),
        ).fetchone()

        # Ensure username exists and password is correct
        if not sql_rows:
            return render_template(
                "apology.html", error="Incorrect password or Username"
            )
        else:
            session["user_id"] = sql_rows[0]

        # Remember which user has logged in

        # Redirect user to home page
        return redirect("/admin_home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("admin_login.html")


@app.route("/owners", methods=["GET", "POST"])
def owners():
    if request.method == "POST":
        name = request.form.get("user_name")

        cursor.execute("DELETE FROM auth_users WHERE user_name = ?", (name,))
        con.commit()

        return redirect("/owners")

    else:
        owners = cursor.execute("SELECT id,user_name FROM auth_users").fetchall()

        return render_template("owners.html", owners=owners)


@app.route("/job_id", methods=["GET", "POST"])
def job_id():
    job_id = cursor.execute("SELECT office_name,idCard FROM auth_office")

    return render_template("job_id.html", job_id=job_id)


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        name = request.form.get("nameR")
        email = request.form.get("mailR")
        data = request.form.get("dataR")

        cursor.execute(
            "INSERT INTO feedback (name,email,data) VALUES (?,?,?)", (name, email, data)
        )
        con.commit()

        return redirect("/")
    else:
        return render_template("feedback.html")


@app.route("/feedback_admin", methods=["GET", "POST"])
def feedback_admin():
    feeds = cursor.execute("SELECT name,email,data FROM feedback")
    return render_template("feedback_admin.html", feeds=feeds)


@app.route("/payments", methods=["GET", "POST"])
def payments():
    pays = cursor.execute("SELECT id,name FROM appointments")

    return render_template("payments.html", pays=pays)
