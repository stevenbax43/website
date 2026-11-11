import numpy as np
import math

from django.http import HttpResponse

import base64
from io import BytesIO
from datetime import datetime

from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
def CO2verloop(request):

    CO2_list = {}
    lst_C_t = []
    lst_C_t_o = []

    if request.method == "POST":

        # Invoer
        ruimteinhoud = float(request.POST.get("volume_room", 0))
        ventilation_mode = request.POST.get(
            "ventilation_mode",
            "pp"
        )

        ventilation_value = float(
            request.POST.get(
                "ventilation_value",
                0
            )
        )

        CO2productie_pp = float(request.POST.get("production_pp", 0))
        aantal_personen = float(request.POST.get("number_persons", 0))

        bezetting = float(request.POST.get("bezetting", 100))
        buitenluchtkwaliteit = float(request.POST.get("outsite_air_ppm", 400))

        beginconcentratie = float(request.POST.get("start_ppm", 400))

        # Conversies
        CO2_productie_pp_unit = CO2productie_pp / 1000 / 3600      # m³/s per persoon
        if ventilation_mode == "pp":

            ventilatiedebiet_totaal = (
                ventilation_value *
                aantal_personen
            )

            ventilatie_pp = ventilation_value
            resultaat_ventilatie = (
                f"{round(ventilatiedebiet_totaal,0)} m³/h"
            )

            resultaat_ventilatie_naam = (
                "Ventilatiedebiet totaal"
            )
        else:

            ventilatiedebiet_totaal = (
                ventilation_value
            )

            ventilatie_pp = (
                ventilatiedebiet_totaal /
                aantal_personen
                if aantal_personen > 0
                else 0
            )
            resultaat_ventilatie = (
                f"{round(ventilatie_pp,1)} m³/h.p"
            )

            resultaat_ventilatie_naam = (
                "Ventilatie per persoon"
            )
        Ventilatie_hoeveelheid = (
            ventilatiedebiet_totaal /
            3600
        )
        CO2_productie_unit = (
            CO2_productie_pp_unit
            * bezetting / 100
            * aantal_personen
        )                                                         # m³/s

        # Beveiliging
        if ruimteinhoud <= 0 or Ventilatie_hoeveelheid <= 0:
            return [{
                "x_values": [],
                "C_t_curve": [],
                "C_t_o_curve": []
            }]

        # Stationaire concentratie
        C_stationair = (
            (CO2_productie_unit * 1e6) / Ventilatie_hoeveelheid
            + buitenluchtkwaliteit
        )

        # 99% punt bepalen
        target = beginconcentratie + 0.99 * (
            C_stationair - beginconcentratie
        )

        t_sec = 0

        while True:

            C_t = (
                (CO2_productie_unit * 1e6) / Ventilatie_hoeveelheid
                + buitenluchtkwaliteit
                - (
                    (CO2_productie_unit * 1e6) / Ventilatie_hoeveelheid
                    - beginconcentratie
                    + buitenluchtkwaliteit
                )
                * np.exp(
                    -Ventilatie_hoeveelheid
                    / ruimteinhoud
                    * t_sec
                )
            )

            if C_t >= target:
                break

            t_sec += 60  # stappen van 1 minuut
        
        # Grafiek 1 uur langer laten doorlopen
        tijd = t_sec / 3600 + 1

        # Afronden naar boven op stappen van 0,2 uur
        tijd = math.ceil(tijd / 0.2) * 0.2

        # Altijd circa 200 punten
        n_points = 201
        lst = np.linspace(0, tijd, n_points)

        # Grafiekdata
        for item in lst:

            item_sec = item * 3600

            C_t = (
                (CO2_productie_unit * 1e6) / Ventilatie_hoeveelheid
                + buitenluchtkwaliteit
                - (
                    (CO2_productie_unit * 1e6) / Ventilatie_hoeveelheid
                    - beginconcentratie
                    + buitenluchtkwaliteit
                )
                * np.exp(
                    -Ventilatie_hoeveelheid
                    / ruimteinhoud
                    * item_sec
                )
            )

            lst_C_t.append(round(C_t))
            lst_C_t_o.append(round(C_t - beginconcentratie))

        CO2_list = {
            "x_values": [round(x, 3) for x in lst.tolist()],
            "C_t_curve": lst_C_t,
            "C_t_o_curve": lst_C_t_o,
            "C_stationair": round(C_stationair),
            "tijd_einde": round(tijd, 2),

            "ventilatie_pp": round(ventilatie_pp, 1),
            "ventilatiedebiet_totaal": round(ventilatiedebiet_totaal, 1),
            "ventilation_mode": ventilation_mode,
            "resultaat_ventilatie": resultaat_ventilatie,
            "resultaat_ventilatie_naam": resultaat_ventilatie_naam, 
        }

    return [CO2_list]

def generate_pdf_CO2(request):

    if request.method != "POST":
        return HttpResponse("Invalid request", status=400)

    # =====================================================
    # INPUTS
    # =====================================================

    volume_room = request.POST.get("volume_room", "")
    start_ppm = request.POST.get("start_ppm", "")

    number_persons = request.POST.get("number_persons", "")
    bezetting = request.POST.get("bezetting", "")
    production_pp = request.POST.get("production_pp", "")

    ventilation_mode = request.POST.get(
        "ventilation_mode",
        "pp"
    )

    ventilation_value = request.POST.get(
        "ventilation_value",
        ""
    )
    outsite_air_ppm = request.POST.get("outsite_air_ppm", "")

    chart_b64 = request.POST.get("chart_image_base64")

    max_concentration = request.POST.get("max_concentration", "")
    max_increase = request.POST.get("max_increase", "")
    time_to_max = request.POST.get("time_to_max", "")
    project_name = request.POST.get("project_name", "").strip()[:80]
    project_number = request.POST.get("project_number", "").strip()[:40]
    room_name = request.POST.get("room_name", "").strip()[:80]
    room_number = request.POST.get("room_number", "").strip()[:40]

    stamp = datetime.now().strftime("%d-%m-%Y %H:%M")

    # =====================================================
    # PDF SETUP
    # =====================================================

    buffer = BytesIO()

    c = canvas.Canvas(buffer, pagesize=A4)

    page_width, page_height = A4

    margin = 25

    # =====================================================
    # HELPERS
    # =====================================================

    def draw_card(x, y, w, h, header, header_color):

        c.setFillColor(colors.white)

        c.roundRect(
            x,
            y,
            w,
            h,
            8,
            fill=1,
            stroke=0
        )

        c.setFillColor(header_color)

        c.roundRect(
            x,
            y + h - 24,
            w,
            24,
            8,
            fill=1,
            stroke=0
        )

        c.rect(
            x,
            y + h - 24,
            w,
            12,
            fill=1,
            stroke=0
        )

        c.setFillColor(colors.black)

        c.roundRect(
            x,
            y,
            w,
            h,
            8,
            fill=0,
            stroke=1
        )

        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x + 10, y + h - 16, header)

    # =====================================================
    # TITEL
    # =====================================================

    c.setFont("Helvetica-Bold", 18)

    c.drawString(
        margin,
        page_height - 35,
        "Tool W4 - CO2-verloop"
    )

    c.setStrokeColor(colors.HexColor("#3DAB39"))
    c.setLineWidth(2)

    c.line(
        margin,
        page_height - 45,
        page_width - margin,
        page_height - 45
    )

    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)

    c.drawRightString(
        page_width - margin,
        page_height - 32,
        stamp
    )

    c.setFillColor(colors.black)

    def draw_metadata(y, label, value):
        prefix = f"{label}:"
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin, y, prefix)
        value_x = margin + stringWidth(f"{prefix} ", "Helvetica-Bold", 9)
        available_width = page_width - margin - value_x
        c.setFont("Helvetica", 12)
        displayed_value = value or "-"
        original_value = displayed_value
        while displayed_value and stringWidth(displayed_value, "Helvetica", 12) > available_width:
            displayed_value = displayed_value[:-1]
        if displayed_value != original_value:
            while displayed_value and stringWidth(f"{displayed_value}...", "Helvetica", 12) > available_width:
                displayed_value = displayed_value[:-1]
            displayed_value += "..."
        c.drawString(value_x, y - 1, displayed_value)

    for index, (label, value) in enumerate((
        ("Projectnaam", project_name),
        ("Projectnummer", project_number),
        ("Ruimtenaam", room_name),
        ("Ruimtenummer", room_number),
    )):
        draw_metadata(page_height - 62 - index * 18, label, value)
    # =====================================================
    # Input TITEL
    # =====================================================

    c.setFont("Helvetica-Bold", 12)

    c.drawString(
        25,
        page_height - 265,
        "Input"
    )

    c.setStrokeColor(colors.HexColor("#E0E0E0"))

    c.line(
        110,
        page_height - 262,
        page_width - 25,
        page_height - 262
    )
    # =====================================================
    # INPUT CARDS
    # =====================================================

    card_y = page_height - 240
    card_h = 110
    card_w = 165

    # -----------------------------------------------------
    # RUIMTE
    # -----------------------------------------------------

    draw_card(
        25,
        card_y,
        card_w,
        card_h,
        "Ruimte",
        colors.HexColor("#DCEBFF")
    )

    c.setFont("Helvetica", 9)

    c.drawString(35, card_y + 60, "Ruimte-inhoud")
    c.drawRightString(180, card_y + 60, f"{volume_room} m3")

    c.drawString(35, card_y + 35, "Beginconcentratie")
    c.drawRightString(180, card_y + 35, f"{start_ppm} ppm")

    # -----------------------------------------------------
    # BEZETTING
    # -----------------------------------------------------

    draw_card(
        215,
        card_y,
        card_w,
        card_h,
        "Bezetting",
        colors.HexColor("#DFF3E3")
    )

    c.drawString(225, card_y + 60, "Aantal personen")
    c.drawRightString(370, card_y + 60, str(number_persons))

    c.drawString(225, card_y + 35, "Bezetting")
    c.drawRightString(370, card_y + 35, f"{bezetting}%")

    c.drawString(225, card_y + 10, "Activiteit")

    activiteit = production_pp[:25]

    c.drawRightString(
        370,
        card_y + 10,
        activiteit
    )

    # -----------------------------------------------------
    # VENTILATIE
    # -----------------------------------------------------

    draw_card(
        405,
        card_y,
        card_w,
        card_h,
        "Ventilatie",
        colors.HexColor("#DDF6FF")
    )

    if ventilation_mode == "pp":

        label = "Debiet per persoon"
        value = f"{ventilation_value} m³/h.p"

    else:

        label = "Debiet totaal"
        value = f"{ventilation_value} m³/h"

    c.drawString(
        415,
        card_y + 60,
        label
    )

    c.drawRightString(
        560,
        card_y + 60,
        value
    )

    c.drawString(415, card_y + 35, "Buitenlucht")

    c.drawRightString(
        560,
        card_y + 35,
        f"{outsite_air_ppm} ppm"
    )
    # =====================================================
    # RESULTATEN TITEL
    # =====================================================

    c.setFont("Helvetica-Bold", 12)

    c.drawString(
        25,
        page_height - 265,
        "Resultaten"
    )

    c.setStrokeColor(colors.HexColor("#E0E0E0"))

    c.line(
        110,
        page_height - 262,
        page_width - 25,
        page_height - 262
    )
    # =====================================================
    # KPI CARDS
    # =====================================================

    result_y = page_height - 390
    result_h = 70
    result_gap = 10
    result_w = (page_width - 2 * margin - 3 * result_gap) / 4

    def draw_result_card(
            x,
            value,
            title,
            fillcolor,
            textcolor):

        c.setFillColor(fillcolor)

        c.roundRect(
            x,
            result_y,
            result_w,
            result_h,
            10,
            fill=1,
            stroke=0
        )

        c.setFillColor(textcolor)

        value_font_size = 14
        value_width = stringWidth(value, "Helvetica-Bold", value_font_size)
        if value_width > result_w - 12:
            value_font_size *= (result_w - 12) / value_width
        c.setFont("Helvetica-Bold", value_font_size)

        c.drawCentredString(
            x + result_w / 2,
            result_y + 40,
            value
        )

        c.setFont("Helvetica", 9)

        c.drawCentredString(
            x + result_w / 2,
            result_y + 18,
            title
        )

    draw_result_card(
        margin,
        f"{max_concentration} ppm",
        "Maximale concentratie",
        colors.HexColor("#FFE8ED"),
        colors.HexColor("#FF6384")
    )

    draw_result_card(
        margin + result_w + result_gap,
        f"+{max_increase} ppm",
        "Maximale verhoging",
        colors.HexColor("#E8F4FF"),
        colors.HexColor("#36A2EB")
    )

    draw_result_card(
        margin + 2 * (result_w + result_gap),
        time_to_max,
        "Tijd tot maximum",
        colors.HexColor("#E8F8EB"),
        colors.HexColor("#3DAB39")
    )

    ventilation_value_number = float(ventilation_value or 0)
    number_persons_value = float(number_persons or 0)
    if ventilation_mode == "pp":
        ventilation_result_label = "Ventilatiedebiet totaal"
        ventilation_result_value = (
            f"{ventilation_value_number * number_persons_value:.0f} m³/h"
        )
    else:
        ventilation_result_label = "Ventilatie per persoon"
        ventilation_per_person = (
            ventilation_value_number / number_persons_value
            if number_persons_value > 0
            else 0
        )
        ventilation_result_value = f"{ventilation_per_person:.1f} m³/h.p"

    draw_result_card(
        margin + 3 * (result_w + result_gap),
        ventilation_result_value,
        ventilation_result_label,
        colors.HexColor("#E0F7FA"),
        colors.HexColor("#26A69A")
    )

    # =====================================================
    # GRAFIEK
    # =====================================================

    # =====================================================
    # RESULTATEN TITEL
    # =====================================================

    c.setFont("Helvetica-Bold", 12)

    c.drawString(
        25,
        page_height - 265,
        "Grafiek CO2-concentratie over de tijd"
    )

    c.setStrokeColor(colors.HexColor("#E0E0E0"))

    c.line(
        110,
        page_height - 262,
        page_width - 25,
        page_height - 262
    )
   
    if chart_b64:

        try:

            img_data = base64.b64decode(chart_b64)

            img = ImageReader(
                BytesIO(img_data)
            )

            c.roundRect(
                20,
                40,
                page_width - 40,
                300,
                8,
                fill=0,
                stroke=1
            )

            c.drawImage(
                img,
                25,
                45,
                width=page_width - 50,
                height=290,
                preserveAspectRatio=True,
                mask='auto'
            )

        except Exception as e:
            print(e)

    # =====================================================
    # VOETTEKST
    # =====================================================

    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)

    c.drawString(
        25,
        20,
        "Tool W4 - CO2-verloop"
    )

    c.drawRightString(
        page_width - 25,
        20,
        "Pagina 1 / 1"
    )

    # =====================================================
    # SAVE
    # =====================================================

    c.save()

    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="CO2_verloop.pdf"'
    )

    return response