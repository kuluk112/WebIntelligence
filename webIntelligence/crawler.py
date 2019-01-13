import urllib3.request
from urllib.parse import urlparse
from urllib import robotparser
import re
from bs4 import BeautifulSoup
from queue import PriorityQueue
import random


class BackQueue:
    def __init__(self):
        self.queue = []

class FrontQueue:
    def __init__(self, priority):
        self.priority = priority
        self.queue = []

class Page:
    def __init__(self, url):
        self.url = url
        self.in_links = []
        self.out_links = []
class RootPage(Page):
    def __init__(self, url, robot):
        Page.__init__(self,url)
        self.robot = robot

class Crawler:
    def __init__(self, priorities,threads):
        self.priorities = priorities
        self.root_pages = []
        self.visited_pages = []
        self.last_visited = PriorityQueue()
        self.page_list = []
        self.front_queues = []
        self.back_queues = []
        self.blacklist = []
        for i in range(1,priorities+1):
            self.front_queues.append(FrontQueue(i))
        for i in range(0,  threads):
            self.back_queues.append(BackQueue())


    def parse_url(self, url):
        result = urlparse(url)
        root = result.netloc
        path = result.path
        return root, path

    def crawl(self, seed):
        seedpage = Page(urlparse(seed))
        self.visited_pages.append(seed)
        #self.last_visited.put((time, seedpage.url.netloc))
        content, links = self.extract_from_webpage(seed)
        self.prioritize_links(links)
        seedpage.content = content

        #while len(self.page_list) < 1000:


    def prioritize_links(self, links):
        for i in links:
            url_object = urlparse(i)
            if url_object.netloc in self.blacklist:
                continue
            else:
                 next_visit = self.visit_robot(url_object)
            self.front_queues[random.randint(0,self.priorities - 1)].append(i)

    def visit_robot(self, url_obj):
        url = str(url_obj.scheme) + "://" + str(url_obj.netloc)
        url2 = url + "/robots.txt"
        rp = robotparser.RobotFileParser()
        rp.set_url(url2)
        rp.read()
        print(rp.can_fetch("008",url))


    def extract_from_webpage(self, url):
        http = urllib3.PoolManager()
        response = http.request('GET', url)
        html = BeautifulSoup(response, 'html.parser')
        links = [a['href'] for a in html.find_all('a')]
        text = html.text
        return text, links

obj = urlparse("http://www.stackoverflow.com/questions")
crawler = Crawler(1,1)
crawler.visit_robot(obj)


def run():
    crawler = Crawler()

