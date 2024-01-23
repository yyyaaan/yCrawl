```
node node_handler.js a01 'https://www.marriott.com/search/default.mi?roomCount=1&numAdultsPerRoom=2&fromDate=02/15/2024&toDate=02/19/2024&destinationAddress.city=New+Caledonia'

node node_handler.js not 'https://www.marriott.com/search/default.mi?roomCount=1&numAdultsPerRoom=2&fromDate=11/17/2023&toDate=11/22/2023&countryName=PF&destinationAddress.city=Bora+Bora&destinationAddress.longitude=-151.696515&destinationAddress.latitude=-16.486419'
```

##  New URL scheme

```
node node_handler.js new 'https://www.marriott.com/search/submitSearch.mi?recordsPerPage=20&isInternalSearch=true&vsInitialRequest=false&searchType=InCity&searchRadius=50.0&missingcheckInDateMsg=Please+enter+a+check-in+date.&is-hotelsnearme-clicked=false&for-hotels-nearme=Near&missingcheckOutDateMsg=Please+enter+a+check-out+date.&pageType=advanced&collapseAccordian=is-hidden&singleSearch=true&destinationAddress.city=New+Caledonia&isTransient=true&initialRequest=false&dimensions=0&destinationAddress.destination=New+Caledonia&fromToDate=01%2F15%2F2024&fromToDate_submit=01%2F19%2F2024&fromDate=01%2F15%2F2024&toDate=01%2F19%2F2024&toDateDefaultFormat=01%2F19%2F2024&fromDateDefaultFormat=01%2F15%2F2024&flexibleDateSearch=false&isHideFlexibleDateCalendar=false&t-start=2024-01-15&t-end=2024-01-19&lengthOfStay=4&roomCountBox=1+Room&roomCount=1&guestCountBox=2+Adult+Per+Room&numAdultsPerRoom=2&childrenCountBox=0+Children+Per+Room&childrenCount=0&clusterCode=none&corporateCode='
```