from app import app, db, Admin
from werkzeug.security import generate_password_hash

username = 'admin'
password = 'admin'

#hashed_password = generate_password_hash(password)

admin = Admin(username=username, password=password)

# Add the admin user to the database
with app.app_context():
    db.create_all()
    db.session.add(admin)
    db.session.commit()

print("Admin user created successfully.")
print(username)
print(password)
