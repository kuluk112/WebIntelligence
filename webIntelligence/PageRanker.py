import random
from urllib.parse import urlparse


class PageRanker:
    def __init__(self, connected_pages):

        self.matrix_size = len(connected_pages)
        self.page_list = connected_pages
        self.transition_probability_matrix = self.init_matrix(self.matrix_size)
        self.alpha = 0.10 #teleport probability

    def init_matrix(self, size):
        matrix = []
        for i in range(0,size):
            inner_list = []
            for i in range(0,size):
                inner_list.append(float(0))
            matrix.append(inner_list)
        return matrix

    def insert_connections(self):
        x = 0
        for outer in self.page_list:
            divisor = len(outer.out_links)
            y = 0
            for inner in self.page_list:
                if outer.url.geturl() == inner.url.geturl():
                    y += 1
                    continue
                for link in outer.out_links:
                    if link.geturl() == inner.url.geturl():
                        if divisor != 0:
                            self.transition_probability_matrix[x][y] = 1/divisor
                        else:
                            self.transition_probability_matrix[x][y] = 0
                y += 1
            x += 1

    def enable_teleportation(self):
        x = 0
        for outer in self.page_list:
            divisor = len(outer.out_links)
            y = 0
            for inner in self.page_list:
                if divisor != 0:
                    self.transition_probability_matrix[x][y] = ((1 - self.alpha) * self.transition_probability_matrix[x][y]) + (self.alpha * (1 / self.matrix_size))
                else:
                    self.transition_probability_matrix[x][y] = 1/self.matrix_size
                y += 1
            x += 1

    def page_rank(self, iterations):
        surfer = self.init_surfer()
        for iteration in range(0, iterations):
            surfer2 = self.init_surfer2()
            for i in range(0, self.matrix_size):
                val = 0
                for j in range(0, self.matrix_size):
                    val += surfer[j] * self.transition_probability_matrix[j][i]
                surfer2[i] = val
            surfer = surfer2
        return surfer

    def init_surfer2(self):
        surfer = []
        for i in range(0, self.matrix_size):
            surfer.append(float(0))
        return surfer

    def init_surfer(self):
        surfer = []
        for i in range(0, self.matrix_size):
            surfer.append(float(0))

        surfer[random.randint(0, self.matrix_size - 1)] = 1
        return surfer

#((1 - self.alpha) * 1/divisor) + (self.alpha * (1 / self.matrix_size))
    def remove_excessive_out_links(self):
        good_links = []
        page_list = []
        for i in self.page_list:
            for j in i.out_links:
                url_obj = urlparse(j)

                if url_obj.geturl() == i.url.geturl():
                    break

                for k in self.page_list:
                    if k.url.geturl() == url_obj.geturl():
                        good_links.append(url_obj)
                        break
            i.out_links = good_links
            page_list.append(i)
            good_links = []
        self.page_list = page_list



    def give_pageranks(self):

        self.remove_excessive_out_links()

        self.insert_connections()   #Transition_probability-matrix
        self.enable_teleportation() 

        pageranks = self.page_rank(200)

        for i in range(len(pageranks)):
            self.page_list[i].pagerank = pageranks[i]

def print_matrix(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            print(matrix[i][j], end=' ')
        print()

