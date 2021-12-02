from app import app, db
from app.models import User, InCom


# u:susan, p:cat
# u:Spawalnia, p:dupa, e: spawalnia@example.com
# migracja
# flask db stamp head
# flask db migrate
# flask db upgrade
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'RW': InCom}