from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime, timezone

from app.models import InCom, User, Types, Models, Causes
from app import app, db

ic_id = 1
order_number = '12345'
detection_area = 'Piła'
product_type = 'FURTKA'
model = 'P82'
cause = 'WADA - MATERIAŁ'
description = 'Testy testy testy'
username = 'SPAWALNIA'
date = '12/20/2021'

# print(data)
id_do_raportu = 21
do_raportu = InCom.query.filter_by(id=id_do_raportu).first()
data = do_raportu.timestamp
print(data)


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%Y-%m-%d %H:%M:%S')


print(utc_to_local(data))


def create_pdf(id_to_report):
    report_query = InCom.query.filter_by(id=id_to_report).first()
    data = {
        'ID ZGŁOSZENIA': id_to_report,
        'NUMER ZLECENIA': report_query.order_number,
        'DATA ZGŁOSZENIA': report_query.timestamp,
        'ZGŁASZAJĄCY': report_query.user_id,
        'OBSZAR WYKRYCIA': report_query.detection_area,
        'RODZAJ': report_query.product_type,
        'MODEL': report_query.model,
        'PRZYCZYNA': report_query.cause,
        'OPIS': report_query.description,

    }
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    report = canvas.Canvas(f"reports/RW_{id_to_report}.pdf")
    report.setFont('Arial', 12)
    report.drawString(150, 800, f'REKLAMACJA WEWNĘTRZNA')
    for i, key in enumerate(data):
        report.drawString(50, 780 - (i * 20), f'{key}: {data[key]}')
    report.save()
