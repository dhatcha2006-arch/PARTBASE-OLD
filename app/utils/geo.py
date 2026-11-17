import math
from urllib.parse import quote_plus

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points on Earth in kilometers.
    Returns distance rounded to 1 decimal place.
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 0.0

    R = 6371.0  # Earth radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return round(distance, 1)

def build_google_maps_url(destination_name, area_name="Chennai"):
    """
    Build Google Maps walking directions link with origin omitted so Google uses live location.
    Format: https://www.google.com/maps/dir/?api=1&destination=<destination_name+area+Chennai>&travelmode=walking
    """
    dest_str = f"{destination_name} {area_name} Chennai".strip()
    encoded_dest = quote_plus(dest_str)
    return f"https://www.google.com/maps/dir/?api=1&destination={encoded_dest}&travelmode=walking"
