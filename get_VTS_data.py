import requests
import time
import sys
from bs4 import BeautifulSoup

# replace these values with the API Key and Secret from VTS
API_KEY = 'FOO'
API_SECRET = 'BAR'


def get_XML_parameter(text, search_open, search_close):
    '''
    Parameters: text - type: string,
                search_open - type: string,
                search_close - type: string
    Return value: type: string

    Returns the deal export status or Job ID from the VTS Deal API
    Status will be one of: [submitted, processing, completed, failed]
    Job ID is a unique identifier string for the deal export to be used to check the export status
    '''
    
    start = text.find(search_open) + len(search_open)
    end = text.find(search_close)
    parameter = text[start:end]
    return parameter


def test_Authorization():
    '''
    Tests authorization of <API Key>:<API Secret> and prints the XML response.
    '''
    response = requests.get('https://api.vts.com/api/connect/v1', auth=(API_KEY, API_SECRET))
    print(response.content)


def get_Deal_Data(deal_stage):
    '''
    Parameter: deal_stage - type: string
    Return value: type: string
    
    Takes a VTS-defined deal stage and returns XML output of all deals within that stage.
    Prints status updates every 10 seconds on export status.
    '''
    stage = deal_stage
    post_request = "https://api.vts.com/api/deal/v1/deal_api_requests?deal_stage=" + stage

    # curl -u <API Key>:<API Secret> -X POST https://api.vts.com/api/deal/v1/deal_api_requests
    # can add request parameters: date, deal_id, deal_stage, and property_id
    response = requests.post(post_request, auth=(API_KEY, API_SECRET))

    # get deal export status and unique job ID
    text = response.text
    status = get_XML_parameter(text, "<status>", "</status>")
    jobid = get_XML_parameter(text, "<jobid>", "</jobid>")

    # print status and job ID
    print("Initiating export from " + post_request)
    print("Deal Export Status: " + status)
    print("Job ID: " + jobid)

    # check status every 10 seconds and update user on export status
    while (status != "completed"):

        # continue to check status of deal export until completed or failed
        # curl -u <API Key>:<API Secret> https://api.vts.com/api/deal/v1/deal_api_requests/<jobid>
        get_Request_URL = "https://api.vts.com/api/deal/v1/deal_api_requests/" + jobid
        response = requests.get(get_Request_URL, auth=(API_KEY, API_SECRET))
        text = response.text
        status = get_XML_parameter(text, "<status>", "</status>")
    
        if status == "failed":
            print("Error: deal export from VTS failed. Please try again later.")
            sys.exit("Oh noes!")
        elif status == "submitted":
            print("Status update: Request for deal export has been submitted. Please wait...")
            time.sleep(10)
        elif status == "processing":
            print("Status update: Request for deal export is processing...")
            time.sleep(10)

    # status == successful
    print("Deal export successful. Fetching export now...")

    ''' get data from completed deal export '''
    # curl -u <API Key>:<API Secret> https://api.vts.com/api/deal/v1/deal_api_requests/<jobid>/data
    get_Request_URL = "https://api.vts.com/api/deal/v1/deal_api_requests/" + jobid + "/data"
    response = requests.get(get_Request_URL, auth=(API_KEY, API_SECRET))
    text = response.text.encode('utf-8')

    return text


def export_Deal_Data(text, path):
    '''
    Parameter: text - type: string
               path - type: string

    Prints deal data (XML text) to the specified file (path). Prints confirmation to the console.
    '''
 
    # open file for writing
    output_file = open(path, 'w')
   
    # use Beautiful Soup to pretty-print the XML
    soup = BeautifulSoup(text, 'xml')
    output_file.write(soup.prettify())
    
    output_file.close()
    print("Deal export data has been printed to: " + path)


def main():

    # XML files to which we will export deal data
    path_tour = './tour.xml'   
    path_proposal = './proposal.xml'   
    path_loi = './loi.xml'   
    
    # get deal data for tours, proposals, and LOIs and export to XML
    tour = get_Deal_Data("tour")
    export_Deal_Data(tour, path_tour)
    
    proposal = get_Deal_Data("proposal")
    export_Deal_Data(proposal, path_proposal)
    
    loi = get_Deal_Data("loi")
    export_Deal_Data(loi, path_loi)


if __name__ == "__main__":
    main()
