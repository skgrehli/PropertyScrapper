import csv
import requests
from datetime import datetime
from bs4 import BeautifulSoup


def fetch_data(year):
    CSV_URL = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-%s.csv" % year
    download = requests.get(CSV_URL)
    decoded_content = download.content.decode('utf-8')
    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    my_list = list(cr)
    response_json = {}
    for row in my_list:
        address = ''
        if row[7]:
            address = row[7]
        if row[8]:
            address = address + ' ' + row[8]
        if row[9]:
            address = address + ' ' + row[9]
        district = row[11]
        town = row[12]
        county = row[13]
        postcode = row[3]
        price = row[1]
        date = row[2]
        datetime_object = datetime.strptime(date, '%Y-%m-%d %H:%M')
        month_name = datetime_object.strftime("%B")
        type1 = row[4]
        new_build = row[5]
        LR_url = row[15]
        zoopla_address = address + ', ' + town + ', ' + \
            postcode  # '37 Talbot Road, Hatfield, AL10 0RA'
        zoopla_address_url = "https://www.zoopla.co.uk/search/?q=%s&geo_autocomplete_identifier=&search_source=house-prices&section=house-prices&view_type=list" % zoopla_address
        zoopla_address_page = requests.get(zoopla_address_url)
        print(zoopla_address_url)
        soup = BeautifulSoup(zoopla_address_page.text, 'html.parser')
        try:
            zoopla_url = 'https://www.zoopla.co.uk' + \
                soup.select(
                    ".yourresult .browse-cell-address a")[0].get_attribute_list('href')[0]
        except Exception as e:
            try:
                zoopla_url = 'https://www.zoopla.co.uk' + \
                    soup.select(
                        "tr .browse-cell-address a")[0].get_attribute_list('href')[0]
            except Exception as e:
                continue
        print(zoopla_url)
        zoopla_page = requests.get(zoopla_url)
        soup = BeautifulSoup(zoopla_page.text, 'html.parser')
        try:
            zoopla_beds = soup.select(".ui-list-flat li.ui-property-spec__item")[
                0].get_text().replace('\n', '').replace('bedrooms', '').strip()
            zoopla_baths = soup.select(".ui-list-flat li.ui-property-spec__item")[
                1].get_text().replace('\n', '').replace('bathrooms', '').strip()
            zoopla_living = soup.select(".ui-list-flat li.ui-property-spec__item")[
                2].get_text().replace('\n', '').replace('receptions', '').strip()
        except Exception as e:
            zoopla_beds = 0
            zoopla_baths = 0
            zoopla_living = 0
        try:
            zoopla_agent = soup.select(
                "small.pdp-history__marketed-by strong")[0].get_text().replace('\n', '').strip()
        except Exception as e:
            zoopla_agent = ''

        rightmove_address = address + ' ' + town + ' ' + \
            postcode  # "37 Talbot Road Hatfield AL10 0RA"
        rightmove_address_url = "https://www.rightmove.co.uk/house-prices/search.html?searchLocation=%s&showMapView=&locationIdentifier=&referrer=landingPage&housePrices=List View" % rightmove_address
        print(rightmove_address_url)
        rightmove_address_page = requests.get(rightmove_address_url)
        soup = BeautifulSoup(rightmove_address_page.text, 'html.parser')

        try:
            rightmove_url = soup.select(".soldDetails a.soldAddress")[
                0].get_attribute_list('href')[0]
            rightmove_page = requests.get(rightmove_url)
            soup = BeautifulSoup(rightmove_page.text, 'html.parser')
            rightmove_beds = soup.select("#propertydetails h2")[
                1].get_text().replace('\n', '').strip().split()[0]
        except Exception as e:
            rightmove_url = ''
            rightmove_beds = ''

        print(address, district, town, county, postcode, price, date, type1, new_build, LR_url, zoopla_url,
              zoopla_beds, zoopla_baths, zoopla_living, zoopla_agent, rightmove_url, rightmove_beds)

        month_data = response_json.get(month_name, [])
        month_data.append([address, district, town, county, postcode, price, date, type1, new_build, LR_url, zoopla_url,
                          zoopla_beds, zoopla_baths, zoopla_living, zoopla_agent, rightmove_url, rightmove_beds])
        response_json[month_name] = month_data

        # Column A(address)= Merge without losing data of columns H, I, J from Land Registry
        # Column B (district) = column L from Land Registry
        # Column C (town)= column M from Land Registry
        # Column D (county) = column N from Land Registry
        # Column E (postcode) = column D from Land Registry
        # Column F (price) = column B from Land Registrye.g. 315000
        # ColumnG (date) = column C fromLand Registrye.g. 01/02/2019
        # Column H (type) = column E from Land Registrye.g. T
        # Column I (new build) = column F from Land Registry e.g. Y or N
        # Column J (tenure) = columnG fromLand Registry e.g. F or L
        # Column K (LR url) = columnP fromLand Registry
        # Column L (zoopla url) = url for this address fromzoopla
        # ColumnM (zoopla beds) = bedrooms number from zoopla. E.g. 3
        # ColumnN(zoopla baths) = bathroomnumber from zoopla. E.g.1
        # ColumnO(zoopla living) = living roomnumber from zoopla. E.g. 2
        # Column P (zoopla agent) = estate agent name from zoopla eg Kings Estate Agents
        # Column Q(rightmove url) = url for this address from rightmove
        # Column R (rightmove beds) = bedrooms number from rightmove e.g. 3
    return response_json


if __name__ == '__main__':
    for year in ['2016', '2017', '2018', '2019']:
        response_json = fetch_data(year)
        for month_name, data in response_json.items():
            with open("%s_%s.csv" %(month_name, year), "w") as out_file :
                writer = csv.writer(out_file)
                writer.writerow(['address' ,'district', 'town', 'county', 'postcode', 'price', 'date', 'type','new build', 'new build','LR url', 'zoopla url','zoopla beds','zoopla baths','zoopla living','zoopla agent','rightmove url','rightmove beds',])
                for row in data:
                    writer.writerow(row)
