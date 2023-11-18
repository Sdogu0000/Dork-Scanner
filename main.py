from requests_html import HTMLSession
import signal
import sys

class Search:
    base_url = 'https://www.bing.com'
    parameters = '/search?q={}'

    def __init__(self, site):
        self.site = site
        self.should_stop = False
        self.found_links = set()

    def read_dorks(self, dorks_file):
        with open(dorks_file, 'r') as file:
            dorks = file.readlines()
        return [dork.strip() for dork in dorks]

    def is_valid(self, link):
        return '=' in link

    def find_links(self, dorks):
        session = HTMLSession()
        session.headers['user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'

        for dork in dorks:
            url = self.base_url + self.parameters.format(f"site:{self.site} {dork}")

            try:
                html = session.get(url).html
            except:
                continue

            links = set()
            for r in html.find('.b_algo'):
                a = r.find('h2', first=True).find('a', first=True)
                try:
                    link = a.attrs['href']
                except:
                    continue

                if self.is_valid(link):
                    links.add(link)

            new_links = links - self.found_links
            if new_links:
                print(f"Dork: {dork} - Found! Links: {', '.join(new_links)}")
                self.found_links.update(new_links)

            if self.should_stop:
                print(" Terminated by user.")
                sys.exit(0)

        if not self.found_links:
            print("No dorks found.")

    def stop_search(self, signum, frame):
        self.should_stop = True


site = input("Enter the target site (Ex: example.com): ")
dorks_file = "dorks.txt"


search = Search(site)


signal.signal(signal.SIGINT, search.stop_search)

dorks = search.read_dorks(dorks_file)
search.find_links(dorks)
