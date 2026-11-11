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

    # =====================================================
    # INPUT CARDS
    # =====================================================

    card_y = page_height - 190
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
        page_height - 215,
        "Resultaten"
    )

    c.setStrokeColor(colors.HexColor("#E0E0E0"))

    c.line(
        110,
        page_height - 212,
        page_width - 25,
        page_height - 212
    )
    # =====================================================
    # KPI CARDS
    # =====================================================

    result_y = page_height - 320
    result_h = 70
    result_w = 165

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

        c.setFont("Helvetica-Bold", 16)

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
        25,
        f"{max_concentration} ppm",
        "Maximale concentratie",
        colors.HexColor("#FFE8ED"),
        colors.HexColor("#FF6384")
    )

    draw_result_card(
        215,
        f"+{max_increase} ppm",
        "Maximale verhoging",
        colors.HexColor("#E8F4FF"),
        colors.HexColor("#36A2EB")
    )

    draw_result_card(
        405,
        time_to_max,
        "Tijd tot maximum",
        colors.HexColor("#E8F8EB"),
        colors.HexColor("#3DAB39")
    )

    # =====================================================
    # GRAFIEK
    # =====================================================

    c.setFont("Helvetica-Bold", 12)

    c.drawString(
        25,
        page_height - 300,
        "CO2-concentratie over de tijd"
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