from geopy.geocoders import Photon

def get_coordinates(address):
    data = {}
    try:
        geolocator = Photon(user_agent="measurements")
        geo = geolocator.geocode(address)
        return False, geo.latitude, geo.longitude, None
    except:
        data['state'] = False
        data['detail'] = '주소 -> 좌표 실패'
        return True, None, None, data

def get_address(coordinates):
    data = {}
    try:
        geolocator = Photon(user_agent="measurements")
        address = geolocator.reverse(coordinates)
        return False, str(address), None
    except:
        data['state'] = False
        data['detail'] = '좌표 -> 주소 실패'
        return True, None, None, data