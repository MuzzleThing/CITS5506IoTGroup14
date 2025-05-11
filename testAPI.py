import urllib.request
import json
import pprint

api_key = "x8hfpalze3rcc8h1idminp3nwnjgmh"
barcode = input("Please scan the barcode: ")
url = f"https://api.barcodelookup.com/v3/products?barcode={barcode}&formatted=y&key={api_key}"

with urllib.request.urlopen(url) as url:
    data = json.loads(url.read().decode())

barcode = data["products"][0]["barcode_number"]
print ("Barcode Number: ", barcode, "\n")

name = data["products"][0]["title"]
print ("Title: ", name, "\n")

print ("Entire Response:")
pprint.pprint(data)