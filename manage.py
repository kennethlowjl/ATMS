from flask_script import Manager
from models import db
from app import app

manager = Manager(app)

@manager.command
def create_tables():
    db.create_all()

if __name__ == "__main__":
    manager.run()