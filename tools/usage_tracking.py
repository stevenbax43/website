TOOL_ROUTE_CODES = {
    "gebouwgegevens": "A1",
    "eenhedenconversie": "A2",
    "klimaatjaar": "A3",
    "NL-sfB": "A4",
    "mollier": "W1",
    "expansievat": "W2",
    "drukverlies": "W3",
    "CO2verloop": "W4",
    "buffervat": "W5",
    "thermisch_vermogen": "W6",
    "installatiegeluid": "W7",
    "driefase_vermogen": "E1",
}

SERVER_CALCULATION_ROUTES = {
    "gebouwgegevens",
    "klimaatjaar",
    "mollier",
    "expansievat",
    "CO2verloop",
    "buffervat",
    "installatiegeluid",
}

CLIENT_CALCULATION_TOOLS = {
    "A2",
    "W3",
    "W6",
    "E1",
}

EXCLUDED_USAGE_USERNAMES = {"stevenbax"}
EXCLUDED_USAGE_EMAILS = {"steven.bax@kropman.nl"}


def is_usage_tracking_excluded(user):
    return (
        user.get_username().casefold() in EXCLUDED_USAGE_USERNAMES
        or (user.email or "").casefold() in EXCLUDED_USAGE_EMAILS
    )
