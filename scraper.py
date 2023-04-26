import re, time
from urllib.parse import urlparse
from bs4 import BeautifulSoup 
import time

MIN_CONTENT_LENGTH = 500
MAX_CONTENT_LENGTH = 100000
crawled = set()
def scraper(url, resp):
    links = extract_next_links(url, resp)
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
    
    # Correctness:
    # Honor the politeness delay for each site - 0.5s
    # Crawl all pages with high textual information content - #
    # Detect and avoid infinite traps - #
    # Detect and avoid sets of similar pages with no information - /#
    # Detect redirects and if the page redirects your crawler, index the redirected content - /#
    # Detect and avoid dead URLs that return a 200 status but no data - /#
    # Detect and avoid crawling very large files, especially if they have low information value -/#
    # Make sure to add relative links to current and return - #
    # time.sleep(0.5) // Already use politeness in config

    # if (resp.status >= 400 or resp.status == 204):
    #     
    #     return list()

    # Check if the response status is 200 (OK)
    if resp.status != 200:
        print(1)
        return []

    # Check the content length before processing the URL
    if len(resp.raw_response.content) < MIN_CONTENT_LENGTH:
        print(2)
        return []

    # Check the content length before processing the URL
    if len(resp.raw_response.content) > MAX_CONTENT_LENGTH:
        print(3)
        return []

    # check duplicates/infinite loop
    dup = set(url)

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')

        #links.append(href)

        # check relative path
        if href and (href.startswith('.') or href.startswith('/')):
            abs_url = url + href
            # delete fragments
            if "#" in abs_url:
                abs_url = abs_url.split('#')[0]
            # check for duplicates
            if abs_url not in dup and abs_url not in crawled:
                links.append(abs_url)
                dup.add(abs_url)
                crawled.add(abs_url)
            continue
        parsed_href = urlparse(href)
        # Check if the URL is valid
        ori_parsed = urlparse(url)
        if parsed_href.scheme and parsed_href.netloc == ori_parsed.netloc:
            # check for duplicates
            if href not in dup and href not in crawled:
                # delete fragments
                if "#" in href:
                    href = href.split('#')[0]
                links.append(href)
                dup.add(href)
                crawled.add(href)
    # print(links)
    # print(len(links))
    # exit()
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if "redirect" in url:
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
