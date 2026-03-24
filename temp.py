import sqlite3

con = sqlite3.connect("database.db")
cursor = con.cursor()

#cursor.execute("CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_name TEXT NOT NULL, hash TEXT NOT NULL, phone INTEGER(10) NOT NULL)")
#cursor.execute("CREATE TABLE auth_users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_name TEXT NOT NULL, hash TEXT NOT NULL, phone INTEGER(10) NOT NULL, office text NOT NULL)")
#cursor.execute("CREATE TABLE auth_office (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, office_name TEXT NOT NULL, idCard INTEGER(3) NOT NULL)")
# cursor.execute("CREATE TABLE admin_users(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_name TEXT NOT NULL, hash TEXT NOT NULL)")

# cursor.execute("INSERT INTO auth_office (office_name, idCard) VALUES ('Star Auto Service', 112),('Go mechanic', 113),('Cars24', 114), ('Shah Associate-Legal Service', 212), ('Alka Shah Advocate', 213), ('Jagdishwar Mishra', 214), ('Om Radiology',312), ('Oroscan', 313), ('Ravi Sono X-ray clinic', 314), ('Unicorm Events', 412),('Divine Event', 413),('Koncept Events', 414), ('Honest', 512),('Rangoli', 513),('Mango', 514), ('Fine hair art', 612),('Bobby hair salon', 613),('Teletop hair style', 614)")
# con.commit()
# cursor.execute("INSERT INTO admin_users (user_name, hash) VALUES ('admin', 'admin')")
# con.commit()

#cursor.execute("CREATE TABLE appointments (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, office TEXT NOT NULL, name TEXT NOT NULL, email TEXT NOT NULL, phone INTEGER(10) NOT NULL, date TEXT NOT NULL, time TEXT NOT NULL)")

# cursor.execute("DROP TABLE feedback")
# con.commit()

# rows = cursor.execute("SELECT * FROM feedback")
# for i in rows:
#         print(i)

# cursor.execute("DELETE FROM payment")
# con.commit()
# cursor.execute("CREATE TABLE payment(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, pay_id INTEGER NOT NULL, pay INTEGER NOT NULL, FOREIGN KEY (pay_id) REFERENCES appointments(id))")
# con.commit()

# cursor.execute("CREATE TABLE feedback(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT NOT NULL, email TEXT NOT NULL, data TEXT NOT NULL)")
# con.commit()

# cursor.execute("ALTER TABLE auth_users ADD email TEXT NOT NULL")
# con.commit()

# cursor.execute("DELETE FROM auth_users")
# con.commit()
cursor.execute("ALTER TABLE appointments DROP COLUMN phone")
con.commit()
