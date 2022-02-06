from datetime import timedelta

url_meta = {
    "pullman maldives": "9924",
    "sofitel moorea": "0566",
    "mercure nadi": "5930",
    "regis bora bora": "countryName=PF&destinationAddress.city=Bora+Bora&destinationAddress.longitude=-151.696515&destinationAddress.latitude=-16.486419",
    "meridien bora bora": "countryName=PF&destinationAddress.city=Bora+Bora&destinationAddress.longitude=-151.736641&destinationAddress.latitude=-16.497324",
    "meridien pines": "destinationAddress.city=Isle+of+Pines%2C+New+Caledonia",
    "marriott fiji": "destinationAddress.city=Fiji",
    "sheraton tokoriki": "destinationAddress.city=Tokoriki+Island%2C+Fiji",
    "desc": "this case-insenitive list contains hotel meta for searching"
}



def url_accor(checkin, nights, hotel):
    hotel_str = url_meta[hotel] if hotel in url_meta.keys() else hotel
    return f'https://all.accor.com/ssr/app/accor/rates/{hotel_str}/index.en.shtml?dateIn={checkin.strftime("%Y-%m-%d")}&nights={nights}&compositions=2&stayplus=false'

def url_marriott(checkin, nights, hotel):
    hotel_str = url_meta[hotel] if hotel in url_meta.keys() else hotel
    checkout = checkin + timedelta(days=nights)
    return f'https://www.marriott.com/search/default.mi?roomCount=1&numAdultsPerRoom=2&fromDate={checkin.strftime("%m/%d/%Y")}&toDate={checkout.strftime("%m/%d/%Y")}&{hotel_str}'