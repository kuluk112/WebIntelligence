import time
from urllib.parse import urlparse
from urllib import robotparser
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
from nltk import ngrams
from queue import PriorityQueue
import random
import hashlib



class BackQueue:
    def __init__(self):
        self.queue = []
        self.host = None


class FrontQueue:
    def __init__(self, priority):
        self.priority = priority
        self.queue = []


class Page:
    def __init__(self, url_object):
        self.url = url_object
        self.out_links = []
        self.sketch = ()
        self.hashed_supershingles = ()
        self.content = ""
        self.pagerank = 0


class HeapNode():
    def __init__(self,time,backqueue):
        self.allow_at_time = time
        self.backqueue = backqueue

    def __cmp__(self, other):
        return min(self.allow_at_time, other.allow_at_time)

    def __lt__(self, other):
        return self.allow_at_time <= other.allow_at_time


class Crawler:
    def __init__(self, priorities, threads, politeness_sec):
        self.politeness_sec = politeness_sec
        self.priorities = priorities
        self.timing_heap = PriorityQueue()
        self.page_list = []
        self.robot_dictionary = {}
        self.front_queues = []
        self.back_queues = []
        for i in range(1,priorities+1):
            self.front_queues.append(FrontQueue(i))
        for i in range(0,  threads * 3):
            self.back_queues.append(BackQueue())

    def run_crawler(self,seed, number_of_pages):
        self.initialize_from_seed(seed)

        while len(self.page_list)< number_of_pages:
            print(len(self.page_list))
            url, heapnode = self.fetch_url_from_backqueue()
            print(url.geturl())

            heapnode, delay, visit_allowed = self.handle_robot(url,heapnode)

            if visit_allowed:
                page = self.fetch_webpage(url)
                heapnode.allow_at_time = time.time() + delay
                self.timing_heap.put(heapnode)
                if self.is_duplicate(page) is False:
                    self.page_list.append(page)
                    self.expand_frontqueues(page)
            else:
                self.timing_heap.put(heapnode)
                print(url.geturl())


    def handle_robot(self,url_object, heapnode):
        try:
            robot = self.get_robot(url_object)
        except:
            heapnode.allow_at_time = time.time() + self.politeness_sec
            return heapnode, self.politeness_sec, False

        try:
            delay = robot.crawl_delay("*")
        except:
            delay = self.politeness_sec
            #heapnode.allow_at_time = time.time() + self.politeness_sec

        if delay is None or delay < self.politeness_sec:
            delay = self.politeness_sec

        time.sleep(delay)

        visit_allowed = True
        if not robot.can_fetch("*", url_object.geturl()):
            heapnode.allow_at_time = time.time() + delay
            visit_allowed = False

        return heapnode, delay, visit_allowed


    def get_robot(self,url_object):
        url = str(url_object.scheme) + "://" + str(url_object.netloc) + "/robots.txt"
        rp = robotparser.RobotFileParser()
        rp.set_url(url)
        rp.read()
        self.robot_dictionary[url_object.netloc] = rp
        return rp


    def initialize_from_seed(self, seed):
        url_object = urlparse(seed)
        page = self.fetch_webpage(url_object)
        self.page_list.append(page)
        self.expand_frontqueues(page)
        heap_entry = HeapNode(0,self.back_queues[0])
        self.timing_heap.put(heap_entry)

    def expand_frontqueues(self, page):
        for i in page.out_links:
            url_object = urlparse(i)
            self.front_queues[random.randint(0,self.priorities - 1)].queue.append(url_object)

    def fetch_url_from_backqueue(self):
        if self.timing_heap.empty():
            print("stop")

        heap_node = self.timing_heap.get()
        if not heap_node.backqueue.queue:
            self.fetch_from_frontqueue()
            heap_node = self.timing_heap.get()
        backqueue = heap_node.backqueue
        url_to_visit = backqueue.queue.pop(0)

        return url_to_visit, heap_node

    def fetch_from_frontqueue(self):
        empty_backqueue = True

        while empty_backqueue:
            index = random.randint(0,self.priorities-1)
            if not self.front_queues[index].queue:
                continue
            else:
                url_object = self.front_queues[index].queue.pop(0)
            host_match = False
            for backqueue in self.back_queues:
                if backqueue.host is url_object.netloc:
                    backqueue.queue.append(url_object)
                    host_match = True
                    break

            if not host_match:
                for backqueue in self.back_queues:
                    if not backqueue.queue:
                        backqueue.queue.append(url_object)
                        backqueue.host = url_object.netloc
                        if url_object.netloc in self.robot_dictionary:
                            robot = self.robot_dictionary[url_object.netloc]
                            try:
                                delay = robot.crawl_delay("*")
                                if delay is None:
                                    time = self.politeness_sec + robot.mtime()
                                else:
                                    time = delay + robot.mtime()
                            except AttributeError:
                                time = self.politeness_sec + robot.mtime()

                            heapentry = HeapNode(time, backqueue)
                            self.timing_heap.put(heapentry)
                        else:
                            heapentry = HeapNode(0, backqueue)
                            self.timing_heap.put(heapentry)
                        break
            empty_backqueue = False
            for backqueue in self.back_queues:
                if not backqueue.queue:
                    empty_backqueue = True

    def is_duplicate(self, new_page, threshold_super_shingle=2, threshold_similarity=0.9):
        if new_page is None:
            return True
        is_duplicate = False

        for page in self.page_list:
            if len(page.hashed_supershingles.intersection(new_page.hashed_supershingles)) >= threshold_super_shingle:
                if len(page.sketch.intersection(new_page.sketch))/ len(page.sketch.union(new_page.sketch)) >= threshold_similarity:
                    is_duplicate = True
                    return is_duplicate
        return is_duplicate



    def fetch_webpage(self,url):

        page = Page(url)
        try:
            response = urllib.request.urlopen(page.url.geturl())
        except urllib.error.HTTPError:
            return None
        except UnicodeEncodeError:
            return None
        soup = BeautifulSoup(response, 'html.parser')
        links = []
        for link in soup.find_all('a', href=True):
            links.append(link['href'])
        links = self.cleanse_links(links)

        for script in soup(["script", "style"]):
            script.decompose()  # rip it out

        # get text
        text = soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        page.content = text
        sketch, hashed_super_shingles = self.make_hashed_shingles_and_super_shingles(page.content)
        page.sketch = sketch
        page.hashed_supershingles = hashed_super_shingles
        page.out_links = links
        return page

    def cleanse_links(self, links):
        result_links = []
        for i in links:
            if i.startswith("http"):
                result_links.append(i)
        return result_links

    def make_hashed_shingles_and_super_shingles(self, content, shingle_size=8, super_shingle_size=6, seed=1234,
                                                permutations=84):
        random.seed(seed)
        random_ints = []
        for i in range(permutations):
            random_ints.append(random.randint(0, 10 ** 42))
        sketch = set()
        hashed_shingles = set()
        shingles = ngrams(content.split(), shingle_size)
        shingles_set = set()
        for shingle in shingles:
            shingles_set.add(shingle)

        for permutation in random_ints:
            for shingle in shingles_set:
                hashcode = hashlib.md5(str(shingle).encode('utf-8')).hexdigest()
                value = int(hashcode, 16)
                hashed_shingles.add(value ^ permutation)
            if len(hashed_shingles) is 0:
                return set(), set()
            sketch.add(min(hashed_shingles))
            hashed_shingles.clear()

        hashed_super_shingles = set()
        sketch_list = list(sketch)
        super_shingle_set = set()
        elements_in_sketches = len(sketch)

        non_overlapping_super_sketches = [sketch_list[i * super_shingle_size:(i + 1) * super_shingle_size] for i in
                                          range((
                                                            elements_in_sketches + super_shingle_size - 1) // super_shingle_size)]

        for super_shingle in non_overlapping_super_sketches:
            super_shingle_set.add(str(super_shingle))

        for super_shingle in super_shingle_set:
            hashcode = hashlib.md5(str(super_shingle).encode('utf-8')).hexdigest()
            value = int(hashcode, 16)
            hashed_super_shingles.add(value)

        return sketch, hashed_super_shingles

