import time
from urllib.parse import urlparse
from urllib import robotparser
import urllib.request
import re
from bs4 import BeautifulSoup
from queue import PriorityQueue
import random
import heapq


class BackQueue:
    def __init__(self):
        self.queue = []
        self.host = None

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
    def __init__(self, url, robot, next_visit):
        Page.__init__(self, url)
        self.robot = robot
        self.next_visit = next_visit


class Crawler:
    def __init__(self, priorities, threads):
        self.datalist = []
        self.priorities = priorities
        self.root_pages = []
        self.visited_pages = []
        self.timing_heap = PriorityQueue()
        self.page_list = []
        self.front_queues = []
        self.back_queues = []
        self.blacklist = []
        for i in range(1,priorities+1):
            self.front_queues.append(FrontQueue(i))
        for i in range(0,  threads * 3):
            self.back_queues.append(BackQueue())


    def make_root_page(self, url_obj, robot):
        url = str(url_obj.scheme) + "://" + str(url_obj.netloc)

        if robot.can_fetch("*", url):
            delay = robot.crawl_delay("*")
            if delay is None:
                delay = 2
            next_visit = time.time() + delay
            root_page = RootPage(url_obj, robot, next_visit)
            self.root_pages.append(root_page)
            return root_page
        else:
            self.blacklist.append(url_obj.netloc)
            return None

    def request_url_from_queue(self):
        ready = False
        queue = None
        while not ready:
            if self.timing_heap.qsize() == 0:
                print("empty queue")
            available = self.timing_heap._get()
            t = time.time()
            if time.time() > available[0]:
                ready = True
            else:
                self.timing_heap._put(available)

        val = available[1]
        for i in self.back_queues:
            if i.host == val.url.netloc:
                queue = i
                break
        if queue is None:
            print("kritisk")
        if len(queue.queue) > 0:
            item = queue.queue.pop(0)
            return item
        else:
            self.query_front_queue(queue)
            return None


    def query_front_queue(self, queue):
        i = 0
        inserted = False
        #queue is a Backqueue --> it contains a queue
        while len(queue.queue) == 0:
            if len(self.front_queues[i].queue) < 1:
                i = self.increment_q_count(i)
                continue
            popped = self.front_queues[i].queue.pop(0)
            for j in self.back_queues:
                if j.host == popped.url.netloc:
                    j.queue.append(popped)
                    inserted = True
                    if queue.host == j.host:
                        for k in self.root_pages:
                            if k.url.netloc == popped.url.netloc:
                                self.timing_heap._put((k.next_visit, k))
                    break
            if not inserted:
                found = False
                for n in self.back_queues:
                    if len(n.queue) == 0:
                        n.queue.append(popped)
                        n.host = popped.url.netloc
                        for j in self.root_pages:
                            if j.url.netloc == popped.url.netloc:
                                self.timing_heap._put((j.next_visit, j))
                                found = True
                                break
                        if not found:
                            rp = self.visit_robot(popped.url)
                            new_root_page = self.make_root_page(popped.url, rp)
                            self.timing_heap._put((new_root_page.next_visit, new_root_page))
                            break




    def increment_q_count(self, i):
        i += 1
        if i == 3:
            return 0
        else:
            return i

    def crawl(self, seed):
        #self.visited_pages.append(seedpage)
        #list_with_seed_only = [seed]
        #self.prioritize_links(list_with_seed_only)
        links = []
        seedpage = Page(urlparse(seed))
        self.page_list.append(seedpage)
        self.back_queues[1].queue.append(seedpage)
        self.back_queues[1].host = seedpage.url.netloc
        rp = self.visit_robot(seedpage.url)
        root_page = self.make_root_page(seedpage.url, rp)

        self.timing_heap._put((root_page.next_visit, root_page))

        #self.back_queues[1].host = seedpage.url.netloc
        #self.root_pages.append(())

        while len(self.datalist) < 10:
            content = str()
            root_page = None
            page = self.request_url_from_queue()
            if page is None:
                continue

            rp = self.visit_robot(page.url)
            if not (isinstance(rp, RootPage)):
                root_page = self.make_root_page(page.url, rp)
                t = time.time()
                while t < root_page.next_visit:
                    t = time.time()
                if rp.can_fetch("*", page.url.geturl()):
                    content, links = self.extract_and_update_next_visit(page, root_page)
                    self.timing_heap._put((root_page.next_visit, root_page))
                    if content is None: #request failure
                        self.page_list.remove(page)
                        continue
                else:
                    continue
            else:
                    if rp.robot.can_fetch("*", page.url.geturl()):
                        content, links = self.extract_and_update_next_visit(page, rp)
                        self.timing_heap._put((rp.next_visit, rp))
                        if content is None:  # request failure
                            self.page_list.remove(page)
                            continue
                        self.page_list.remove(page)
                    else:
                        continue
            if True: #check for duplicates
                if content is not None:
                    page.content = content
                    self.datalist.append(content)
            if len(links) > 0:
                self.prioritize_links(page, links)



    def extract_and_update_next_visit(self, page, root_page):
        delay = root_page.robot.crawl_delay("*")
        if delay is None:
            root_page.next_visit = time.time() + 1
        else:
            root_page.next_visit = time.time() + delay
        content, links = self.extract_from_webpage(page.url)
        if content is None: #error occured in request
            return None, None
        return content, links

    def prioritize_links(self, page: Page, links):
        for i in links:
            url_object = urlparse(i)
            if url_object.netloc in self.blacklist:
                continue
            else:
                newpage = Page(url_object)
                self.front_queues[random.randint(0,self.priorities - 1)].queue.append(newpage)
                self.page_list.append(newpage)
                newpage.in_links.append(page)
                page.out_links.append(newpage)


    def visit_robot(self, url_obj):
        lookup = None
        for i in self.root_pages:
            if url_obj.netloc == i.url.netloc:
                lookup = i
        if lookup is not None:
            return lookup
        if len(str(url_obj.netloc)) < 1:
            print("robot fejl")
        url = str(url_obj.scheme) + "://" + str(url_obj.netloc) + "/robots.txt"
        rp = robotparser.RobotFileParser()
        rp.set_url(url)
        rp.read()

        return rp



    def extract_from_webpage(self, url):

        try:
            response = urllib.request.urlopen(url.geturl())
        except:
            return None, None

        soup = BeautifulSoup(response, 'html.parser')
        links = []
        for link in soup.find_all('a', href=True):
            links.append(link['href'])
        links = self.cleanse_links(links)
        text = soup.text
        return text, links


    def cleanse_links(self, links):
        result_links = []
        for i in links:
            if "http" in i:
                result_links.append(i)
        return result_links
'''
crawler = Crawler(3, 1)
crawler.crawl("https://stackoverflow.com")
print ("dwa")
'''