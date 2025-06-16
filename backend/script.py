def get_idfm_agency():
    """
    Returns a list of agency IDs for IDFM.
    """
    f = open("IDFM-gtfs/agency.txt", "r")
    data = f.readlines()
    id = []
    for line in data:
        if line.startswith("agency_id"):
            continue
        if "IDFM" in line:
            id.append(line.strip().split(",")[0])
    print(id)
    f.close()

def get_idfm_routes():
    """
    Returns a list of route IDs for IDFM.
    """
    f = open("IDFM-gtfs/routes.txt", "r")
    data = f.readlines()
    id = []
    for line in data:
        if line.startswith("route_id"):
            continue
        ligne = line.strip().split(",")
        if ligne[5] == '1':
            id.append(ligne)
    print(id, len(id))
    f.close()


def get_idfm_trips():
    """
    Returns a list of trip IDs for IDFM.
    """
    f = open("IDFM-gtfs/trips.txt", "r")
    data = f.readlines()
    lignes = []
    for line in data:
        if line.startswith("trroute_id"):
            continue
        ligne = line.strip().split(",")
        if ligne[0] == 'IDFM:C01377':
            lignes.append(ligne)
    print(lignes[0], len(lignes))
    f.close()

get_idfm_trips()

#IDFM:C01377


