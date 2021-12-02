from app.models import InCom
from app import app, db


def dupa():
    cyce = InCom.query(id).all
    return cyce


print(dupa())
