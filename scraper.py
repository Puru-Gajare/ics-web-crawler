import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import tokenFunctions
from utils import get_urlhash, get_logger
from utils.response import Response


# from crawler import frontier

# Global Variables:
numberOfUniquePages = 0
longestPageWordCount = 0
fiftyMostCommonWords = dict()
numberofSubdomains = 0
visitedSites = set()


def scraper(url, resp, frontier, word_frequencies: dict):
    '''

    url: actual url
    resp: web response containing the page

    return: list of urls scrapped from page
    '''

    # if url is not valid, don't parse it
    if (is_valid(url) == False) or (get_urlhash(url) in visitedSites ):
        print("skipping this link in scraper(), url:", url)
        return []

    # step 1: extract information from page's text in order to answer question on report
    
    # step 2: return list of urls scrapped from that page
    links = extract_next_links(url, resp, frontier, word_frequencies)
    

    # increment number of unique pages
    # numberOfUniquePages += 1

    visitedSites.add(get_urlhash(url))
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp: Response, frontier, word_frequencies: dict):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    # if the url is already in the queue, don't add it again
    # frontier.to_be_downloaded is the actual queue
    if url in frontier.to_be_downloaded: 
        return []
    
    # Status Code 301: redirect to permananent new location
    # Status Code 302: redirect to temporary new location
    # THIS WILL NOT WORK, resp is not a response object
    if resp.status == 301 and resp.status == 302:
        return [resp.headers['Location']]       
    if resp.status != 200:
        # handle poor connection issues
        return []


    urls_found = []
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    anchor_tags = soup.find_all("a")
    # for every anchor tag, append
    for anchor_tag in anchor_tags:
        if anchor_tag.has_attr("href"):
            url = anchor_tag["href"]
        else:
            continue

        # defragment url
        urlWithoutFragment = url.split('#')[0]
        # is this a relative or absolute url
        if urlWithoutFragment[0:4] != "http":  
            urls_found.append(urljoin(url, urlWithoutFragment))
        else:
             urls_found.append(urlWithoutFragment)
       


    text = soup.get_text()
    if len(text) < 300:
        # random value, if the page contains no information, should we return?
        pass

    listOfTokens = tokenFunctions.tokenizeString(text)
    # if longest page word count is this url, 
    # if len(listOfTokens) > longestPageWordCount:
    #     longestPageWordCount = len(listOfTokens)

    tokenDictionary = tokenFunctions.computeWordFrequencies(listOfTokens)
    for word, frequency in tokenDictionary.items():
        # frontier.add_word_frequency(word, frequency)
        if word in word_frequencies:
            word_frequencies[word] += frequency
        else:
            word_frequencies[word] = frequency
    print(len(word_frequencies))

    # print(len(frontier.save["REPORT_INFO"][1]["word_frequencies"]))    
    return urls_found

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        allowed_urls = ["ics.uci.edu",
                        '.ics.uci.edu',   # has to be plain urls to allow for using "in" operator
                        '.cs.uci.edu',
                        '.informatics.uci.edu',
                        '.stat.uci.edu']
        
        allowed = False
        for check_against in allowed_urls:
            if check_against in url:
                allowed = True
                break
            
        if not allowed:
            return False
        


        
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise


# def get_webpage(url: str) -> BeautifulSoup:
#     '''
#     this function gets the webpage and returns a soup object

#     @return: Soup object
#     @error: None
#     '''
#     try:
#         response = requests.get(url)
#         if response.status_code != 200:
#             print("failed to fetch html from url:   ", url)
#             return None
#         return BeautifulSoup(response.text, html.parser) 
#     except requests.RequestException as e:
#         print(f"Error fetching HTML from {url}: {e}")
#         return None