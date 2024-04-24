from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from collections import defaultdict


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        # self.crawler_logger = get_logger(f"Worker-{worker_id}", "CRAWLER")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        word_frequencies = dict()
        longest_url = ["",0]
        ics_frequencies = dict()
        subdomains = defaultdict(int)

        count = 0
        while True:
            tbd_url = self.frontier.get_tbd_url()

            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break

            # get number of words method?
            if not scraper.is_valid(tbd_url):
                continue
            
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp, self.frontier, word_frequencies, longest_url, ics_frequencies)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url) 
            if (count % 50 == 0):   # every 500 pages, print to add on something
                print("******************************************************")
                print("******************************************************")
                print("number of unique pages: ", self.frontier.numberOfUniquePages)
                print("longest url is: ", longest_url[0], "which had", longest_url[1], "words")
                self.print_most_common_words(word_frequencies, False)
                self.print_ics_websites(ics_frequencies, False)
                print("******************************************************")
                print("******************************************************")
            count += 1
            time.sleep(self.config.time_delay)

        print("******************************************************")
        print("******************************************************")
        print("number of unique pages: ", self.frontier.numberOfUniquePages)
        print("longest url is: ", longest_url[0], "which had", longest_url[1], "words")
        print(word_frequencies, False)
        print(ics_frequencies, False)
        print("******************************************************")
        print("******************************************************")

    def print_most_common_words(self, frequencies: dict, log: bool):
        frequencies = sorted(frequencies.items(), key=lambda item: -item[1])
        to_print = []
        for i in range(50):
            to_print.append(frequencies[i][0])
            if log:
                # self.crawler_logger.info(frequencies[i][0])
                pass
        print(to_print)
    
    def print_ics_websites(self, websites: dict, log: bool):
        websites = sorted(websites.items())  # list of tuples
        to_print = []
        for pair in websites:
            if (pair[0] == "https://www.ics.uci.edu" or pair[0] == "http://www.ics.uci.edu"):  # skip the actual ics website
                continue
            to_print.append(f"{pair[0]}, {pair[1]}")

        if log:
            # self.crawler_logger.info(f"{pair[0]}, {pair[1]}")
            pass    
        print(to_print)



