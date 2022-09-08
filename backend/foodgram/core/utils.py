import io

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def merge_fields(jdata):
    ids = {}
    result = []
    for data in jdata:
        if data['id'] not in ids:
            ids[data['id']] = data['amount']
        else:
            ids[data['id']] += data['amount']
    for data in jdata:
        if data['id'] in ids:
            data['amount'] = ids[data['id']]
            result.append(data)
            ids.pop(data['id'])
    return result


def pdf_buffer(jdata):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    pdfmetrics.registerFont(TTFont('DejaVuSerif-Italic',
                            'DejaVuSerif-Italic.ttf', 'UTF-8'))
    pdfmetrics.registerFont(TTFont('DejaVuSerif-BoldItalic',
                            'DejaVuSerif-BoldItalic.ttf', 'UTF-8'))
    c.setFont('DejaVuSerif-BoldItalic', 18)
    c.drawCentredString(220, 780, 'Список покупок.')
    c.setFont('DejaVuSerif-Italic', 12)
    y = 720
    d = 15
    for ing in merge_fields(jdata):
        c.drawString(40, y, (f'- {ing["name"]} ({ing["measurement_unit"]})'
                     f' - {ing["amount"]}'))
        y += d
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
