WATER_SPECIFIC_HEAT_KJ_KG_K = 4.2
WATER_DENSITY_KG_M3 = 998


def buffervat(request):
    Vermogen_max, Vermogen_min, Temp_verschil, tijd_aan = 0, 0, 0, 0
    buffervat_output = []
    if request.method == 'POST':
        Vermogen_max, perc_min, Temp_verschil, tijd_aan = map(
            int,
            [
                request.POST.get('max_vermogen'),
                request.POST.get('min_vermogen'),
                request.POST.get('temp_verschil'),
                request.POST.get('tijd_aan'),
            ],
        )
        Vermogen_min = Vermogen_max * perc_min / 100

        Volume_L = (
            1000 * (Vermogen_min * tijd_aan * 60)
            / (WATER_DENSITY_KG_M3 * Temp_verschil * WATER_SPECIFIC_HEAT_KJ_KG_K)
        )

        buffervat_output = [
            round(Volume_L),
            Vermogen_min,
            Temp_verschil,
            tijd_aan,
            WATER_SPECIFIC_HEAT_KJ_KG_K,
            WATER_DENSITY_KG_M3,
        ]

    return buffervat_output