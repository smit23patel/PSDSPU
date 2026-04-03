from app import app, db, seed_data

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_data()
    app.run()
