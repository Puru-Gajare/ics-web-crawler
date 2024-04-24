import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import tokenFunctions
from utils import get_urlhash, get_logger
from utils.response import Response


# from crawler import frontier

# Global Variables:
'''
numberOfUniquePages = 0         =>      completed in frontier.py class
longestPageWordCount = 0
fiftyMostCommonWords = dict()
numberofSubdomains = 0
'''


def scraper(url, resp, frontier, word_frequencies: dict, longest_url: list, ics_frequencies):
    '''

    url: actual url
    resp: web response containing the page

    return: list of urls scrapped from page
    '''

    # if url is not valid, don't parse it
    # no need to check if the url is in the shelve, should be covered by the add_url function in worker.py: url not added to queue if it's been seen before
    if (is_valid(url) == False):
        print("skipping this link in scraper(), url:", url)
        return []
    
    # subdomain stuff
    url_parsed = urlparse(url)
    url_parsed = url_parsed.scheme + "://" + url_parsed.hostname
    if ("ics.uci.edu" in url_parsed):
        if url_parsed in ics_frequencies:
            ics_frequencies[url_parsed] += 1
        else:
            ics_frequencies[url_parsed] = 1    
        
    # step 2: return list of urls scrapped from that page
    links = extract_next_links(url, resp, frontier, word_frequencies, longest_url)
    
    # visitedSites.add(get_urlhash(url))
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp: Response, frontier, word_frequencies: dict, longest_url: str):
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
    # changed to remove the return [] that was after this block
    if resp.status > 300 and resp.status < 309:
        if is_valid(resp.headers['Location']):
            return [resp.headers['Location']]     
            
    if resp.status != 200: 
        # handle poor connection issues, including 404
        return []


    urls_found = []
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    anchor_tags = soup.find_all("a")
    text = soup.get_text()
    # for every anchor tag, append
    if len(text) < 500:
        print("skipping because of low information value")
        return []
    for anchor_tag in anchor_tags:
        if anchor_tag.has_attr("href"):
            tempUrl = anchor_tag["href"]
        else:
            continue

        # defragment url
        urlWithoutFragment = tempUrl.split('#')[0]
        # is this a relative or absolute url
        if urlWithoutFragment[0:4] != "http":  
            urls_found.append(urljoin(url, urlWithoutFragment))
        else:
             urls_found.append(urlWithoutFragment)
       


    text = soup.get_text()
    # this is 500 characters

    listOfTokens = tokenFunctions.tokenizeString(text)

    # This function should in theory update the longest url in frontier
    if len(listOfTokens) > longest_url[1]:
        longest_url[1] = len(listOfTokens)
        longest_url[0] = url


    tokenDictionary = tokenFunctions.computeWordFrequencies(listOfTokens)
    for word, frequency in tokenDictionary.items():
        if word in word_frequencies:
            word_frequencies[word] += frequency
        else:
            word_frequencies[word] = frequency    

    return urls_found

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if (parsed.hostname == None):
            return False
        
        blacklisted = ["https://swiki.ics.uci.edu/doku.php", 'http://www.informatics.uci.edu/files/pdf/InformaticsBrochure-March2018']
        for black_url in blacklisted:
            if black_url in url:
                return False
        
        allowed_urls = ['.ics.uci.edu',   # has to be plain urls to allow for using "in" operator
                        '.cs.uci.edu',
                        '.informatics.uci.edu',
                        '.stat.uci.edu']
        
        allowed = False
        for allowed_portion in allowed_urls:
            if allowed_portion in parsed.hostname:
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

