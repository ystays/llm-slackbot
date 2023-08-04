import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urlparse, urljoin
import os

def save_all_urls(csv_file_name):
    # Set the starting URL
    base_url = 'https://saatva.com/'

    # Initialize the set of visited URLs and add the base URL
    visited_urls = set()
    visited_urls.add(base_url)

    # Initialize the set of URLs to be visited and add the base URL
    urls_to_visit = set()
    urls_to_visit.add(base_url)

    # Parse the base URL to get the domain name
    base_domain = urlparse(base_url).netloc

    # Initialize the CSV writer
    csv_file = open(csv_file_name, 'w', newline='')
    csv_writer = csv.writer(csv_file)

    print(base_domain)

    # Loop through the URLs to be visited
    while urls_to_visit:

        # Get the next URL from the set of URLs to be visited
        current_url = urls_to_visit.pop()

        try:
            # Make a GET request to the URL
            response = requests.get(current_url)

            # Check if the response was successful (status code 200)
            if response.status_code == 200:

                # Parse the HTML content of the page
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all the links on the page
                for link in soup.find_all('a'):

                    # Get the URL from the link
                    link_url = link.get('href')

                    if link_url is not None and link_url != '':
                        # Normalize the link URL by joining it with the base URL
                        link_url = urljoin(current_url, link_url)

                        parsed_url = urlparse(link_url)
                        # Parse the domain name from the link URL
                        link_domain = parsed_url.netloc

                        linkpath = parsed_url.path.split('/')

                        # Check if the link domain matches the base domain
                        if link_domain == base_domain and len(linkpath) > 2 and \
                            linkpath[1] in ["mattresses", "bedding", "furniture", "bundle"] and parsed_url.query == "":
                            print(link_url)
                            # Add the link URL to the set of URLs to be visited if it hasn't been visited yet
                            if link_url not in visited_urls:
                                urls_to_visit.add(link_url)

                            # Add the link URL to the set of visited URLs
                            visited_urls.add(link_url)

                            # Write the link URL to the CSV file
                            # csv_writer.writerow([link_url])

            # Print an error message if the response was not successful
            else:
                print('Error: ' + str(response.status_code))


        # Print an error message if there was an error making the GET request
        except requests.exceptions.RequestException as e:
            print('Error: ' + str(e))

    sorted_urls = sorted(visited_urls)
    for url in sorted_urls:
        csv_writer.writerow([url])

    # Close the CSV file
    csv_file.close()




def check_for_url_duplicates():
    url_set = set()
    no_of_duplicates = 0

    with open('links_pdp.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        print(f"no of urls found {len(list(reader))}")
        for row in reader:
            url = row[0].strip()
            if url in url_set:
                no_of_duplicates += 1
                print(f"Duplicate URL found: {url}")
            else:
                url_set.add(url)

    print(f"No of duplicates found {no_of_duplicates}")
    print("Duplicate check complete!")

def convert_to_text(x, separator='\n'):
    if x:
        return x.get_text(separator=separator, strip=True) + "\n\n"
    else:
        return ""

def access_html_and_parse(urls_csv_file_name):
    # Create the data_output directory if it does not already exist
    if not os.path.exists('../output'):
        os.makedirs('../output')

    counter = 0

    with open(urls_csv_file_name, 'r') as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:
            url = row[0]
            response = requests.get(url)

            # Check if response object is not None
            if response is not None:
                soup = BeautifulSoup(response.content, 'html.parser')

                # productPanel = soup.find('section', id='productPanel')
                title = soup.find('header', class_='productPanel__title')
                if title:
                    productName = (title.find("h1"))
                    if productName:
                        productName = productName.get_text(separator='\t', strip=True)
                    else:
                        productName = ""
                else:
                    productName = ""
                title = convert_to_text(title)

                productDescription = soup.find(class_=lambda x: x and 'panel__description' in x.lower())
                productDescription = convert_to_text(productDescription)
                
                productDetails = soup.find(class_='productDetailsOverviewDynamic')
                productDetails = convert_to_text(productDetails)

                productTabbedFeatures = soup.find(id='tabbedFeatures')
                productTabbedFeatures = convert_to_text(productTabbedFeatures)

                productOverview = soup.find(class_=lambda x: x and "overview" in x.lower())
                productOverview = convert_to_text(productOverview)

                productSpecsTemp = soup.find_all(id=lambda x: x and x.lower().endswith('specs'))
                productSpecs = ""
                for s in productSpecsTemp:
                    productSpecs += "\n" + convert_to_text(s)
                
                productLinkedContent = soup.find(class_="contentNav__linkedContent")
                productLinkedContent = convert_to_text(productLinkedContent)

                productValueProps = soup.find('section', class_=lambda x: x and "valueprop" in x.lower())
                productValueProps = convert_to_text(productValueProps)

                productFaq = soup.find(id=lambda x: x and 'faq' in x)
                productFaq = convert_to_text(productFaq)
                    
                # productSurveyResults = soup.find('section', id='marketSurveyResults')
                    
                # productReviews = soup.find('section', id='customer-reviews')
                
                # productSelectSize = soup.find('div', class_='productPanel__selectSize')

                formRadio_options = soup.find_all('input', attrs={'name':'mattressSizeOptions'})
                
                currPageText = ""
                currPageText += title

                if formRadio_options:
                    for f in formRadio_options:
                        url_option = url + "?sku=" + f["value"]
                        print(url_option)
                        currPageText += "\n\n" + productName
                        response = requests.get(url_option)
                        if response is not None:
                            soup_option = BeautifulSoup(response.content, 'html.parser')

                            options = soup_option.find_all('div', class_='formToggle is-selected')
                            for option in options:
                                currPageText += "\t" + option.get_text(separator='\t', strip=True) + " "

                            productPrice = soup_option.find('div', class_='smallPriceDisplay')
                            productPrice = productPrice.get_text(separator='\t', strip=True)
                            currPageText += "\tPrice: " + productPrice + "\n"                  

                    currPageText += productDescription + productDetails + productTabbedFeatures + productOverview + productSpecs + productValueProps + productFaq
                else:
                    productPanelContent = soup.find('div', id='productPanelContent')
                    productPanelContent = convert_to_text(productPanelContent)
                    productPrice = soup.find('div', class_='smallPriceDisplay')
                    if productPrice:
                        productPrice = productPrice.get_text(separator="\t", strip=True) + "\n"
                    else:
                        productPrice = ""
                    currPageText += productName + "\tPrice: " + productPrice + productPanelContent + productTabbedFeatures + productOverview + productSpecs + productValueProps + productFaq

                # main_text = main_tag.get_text(separator='\n', strip=True)

                # Create a filename based on the url
                filename = url.replace('https://', '').replace('http://', '').replace('/', '_').replace(':', '') + '.txt'

                # Save the text to a file in the data_output directory
                with open('../output/' + filename, 'w') as f:
                    print(counter)
                    counter += 1
                    f.write(currPageText)
                
            else:
                print(f"Error fetching {url}")


if __name__ == "__main__":
    n = input("Are you sure you want to initialize scraping data? (y/n)")
    if n == 'y':
        save_all_urls('links_pdp.csv')
        check_for_url_duplicates()
        access_html_and_parse('links_pdp.csv')