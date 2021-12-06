from app.models import InCom, User, Types, Models, Causes
from app import app, db


def dupa():
    zgloszenia = Types.query.with_entities(Types.product_type)
    out = [item for t in zgloszenia for item in t]
    print(out)


# dupa()

def zmiana(id_do_zmiany):
    do_zmiany = InCom.query.filter_by(id=id_do_zmiany).first()
    print(do_zmiany.registration_status)
    # do_zmiany.registration_status = 'ZAKOŃCZONE'
    # db.session.commit()

zmiana(15)


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

# for x in lista_przyczyny:
#     dodaj_roznie(x)
