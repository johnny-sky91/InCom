from app import app, db
from app.models import User, InCom, Models, Types, Causes, DetectionAreas


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'InCom': InCom,
            'Types': Types, 'Models': Models, 'Causes': Causes, 'DetectionAreas': DetectionAreas}
