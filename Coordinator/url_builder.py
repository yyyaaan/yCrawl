from datetime import timedelta, date
from config import *

def url_qr(from1, to1, from2, to2, departure_date, layover_days):
    return f'{from1}-{to1} and {from2}-{to2} on {departure_date.strftime("%d-%b-%Y")} for {layover_days}'

def url_hotel(checkin, nights, hotel):

    global META_URL

    # find hotel code
    if hotel.lower() in META_URL.keys():
        code = META_URL[hotel.lower()]
    else:
        print(META_URL.keys)
        return "ERROR"

    # type check and compute check out date
    if type(checkin) == type(date(2022, 1, 1)):
        checkout = checkin + timedelta(days=nights)
    else:
        return "ERROR"

    # use hotel_code's length to determine hotel group
    if len(code) == 4:
        return f'https://all.accor.com/ssr/app/accor/rates/{code}/index.en.shtml?dateIn={checkin.strftime("%Y-%m-%d")}&nights={nights}&compositions=2&stayplus=false'
    if len(code) == 6:
        return f'https://reservations.fourseasons.com/choose-your-room?hotelCode={code}&checkIn={checkin.strftime("%Y-%m-%d")}&checkOut={checkout.strftime("%Y-%m-%d")}&adults=2&children=0&promoCode=&ratePlanCode=&roomAmadeusCode=&_charset_=UTF-8'
    if len(code) == 7:
        return f'https://www.hilton.com/en/book/reservation/rooms/?ctyhocn={code}&arrivalDate={checkin.strftime("%Y-%m-%d")}&departureDate={checkout.strftime("%Y-%m-%d")}&room1NumAdults=2&displayCurrency=EUR'
    if len(code) > 20:
        return f'https://www.marriott.com/search/default.mi?roomCount=1&numAdultsPerRoom=2&fromDate={checkin.strftime("%m/%d/%Y")}&toDate={checkout.strftime("%m/%d/%Y")}&{code}'


def test_area():
    for this_key in ['Conrad Bora', "Pullman Maldives"]:
        print(url_hotel(date(2022, 9, 1), 3, this_key))
