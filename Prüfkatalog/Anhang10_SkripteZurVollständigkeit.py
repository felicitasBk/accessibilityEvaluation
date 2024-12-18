import osmnx as ox
import pandas as pd


# Untersuchungsgegenstand festlegen
placeName = "Bamberg, Germany"

# Straßen extrahieren
tags = {'highway': True}
streetElements = ox.features_from_place(placeName, tags)

totalStreetElements = len(streetElements)
elementsWithoutSurfaceData = streetElements[streetElements['surface'].isna()]
elementsWithoutInclineData = streetElements[streetElements['incline'].isna()]
elementsWithoutKerbData = streetElements[streetElements['kerb'].isna()]
elementsWithoutKerbHeightData = streetElements[streetElements['kerb:height'].isna()]

# Straßenüberquerungen extrahieren
tags = {'highway': 'crossing'}
highwayCrossings = ox.features_from_place(placeName, tags)

totalCrossings = len(highwayCrossings)
elementsWithoutTrafficSignalData = highwayCrossings[highwayCrossings['traffic_signals:sound'].isna()]
elementsWithoutTactilePavingData = highwayCrossings[highwayCrossings['tactile_paving'].isna()]

# Metriken berechnen
kpiRoutingKerb = 1 - (len(elementsWithoutKerbData)/totalStreetElements)
kpiRoutingKerbHeight = 1 - (len(elementsWithoutKerbHeightData)/totalStreetElements)
kpiRoutingSurface = 1 - (len(elementsWithoutSurfaceData)/totalStreetElements)
kpiRoutingIncline = 1 - (len(elementsWithoutInclineData)/totalStreetElements)
kpiRoutingTactilePaving = 1 - (len(elementsWithoutTactilePavingData)/totalCrossings)
kpiRoutingTrafficSignals = 1 - (len(elementsWithoutTrafficSignalData)/totalCrossings)

# Ergebnisse ausgeben
print(f"Vollständigkeit - Routing - Bordsteinkanten: {kpiRoutingKerb}")
print(f"Vollständigkeit - Routing - Bordsteinhöhen: {kpiRoutingKerbHeight}")
print(f"Vollständigkeit - Routing - Oberflächen: {kpiRoutingSurface}")
print(f"Vollständigkeit - Routing - Steigung: {kpiRoutingIncline}")
print(f"Vollständigkeit - Routing - Taktile Leitsysteme: {kpiRoutingTactilePaving}")
print(f"Vollständigkeit - Routing - Ampelsignale: {kpiRoutingTrafficSignals}")

#############################################################

# Orte extrahieren & kategorisieren
buildings = ox.features_from_place(placeName, tags={"building": True})
amenities = ox.features_from_place(placeName, tags={"amenity": True})

totalBuildings = len(buildings)
totalAmenities = len(amenities)

placesWithoutWheelchairData = amenities[amenities['wheelchair'].isna()]

buildingsWithTaggedEntranceWidth = 0
for _, row in buildings.iterrows():
    # Check if 'entrance:width' is present
    if 'entrance:width' in row:
        buildingsWithTaggedEntranceWidth += 1

# Metriken berechnen
kpiPlacesWheelchair = (totalAmenities - len(placesWithoutWheelchairData))/totalAmenities
kpiPlacesEntranceWidth = buildingsWithTaggedEntranceWidth/totalBuildings

# Ergebnisse ausgeben
print(f"Vollständigkeit - Orte - Rollstuhlgerechtigkeit: {(kpiPlacesWheelchair)}")
print(f"Vollständigkeit - Orte - Türbreite: {(kpiPlacesEntranceWidth)}")

#############################################################

# Toiletten extrahieren & kategorisieren
tags = {'amenity': 'toilets'}
toilets = ox.features_from_place(placeName, tags)

# Metriken berechnen
totalToilets = len(toilets)
toiletsWithoutWheelchairTag = toilets[toilets['wheelchair'].isna()]
kpiToilets = 1- (len(toiletsWithoutWheelchairTag)/totalToilets)

# Ergebnis ausgeben
print(f"Vollständigkeit - Toiletten - Rollstuhlgerechtigkeit: {kpiToilets}")

#############################################################

# Parkflächen extrahieren
tags = {'amenity': 'parking'}
parkingAreas = ox.features_from_place(placeName, tags)

# Spezifische Parkplätze extrahieren
parkingSpotTag = {'amenity': 'parking_space'}
parkingSpots = ox.features_from_place(placeName, parkingSpotTag)

disabledParkingAreas = 0
roadsideParkingSpaces = 0
parkingSpaces = 0

# In Abhängigkeit des OSM Schemas Behindertenparkplätze finden und summieren
for _, row in parkingSpots.iterrows():
    if 'disabled' in row and row['disabled'] in ['yes', 'designated']:
        parkingSpaces += 1
    elif 'parking_space' in row and row['parking_space'] == 'disabled':
        parkingSpaces += 1

for _, row in parkingAreas.iterrows():

    if 'capacity:disabled' in row and pd.notna(row['capacity:disabled']):
        capacity_disabled = row['capacity:disabled']
        
        if isinstance(capacity_disabled, (int, float)):  # Numerische Werte
            disabledParkingAreas += int(capacity_disabled)
        elif isinstance(capacity_disabled, str):  # String Werte
            capacity_disabled = capacity_disabled.lower()
            if capacity_disabled.isdigit():
                disabledParkingAreas += int(capacity_disabled)
            elif capacity_disabled == "yes":
                disabledParkingAreas += 1
            elif capacity_disabled == "no":
                disabledParkingAreas += 0

    if any('parking:side' in col for col in row.index):
        if 'parking:side:disabled' in row and row['parking:side:disabled'] == 'designated':
            roadsideParkingSpaces += 1

kpiParking = (disabledParkingAreas + roadsideParkingSpaces + parkingSpaces) / 93

# Ergebnisse ausgeben
print(f"Parkflächen (capacity:disabled): {disabledParkingAreas}")
print(f"Parkplätze entlang der Straße (parking:side:disabled or capacity): {roadsideParkingSpaces}")
print(f"Einzelne Parkplätze (amenity=parking_space): {parkingSpaces}")
print(f"Vollständigkeit - Parken: {kpiParking}")

#############################################################

# ÖPNV Haltestellen extrahieren & kategorisieren
tags = {
    'public_transport': ['platform', 'station', 'stop_position'],
    'highway': 'bus_stop'
}
transportStops = ox.features_from_place(placeName, tags)

totalStops = len(transportStops)
StopsWithoutWheelchairTag = transportStops[transportStops['wheelchair'].isna()]
StopsWithoutTactilePavingTag = transportStops[transportStops['tactile_paving'].isna()]

# Metriken berechnen
kpiStopsWheelchair = 1 - (len(StopsWithoutWheelchairTag)/totalStops)
kpiStopsTactilePaving = 1 - (len(StopsWithoutTactilePavingTag)/totalStops)

# Ergebnisse ausgeben
print(f"Vollständigkeit - ÖPNV - Rollstuhlgerechtigkeit: {kpiStopsWheelchair}")
print(f"Vollständigkeit - ÖPNV - Taktiles Leitsystem: {kpiStopsTactilePaving}")

#############################################################


