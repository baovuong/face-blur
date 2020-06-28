from app import db

if __name__ == '__main__':
    db.session.create_all()