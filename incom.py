from app import app, db
from app.models import User, Post


# u:susan, p:cat
# u:Spawalnia, p:dupa, e: spawalnia@example.com
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
