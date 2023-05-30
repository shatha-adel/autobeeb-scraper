# Scrape information from the autobeeb.com website
#
# Requires Python 3.9 or later
# Requires urllib3 and BeautifulSoup4 installed

import requests
from bs4 import BeautifulSoup
import csv
import urllib3
import os.path
dir_path = os.path.dirname(os.path.realpath(__file__))
outputCsvFilename = os.path.join(dir_path, "out.csv") 
###################################################
## Constants to alter

# Target URL to begin search from
targetUrl = 'https://autobeeb.com/ar/dealer/%D8%A7%D8%A8%D9%88-%D8%A7%D9%8A%D9%85%D9%86-%D8%A7%D9%84%D8%AE%D9%84%D9%8A%D9%84%D9%8A-%D9%84%D9%82%D8%B7%D8%B9-%D8%BA%D9%8A%D8%A7%D8%B1-%D8%A7%D9%84%D8%A8%D9%83%D8%A8%D8%A7%D8%AA-%D8%A7%D9%84%D8%A7%D8%B1%D8%AF%D9%86/da8009c7-8216-4fe0-a7cc-ab3676ccadf2'

# Name of the .csv file to output


headers={"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
"Accept-Encoding":"gzip, deflate, br",
"Accept-Language":"en-US,en;q=0.9,ar-YE;q=0.8,ar;q=0.7",
"Cache-Control":"max-age=0",
"Cookie":"lang=ar; cur=2; _scid=69ef453e-ce1d-4b63-acd0-0476d2bbc7d7; _fbp=fb.1.1684661745410.105608508; _ga=GA1.1.436731662.1684661746; G_ENABLED_IDPS=google; _sctr=1%7C1684616400000; ListingDetails=; _hjSessionUser_1913100=eyJpZCI6ImRiNjBkMTgzLTBmMzgtNWYxYS05NGJhLThmNzM3MDBhYWY2ZSIsImNyZWF0ZWQiOjE2ODQ2NjE3NDY4MzcsImV4aXN0aW5nIjp0cnVlfQ==; ASP.NET_SessionId=km0zgiunp2ztgfmqizqqoukd; prefix=ar-jo; _scid_r=69ef453e-ce1d-4b63-acd0-0476d2bbc7d7; _ga_SLB81K5YL3=GS1.1.1684872788.2.0.1684872788.60.0.0; _ga_GNVBNGZMGL=GS1.1.1684872789.2.0.1684872789.0.0.0; ln_or=eyIxODgxMTI5IjoiZCJ9; _hjIncludedInSessionSample_1913100=0; _hjSession_1913100=eyJpZCI6ImMxNThjOTFhLTEyMDQtNGQ1YS1iZjY5LTc0NzEzNmM4YTYwMiIsImNyZWF0ZWQiOjE2ODQ4NzI3OTQxMTYsImluU2FtcGxlIjpmYWxzZX0=",
"Dnt":"1",
"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"}

# Option to limit the number of pages to scrape, set to 0 to scrape everything
# In my experience the number of pages can be very high so I recommend setting a limit
maxPagesToScrape = 1
###################################################



# http = urllib3.PoolManager()


def scrapeEntry(url):

    # Scrape a particular URL
    try:
        # print(url)
        resp = requests.get(url,headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
    except Exception as E:
        print(f'Exception fetching or parsing entry "{url}": {E}')
        return None

    # Our dictionary of entries
    entryData = {}

    # Fetch the title
    titleH1 = soup.find('h1', attrs={'class': 'f-site-20'})
    if not titleH1:
        print(f'ERROR: Entry "{url}" does not contain expected header dic')
        return None

    entryData['title'] = titleH1.contents[0].strip()
    




    # And the details title
    detailsTitle = soup.find('p', attrs={'class': 'detalis-title'})
    if detailsTitle:
        details = detailsTitle.text.strip()
        details = ' '.join(details.split())
        entryData['detailsTitle'] = details
    else:
        entryData['detailsTitle'] = ''

    # Fetch the user details
    userInfoDiv = soup.find('div', attrs={'class': 'user-info'})
    if not userInfoDiv:
        print(f'ERROR: Cannot find user infomation in Entry "{url}"')
        return None

    entryData['username'] = userInfoDiv.find('p', attrs={'class': 'user-name'}).text.strip()
    entryData['usersince'] = userInfoDiv.find('p', attrs={'class': 'user-time'}).text.strip()

    # When is the offer time?
    entryData['offertime'] = soup.find('p', attrs={'class': 'p-l-15'}).text.strip()

    img=''
    img_name=''
    try:
            img = soup.select_one('.slides img')['src']
            img_name=img.split('/')[-1]
            response = requests.get(img,headers=headers)
            if response.status_code == 200:
                with open(os.path.join(dir_path, img_name) , "wb") as f:
                    f.write(response.content)
            entryData['image'] = img_name
            
    except Exception as e:
        print(e)
    # Retrieve the phone number
    phoneDiv = soup.find('div', attrs={'class': 'call-ad-button'})
    if phoneDiv:
        telref = phoneDiv.find('a')['href']
        telref = telref.split(':')
        if len(telref) != 2 or telref[0] != 'tel':
            print(f'WARNING: Unable to understand phone number for "{url}"')
            entryData['phone'] = ''
        else:
            entryData['phone'] = telref[1]
    else:
        print(f'WARNING: Could not find phone number for "{url}"')
        entryData['phone'] = ''

    # Find the features div
    featureDiv = soup.select('div[class*=key-features]')
    if not featureDiv:
        print(f'ERROR: Entry "{url}" does not contain expected features div')
        return None
    featureDiv = featureDiv[0]

    # Then find all the feature within this
    features = soup.select('.col-sm-4.col-md-4.col-xs-6.no-padding')
    # print(len(features))
    if not features or len(features) == 0:
        print(f'ERROR: No features found in entry "{url}"')
        return None

    for feature in features:
        # print(feature)
        # Get the key, and then ditch the trailing :
        key = feature.find('span').text.strip().replace(":",'').replace('\n','')
        
        value = feature.find('span', attrs={'class': 'feature-value'}).text.strip().replace(":",'').replace('\n','')
       

        entryData[key] = value

        

    return entryData



# Scrape a search page, returning URLs for all entries and then whether they are more pages or not
def scrapeSearchPage(url, pageNum):
    # Scrape a particular URL
    try:
        resp=requests.get(url+f'?pageNum={pageNum}',headers=headers)
        # resp = http.request('GET', url+f'?pageNum={pageNum}')
        soup = BeautifulSoup(resp.text, 'html.parser')
    except Exception as E:
        print(f'Exception fetching or parsing entry "{url}": {E}')
        return (None, None)

    # Get all the results from the first page
    entryURLs = []
    resultCards = soup.select('.dealer')
    if resultCards is None:
        print(f'ERROR: Unable to find the result cards element in "{url}"')
        return (None, None)

    for row in resultCards:
        for entry in row.findChildren('div', recursive=False):
            # Some entries are blank and ignorable, the rest have a clickable image tag
            link = entry.find('a')
            if not link:
                continue

            # After all relevant entries have been found, rather than stopping, it adds less relevant entries
            firstDiv = entry.find('div')
            if not firstDiv:
                continue
            if 'style' in firstDiv.attrs and firstDiv['style'] == 'opacity:0.6 !important; border: 1px solid #fb5201 !important ':
                return (entryURLs, False)

            if 'href' in link.attrs:
                entryURLs.append(link['href'])

    # Didn't stop on a first irrelevant entry, so there is another page of useful entries
    return (entryURLs, True)






def main():
    # Find the domain root
    parsed = urllib3.util.parse_url(targetUrl)
    domainRoot = parsed.scheme + '://' + parsed.host + '/'
    

    # Scrape the main page for entries, reading entries as we go
    data = []
    allKeys = {}
    onPage = 1
    while maxPagesToScrape == 0 or onPage <= maxPagesToScrape:
        print(f'Scraping page {onPage}')
        # Find the links on this page
        entries, morePages = scrapeSearchPage(targetUrl, onPage)
        onPage += 1

        # Check if entries is not None before iterating over it
        if entries:
            # Scrape the entries on this page
            for entry in entries:
                print('   > ' + entry)
                try:
                    entryInfo = scrapeEntry(domainRoot + entry)
                    if entryInfo:
                        data.append(entryInfo)
                        allKeys = allKeys | dict.fromkeys(entryInfo.keys(), '')
                except Exception as e:
                    print(f'Exception during scraping: "{e}"')

        if not morePages:
            print("All relevant entries found. Ending")
            break

    # Write out as .csv file
    with open(outputCsvFilename, 'w', newline='', encoding='utf-8-sig') as outputCsvFile:
        outputCsv = csv.DictWriter(outputCsvFile, allKeys.keys())
        outputCsv.writeheader()
        for row in data:
            # Fill in any missing entries
            completeRow = allKeys | row
            outputCsv.writerow(completeRow)

    print(f'Output written to "{outputCsvFilename}"')





if __name__ == "__main__" :
	main()