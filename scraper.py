import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import collections
import tokenFunctions
from utils import get_urlhash

# Global Variables:
numberOfUniquePages = 0
longestPageWordCount = 0
fiftyMostCommonWords = dict()
numberofSubdomains = 0
stopWords = {'but', 'by', 'it', 'out', 'up', "couldn't", 'ours', 'ourselves', 'of', 'whom', 'further', 'both', 'would', 'not', 'should', 'how', 'again', 'why', 'theirs', 'who', "where's", 'there', "hasn't", 'more', 'which', 'we', 'no', 'above', 'at', "we'd", 'before', 'they', 'ought', 'them', "won't", 'nor', "you're", 'myself', 'that', 'below', "you'd", 'as', "they've", 'is', 'then', 'our', 'when', "you'll", 'where', "it's", 'those', 'do', 'was', 'into', 'while', 'its', 'only', 'between', 'does', 'any', 'did', 'and', 'me', 'his', 'than', 'an', 'yourself', 'these', 'against', 'himself', 'be', 'because', 'each', "how's", 'are', 'most', 'some', 'have', "there's", 'all', 'she', 'so', "who's", "he's", 'through', 'themselves', 'been', "isn't", 'he', 'down', 'under', 'had', "mustn't", "shan't", "can't", "when's", 'i', 'for', 'very', "weren't", 'itself', 'with', 'her', "wasn't", 'a', 'herself', "we're", 'has', 'were', "she'll", "i'd", 'off', 'could', "he'd", "she's", "they're", "doesn't", "haven't", 'here', 'him', 'on', "i'll", 'over', 'too', 'about', "why's", 'your', "aren't", 'same', "that's", 'doing', 'their', 'in', 'cannot', "hadn't", 'my', 'having', 'yours', 'if', 'what', 'during', "i'm", 'hers', "let's", 'this', "shouldn't", 'to', 'other', 'you', "they'd", 'such', 'yourselve', 'until', "we'll", 'own', "here's", "they'll", 'few', 'or', 'being', "what's", "i've", "she'd", "wouldn't", "you've", "he'll", 'after', 'the', 'am', 'once', 'from', "didn't", "we've", "don't"}
visitedSites = set()


def scraper(url, resp):
    '''

    url: actual url
    resp: web response containing the page

    return: list of urls scrapped from page
    '''

    # if url is not valid, don't parse it
    if is_valid(url) == False or (get_urlhash(url) in visitedSites):
        return []

    # step 1: extract information from page's text in order to answer question on report
    
    # step 2: return list of urls scrapped from that page
    links = extract_next_links(url, resp)
    

    # increment number of unique pages
    numberOfUniquePages += 1

    visitedSites.add(get_urlhash(url))
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    if resp.status == 301:
        
    if resp.status != 200:
        # handle poor connection issues
        return []


    urls_found = []
    print(type(resp.raw_response.content))
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    anchor_tags = soup.find_all("a")

    # for every anchor tag, append
    for anchor_tag in anchor_tags:
        url = anchor_tag["href"]

        # defragment url
        urlWithoutFragment = url.split('#')[0]
        urls_found.append(urlWithoutFragment)


    text = soup.get_text()
    if len(text) < 300:
        # random value, if the page contains no information, should we return?
        pass

    listOfTokens = tokenFunctions.tokenizeString(text)
    # if longest page word count is this url, 
    if len(listOfTokens) > longestPageWordCount:
        longestPageWordCount = len(listOfTokens)

    tokenDictionary = tokenFunctions.computeWordFrequencies(listOfTokens)
    # output 50 highest frequency chars
    
    return urls_found

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        allowed_urls = ['.ics.uci.edu',   # has to be plain urls to allow for using "in" operator
                        '.cs.uci.edu',
                        '.informatics.uci.edu',
                        '.stat.uci.edu']
        
        allowed = False
        edited_url = parsed.hostname[parsed.hostname.find(".", 4):]
        for check_against in allowed_urls:
            if check_against in edited_url:
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