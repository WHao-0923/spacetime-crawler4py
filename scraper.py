import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup 

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
    # Crawl all pages with high textual information content
    # Detect and avoid infinite traps
    # Detect and avoid sets of similar pages with no information
    # Detect redirects and if the page redirects your crawler, index the redirected content
    # Detect and avoid dead URLs that return a 200 status but no data (click here to see what the different HTTP status codes mean Links to an external site.)
    # Detect and avoid crawling very large files, especially if they have low information value
    
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        #print(is_valid(href))
        #print("ori: ",href)
        if href and is_valid(href):
            parsed_href = urlparse(href)
            #print("parsed: ",parsed_href)
            # Check if the URL is valid
            #print(parsed_href.scheme, parsed_href.netloc)
            ori_parsed = urlparse(url)
            if parsed_href.scheme and parsed_href.netloc == ori_parsed.netloc:
                links.append(href)
    #print(links)
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
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
