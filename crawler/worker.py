from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time


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
        word_frequencies = dict()
        longest_url = ["",0]
        ics_frequencies = dict()
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
            time.sleep(self.config.time_delay)


        print("number of unique pages: ", self.frontier.numberOfUniquePages)
        print("longest url is: ", longest_url[0], "which appeared ", longest_url[1], "times")
        self.print_most_common_words(word_frequencies)
        self.print_ics_websites(ics_frequencies)

    def print_most_common_words(self, frequencies: dict):
        frequencies = sorted(frequencies.items(), key=lambda item: -item[1])
        for i in range(50):
            print(frequencies[i][0])
    
    def print_ics_websites(self, websites: dict):
        websites = sorted(websites.items())
        for pair in websites:
            if (pair[0] == "https://www.ics.uci.edu" or pair[0] == "http://www.ics.uci.edu"):  # skip the actual ics website
                continue
            print(f"{pair[0]}, {pair[1]}")


