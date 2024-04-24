import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import tokenFunctions
from utils import get_urlhash, get_logger
from utils.response import Response
from collections import defaultdict
import time


# Global Variables: Don't work in this, as the whole file is never really called

# Trap detect functions


# Avoid infinite redirects
redirect_tracker = defaultdict(int)
def is_infinite_redirect(url):
    redirect_tracker[url] += 1
    return redirect_tracker[url] > 2  # Redirect limit to avoid traps

# Avoid large files
def is_large_file(resp):
    if not resp.raw_response:
        return False
    
    content_type = resp.raw_response.headers.get("Content-Type", "").lower()
    content_length = int(resp.raw_response.headers.get("Content-Length", "0"))

    non_textual_types = ["image", "video", "application"]
    large_file_size = 1000000  # 1 MB

    return any(t in content_type for t in non_textual_types) or content_length > large_file_size

# Avoid infinite trap by not revisiting


url_revisit_tracker = defaultdict(list)
def is_infinite_trap(url, revisit_threshold= 10, time_window=20):
    current_time = time.time()
    url_revisit_tracker[url].append(current_time)

    # Remove old entries outside the time window
    url_revisit_tracker[url] = [t for t in url_revisit_tracker[url] if (current_time - t) < time_window]

    return len(url_revisit_tracker[url]) > revisit_threshold  # High revisit frequency indicates a trap

# Avoid recursive patterns
def has_recursive_pattern(url):
    parsed = urlparse(url)
    path_segments = parsed.path.split("/")
    return len(set(path_segments)) < len(path_segments)  # Detect recursive paths

# main scraper
def scraper(url, resp, frontier, word_frequencies: dict, longest_url: list, ics_frequencies: dict):
    '''
    url: actual url
    resp: web response containing the page
    return: list of urls scrapped from page
    '''
    # Handle infinite redirects
    if is_infinite_redirect(url):
        return []
    
    # Handle large files and non-textual content
    if is_large_file(resp):
        return []  # Avoid large files

    # Check for infinite traps
    if is_infinite_trap(url) or is_infinite_redirect(url):
        return []

    # Avoid recursive paths
    if has_recursive_pattern(url):
        return []
    
    # records all ics.uci.edu subdomains
    url_parsed = urlparse(url)
    url_parsed = url_parsed.scheme + "://" + url_parsed.hostname
    if ("ics.uci.edu" in url_parsed):
        if url_parsed in ics_frequencies:
            ics_frequencies[url_parsed] += 1
        else:
            ics_frequencies[url_parsed] = 1    
        
    # skip if url is already in the queue
    if url in frontier.to_be_downloaded: 
        return []
    
    # Status Code 301: redirect to permananent new location
    # Status Code 307: redirect to temporary new location
    if resp.status > 300 and resp.status < 309:
        if is_valid(resp.headers['Location']):
            return [resp.headers['Location']]     
            
    # handle poor connection issues, including 404
    if resp.status != 200: 
        return []
    
    links = extract_next_links(url, resp, frontier, word_frequencies, longest_url)
    
    
    # return scraped urls
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
    


    urls_found = []
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    anchor_tags = soup.find_all("a")
    text = soup.get_text()

    # if text has low information value, then skip
    if len(text) < 500:
        print("skipping because of low information value")
        return []

     # for every anchor tag, append
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

    # do we need this line? yeah its used for tokenizeString
    text = soup.get_text()

    listOfTokens = tokenFunctions.tokenizeString(text)

    # updates the url with the most tokens
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
            r".*\.(css|js|bmp|gif|jpe?g|ico|img|png|jpg|jpeg|pdf|ai|gif|raw|psd|eps"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|ppsx|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|war|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

