import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from tasks import create_app, db
from tasks.models import Task


env_name = os.getenv('FLASK_ENV')
app = create_app()

migrate = Migrate(app=app, db=db)

manager = Manager(app=app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
