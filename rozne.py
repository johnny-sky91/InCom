from app.models import InCom, User
from app import app, db


def dupa():
    zgloszenia = InCom.query.order_by(InCom.id.desc()).all()
    for zgloszenie in zgloszenia:
        print(User.query.filter_by(id=zgloszenie.user_id).first().username)


print(dupa())
