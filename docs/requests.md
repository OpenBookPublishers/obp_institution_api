## Requests

### Institutions

GET `/institutions` Get all institutions

GET `/institutions?institution_uuid=$uuid` Get single institution

POST `/institutions` institution\_name, country\_code

PUT `/institutions` institution\_uuid, institution\_name, country\_code

DELETE `/institutions` instituion\_uuid


### Contacts

GET `/contacts` Get all contacts

GET `/contacts?contact_uuid=$uuid` Get single contact

POST `/contacts` institution\_uuid, contact\_name, (email\_address, contact\_notes)

PUT `/contacts` institution\_uuid, contact\_uuid, contact\_name, (email\_address, contact\_notes)

DELETE `/contacts` contact\_uuid


### Countries

GET `/countries` Get all countries

GET `/countries?country_name=$name` Get single country

POST `/countries` country\_code, country\_name

DELETE `/countries` country\_code Delete code and all country\_names

DELETE `/countries` country\_name Delete a country\_name (keeping it's code intact)


### IP Ranges

GET `/ipranges` Get all ipranges

GET `/ipranges?ip_range_value=$iprange` Get single IP Range

POST `/ipranges` institution\_uuid, ip\_range\_value

DELETE `/ipranges` ip\_range\_value



