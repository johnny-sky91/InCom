from app.models import InCom, User, Types, Models, Causes, DetectionAreas
from app import app, db
from datetime import timezone


def delete_users():
    User.query.delete()
    db.session.commit()


def delete_incom():
    InCom.query.delete()
    db.session.commit()


def delete_areas():
    DetectionAreas.query.delete()
    db.session.commit()


delete_users()


def bezposrednio_baza():
    import sqlite3
    sqlite3.connect('app.db')
    conn = sqlite3.connect('app.db')
    "ALTER TABLE table_name RENAME COLUMN current_name TO new_name;"

    sql = "ALTER TABLE in_com RENAME COLUMN registration_status TO complaint_status;"
    cur = conn.cursor()
    cur.execute(sql)


def dodaj_roznie(do_dodania):
    incom = Causes(cause_type=do_dodania)
    db.session.add(incom)
    db.session.commit()


lista_model = ['PP001', 'PP002', 'PP002D', 'VERTICALE', 'P82', 'P64', 'PS001', 'PS002', 'PS003', 'PS004', 'PB001',
               '2D', '3D', 'P302', 'P305', 'P102', 'INNE']
lista = ['BRAMA SAMONOŚNA', 'BRAMA UCHYLNA', 'FURTKA', 'PRZĘSŁO', 'SŁUP', 'INNE']

lista_przyczyny = ['USZKODZENIE - POWŁOKA LAKIERNICZA', 'USZKODZENIE - KONSTRUKCJA',
                   'USZKODZENIE - WYPEŁNIENIE', 'USZKODZENIE - AKCESORIA', 'USZKODZENIE - POZOSTAŁE', 'WADA - MATERIAŁ',
                   'WADA - POWŁOKA LAKIERNICZA', 'WADA - POZOSTAŁE', 'BŁĘDY - SPAWANIE', 'BŁĘDY - LASER',
                   'BŁĘDY - PIŁA',
                   'BŁĘDY - GUMOWANIE', 'BŁĘDY - POZOSTAŁE', 'BRAKI']
