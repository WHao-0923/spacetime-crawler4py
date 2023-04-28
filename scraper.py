import re, time, tokenize, hashlib, nltk
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from utils.count_words import tokenize
nltk.download('stopwords')
nltk.download('punkt')
from collections import defaultdict, Counter
from crawler.report import Report


MIN_CONTENT_LENGTH = 500
MAX_CONTENT_LENGTH = 100000
OK_counter = 0
NotOK_counter = 0
MAX_word_count = 0
dup = set()
fingerprints = set()
word_frequency_dict = {}
ics_subdomain_dict = {}




def scraper(url, resp):
    links = extract_next_links(url, resp)
    if (urlparse(url).netloc).endswith("ics.uci.edu"):
        output_file1 = "Logs/subdomain_counts.txt"
        with open(output_file1, 'w') as f:
            f.write(f"{urlparse(url).netloc}, {len(links)}\n")
        # output_file2 = "Logs/word_counts.txt"
        # with open(output_file2, 'w') as f:
        #     f.write(f"{}\n")    

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
    

    # Check if the response status is 200 (OK)
    if resp.status != 200:
        global NotOK_counter
        NotOK_counter += 1
        print("number of page crawled that is bad: ", NotOK_counter)
        return []
    else:
        global OK_counter 
        OK_counter += 1
        print("number of page crawled that is ok: ", OK_counter)


    # Check if the content length is within the desired range
    if len(resp.raw_response.content) < MIN_CONTENT_LENGTH or len(resp.raw_response.content) > MAX_CONTENT_LENGTH:
        OK_counter -= 1
        return []


    # Initialize a set to store unique URLs
    dup.add(url)

    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")

    # Extract the text content of the page
    text = soup.get_text()

    
    global word_frequency_dict
    word_count, word_frequency_dict = tokenize_and_count_max(text, word_frequency_dict)
    print("word in this page", word_count)


    #update the max word counter
    global MAX_word_count
    if word_count > MAX_word_count:
        MAX_word_count = word_count
        print("Max word of a page is updated to ", word_count)


    # get fingerprint of current page -- XX
    fingerprint = simhash(text)
    for fp in fingerprints:
        if is_similar(fp,fingerprint):
            print("High similarity")
            OK_counter -= 1
            return []
    fingerprints.add(fingerprint) 
    
    # count the word in this page and update the final frequency dictionary
    # tokenize(url,text)

    if (urlparse(url).netloc[3:] == ".stat.uci.edu"):
        key = urlparse(url).netloc[:3] + ".stat.uci.edu"
        global ics_subdomain_dict
        ics_subdomain_dict[key]  = ics_subdomain_dict.get(key, 0) + 1
        print(ics_subdomain_dict)

    # Initialize an empty list to store the extracted links
    links = []

    # Iterate over all 'a' tags in the HTML content
    for link in soup.find_all('a'):

        # Get the 'href' attribute of the link
        href = link.get('href')

        # If the 'href' attribute exists
        if href:
            # Use urljoin to combine the base URL and the relative URL
            abs_url = urljoin(url, href)

            # Remove any URL fragment if present
            if "#" in abs_url:
                abs_url = abs_url.split('#')[0]


            # Normalize the URL by removing the trailing slash
            abs_url = abs_url.rstrip('/')
            #print(abs_url)
            

            # Check if the absolute URL has the same domain as the base URL
            

            if (urlparse(abs_url).netloc).endswith(urlparse(url).netloc[3:]):

                # Check if the absolute URL is not a duplicate and has not been crawled already
                if abs_url not in dup:
                    # Append the absolute URL to the list of extracted links
                    links.append(abs_url)
                    # Add the absolute URL to the sets of unique URLs and crawled URLs
                    dup.add(abs_url)
    
    #print(len(dup))
    #print('\n'.join(dup))
    #print(len(dup))
    #exit()

    Report.scraped.add(url)

    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False
        if urlparse(url).netloc.endswith('ics.uci.edu'):
            Report.unique_urls.add(url)
        return True


    except TypeError:
        print ("TypeError for ", parsed)
        raise

def simhash(text):
    # Count the weight of each token
    weights = {}
    for token in text.split():
        weights[token] = weights.get(token, 0) + 1
    # Hash the tokens for each token
    hashes = {}
    for token, weight in weights.items():
        hash_value = int(hashlib.sha256(token.encode('utf-8')).hexdigest(), 16)
        hashes[token] = hash_value
    # Transfer the hash result to binary for each token
    binary_hashes = {}
    for token, hash_value in hashes.items():
        binary_hashes[token] = bin(hash_value)[2:].zfill(64)
    # Vector V formed by summing weights
    V = [0] * 64
    for token, weight in weights.items():
        for i in range(64):
            if binary_hashes[token][i] == '1':
                V[i] += weight
            else:
                V[i] -= weight
    # 64-bit fingerprint formed from V
    fingerprint = 0
    for i in range(64):
        bit = 1 if V[i] >= 0 else 0
        fingerprint |= bit << i
    #print(fingerprint)
    return fingerprint

def is_similar(fingerprint1, fingerprint2):
    distance = bin(fingerprint1 ^ fingerprint2).count('1')
    similarity = 1 - float(distance/64.0)
    #print(f"Distance: {distance}, Similarity: {similarity}")
    return similarity > 0.95

def tokenize_and_count_max(text, word_freq):
    stop_words = set(stopwords.words("english"))
    #nltk to tokenize the text provided
    tokens = word_tokenize(text)

    #update the word_frequency dictionary and give the word count of this page
    for token in tokens:
        word = token.lower()
        if word.isalnum() and word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    return len(tokens), word_freq

