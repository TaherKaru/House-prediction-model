from dataclasses import asdict, dataclass

import httpx

from .config import OVERPASS_URL, WALKSCORE_API_KEY


@dataclass
class NeighbourhoodSignals:
    schools_within_2km: int | None = None
    hospitals_within_2km: int | None = None
    transit_stations_within_2km: int | None = None
    walk_score: int | None = None
    source: str = "not-requested"

    def as_dict(self):
        return asdict(self)


async def fetch_neighbourhood_signals(latitude: float, longitude: float) -> NeighbourhoodSignals:
    """Fetch live OSM amenities within 2 km and optional Walk Score data."""
    query = f"""
    [out:json][timeout:3];
    (
      nwr(around:2000,{latitude},{longitude})[amenity~\"school|college|kindergarten\"];
      nwr(around:2000,{latitude},{longitude})[amenity~\"hospital|clinic\"];
      nwr(around:2000,{latitude},{longitude})[railway~\"station|halt\"];
      nwr(around:2000,{latitude},{longitude})[public_transport=station];
    ); out center tags;
    """
    signals = NeighbourhoodSignals(source="OpenStreetMap / Overpass")
    try:
        async with httpx.AsyncClient(timeout=4) as client:
            response = await client.post(OVERPASS_URL, data={"data": query})
            response.raise_for_status()
            elements = response.json().get("elements", [])
            school_ids, hospital_ids, transit_ids = set(), set(), set()
            for item in elements:
                tags = item.get("tags", {})
                element_id = f"{item.get('type')}:{item.get('id')}"
                if tags.get("amenity") in {"school", "college", "kindergarten"}:
                    school_ids.add(element_id)
                if tags.get("amenity") in {"hospital", "clinic"}:
                    hospital_ids.add(element_id)
                if tags.get("railway") in {"station", "halt"} or tags.get("public_transport") == "station":
                    transit_ids.add(element_id)
            signals.schools_within_2km = len(school_ids)
            signals.hospitals_within_2km = len(hospital_ids)
            signals.transit_stations_within_2km = len(transit_ids)
            if WALKSCORE_API_KEY:
                walk_response = await client.get("https://api.walkscore.com/score", params={"format": "json", "lat": latitude, "lon": longitude, "wsapikey": WALKSCORE_API_KEY})
                if walk_response.is_success:
                    signals.walk_score = walk_response.json().get("walkscore")
                signals.source += " + Walk Score"
    except (httpx.HTTPError, ValueError):
        signals.source = "unavailable"
    return signals
