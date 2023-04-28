from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
import os




class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.") 
                with open("myreport", 'r+') as file:
                    file.truncate(0)
                    file.write("Total unique page crawled: " + str(scraper.Total_counter) + "\n")
                    file.write("longest page in terms of the number of words: " + str(scraper.MAX_word_count_url) + " with " + str(scraper.MAX_word_count) + " words\n")
                    sorted_dict = sorted(scraper.word_frequency_dict.items(), key=lambda x: -x[1])
                    file.write("50 most common word:\n")
                    count = 0
                    for item in sorted_dict:
                        if count == 50:
                            break
                        file.write(f"{item[0]} -> {item[1]} \n")
                        count += 1
                    sorted_dict1 = sorted(scraper.ics_subdomain_dict.items())
                    file.write("pages in subdomains:\n")
                    for item in sorted_dict1:
                        file.write(f"{item[0]}, {item[1]}\n")
                print("report initialized in dirctory: \"spacetime-crawler4py\"")
                print()
                break
            
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
        
