import nltk
import math
from nltk import ngrams
import string
import hashlib
import random

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize



class DocumentValues:
    def __init__(self):
        self.tf = 1
        self.tf_star = 0
        self.tf_idf = 0
        self.weight = 0
        self.normalized = 0

class RowEntry:
    def __init__(self, document):
        self.df = 1
        self.documents = [document]
        self.idf = 0
        self.query_weight = 0


class Document:
    def __init__(self, page=None, document_id=None, query=None):
        if page is not None:
            self.term_dictionary = {}
            self.page = page
            self.content = page.content
            self.document_id = document_id
            self.product = 0
            self.weight_sum_not_squared = 0
        else:
            self.term_dictionary = {}
            self.query = query

def tokenize(input):
    ps = PorterStemmer();
    stop_words = ["a","about","above","after","again","against","all","am","an","and","any","are","arent","as","at",
                  "be","because","been","before","being","below","between","both","but","by","cant","cannot","could",
                  "couldnt","did","didnt","do","does","doesnt","doing","dont","down","during","each","few","for","from",
                  "further","had","hadnt","has","hasnt","have","havent","having","he","hed","hell","hes","her","here",
                  "heres","hers","herself","him","himself","his","how","hows","i","id","ill","im","ive","if","in",
                  "into","is","isnt","it","its","its","itself","lets","me","more","most","mustnt","my","myself","no"
        ,"nor","not","of","off","on","once","only","or","other","ought","our","ours","ourselves","out","over","own",
                  "same","shant","she","shed","shell","shes","should","shouldnt","so","some","such","than","that",
                  "thats","the","their","theirs","them","themselves","then","there","theres","these","they","theyd",
                  "theyll","theyre","theyve","this","those","through","to","too","under","until","up","very","was",
                  "wasnt","we","wed","well","were","weve","were","werent","what","whats","when","whens","where",
                  "wheres","which","while","who","whos","whom","why","whys","with","wont","would","wouldnt","you",
                  "youd","youll","youre","youve","your","yours","yourself","yourselves"]
    tr = str.maketrans("", "", string.punctuation)
    normalized = input.translate(tr).casefold()

    tokens = nltk.word_tokenize(normalized)
    tokens_without_stopwords = [ps.stem(i) for i in tokens if i not in stop_words]
    return tokens_without_stopwords

tokenize("Hey. What are you doing? I'm running.")

def create_inverted_index_from_pages(pages):
    inverted_index = {}
    document_list = []

    document_id = 0
    for page in pages:
        document = Document(page, document_id)
        document_list.append(document)
        for term in document.content:
            if term not in inverted_index:
                inverted_index[term] = RowEntry(document)
                document.term_dictionary[term] = DocumentValues()
            elif term not in document.term_dictionary:
                inverted_index[term].df += 1
                inverted_index[term].documents.append(document)
                document.term_dictionary[term] = DocumentValues()
            else:
                document.term_dictionary[term].tf += 1
        document_id += 1
    calc_ranking(inverted_index, len(document_list))
    return inverted_index

def calc_ranking(inverted_index, number_of_documents):
    calc_tf_star(inverted_index)
    calc_idf(inverted_index,number_of_documents)
    calc_tf_idf(inverted_index,number_of_documents)

def calc_score(query,inverted_index):
    tokenized_query = tokenize(query)
    query_document = Document(id=-1, query=query)
    #Need tf*-idf for query

def create_query_document(query):
    tokenized_query = tokenize(query)
    query_document = Document(query=tokenized_query)
    return create_inverted_index_from_query(query_document)


def create_inverted_index_from_query(document):
    inverted_index = {}

    for term in document.query:
        if term not in inverted_index:
            inverted_index[term] = RowEntry(document)
            document.term_dictionary[term] = DocumentValues()
        elif term not in document.term_dictionary:
            inverted_index[term].df += 1
            document.term_dictionary[term] = DocumentValues()
        else:
            document.term_dictionary[term].tf += 1
    calc_tf_star(inverted_index)
    return inverted_index


def calc_tf_star(inverted_index):
    for key, value in inverted_index.items():
        print("test")
        for document in value.documents:
            document_values = document.term_dictionary[key]
            document_values.tf_star = 1 + math.log10(document_values.tf)

def calc_tf_idf(inverted_index, number_of_documents):
    for key, value in inverted_index.items():
        for document in value.documents:
            document_values = document.term_dictionary[key]
            document_values.tf_idf = document_values.tf_star*value.idf
            document.weight_sum_not_squared += document_values.tf_idf**2



def calc_idf(inverted_index,number_of_documents):
    for key in inverted_index:
        row = inverted_index[key]
        row.idf = math.log10(number_of_documents/row.df)

def create_champlist(inverted_index, r):
    inverted_index_champlist = {}
    amount_of_docs = 0

    for key,value in inverted_index.items():
        top_r_contenders = []
        amount_of_docs = 0
        for doc in sorted(value.documents, key=lambda doc: doc.term_dictionary[key].tf_idf):
            if amount_of_docs < r:
                amount_of_docs += 1
                top_r_contenders.append(doc)
        inverted_index_champlist[key] = value
        inverted_index_champlist[key].documents = list(top_r_contenders)
    print("stop")
    return inverted_index_champlist

def get_k_best_results(query_inverted_index,inverted_index,k):
    intersection_list = []
    for key,value in query_inverted_index.items():
        if key in inverted_index:
            row = inverted_index[key]
            weight = row.idf*value.documents[0].term_dictionary[key].tf_star
            intersection_list.append((key, weight, row))
    document_set = set()
    for item in intersection_list:
        for doc in item[2].documents:
            document_set.add(doc)
        for doc in document_set:
            for key, value in doc.term_dictionary.items():
                value.weight = value.tf_idf
                value.normalized = 1/math.sqrt(doc.weight_sum_not_squared)

    for doc in document_set:
        product = 0
        for entry in intersection_list:
            term = entry[0]
            query_weight = entry[1]
            if term in doc.term_dictionary:
                product += query_weight*doc.term_dictionary[term].normalized
        doc.product = product
    document_list = list(document_set)
    sorted(document_list, key=lambda doc: doc.product)
    if len(document_list)<k:
        return document_list
    return document_list[:k]


def make_hashed_shingles_and_super_shingles(content, shingle_size=8,super_shingle_size=6,seed=1234, permutations= 84):
    random.seed(seed)
    random_ints = []
    for i in range(permutations):
        random_ints.append(random.randint(0,10**42))
    sketch = set()
    hashed_shingles = set()
    shingles = ngrams(content.split(), shingle_size)
    shingles_set = set()
    for shingle in shingles:
        shingles_set.add(shingle)

    for permutation in random_ints:
        for shingle in shingles_set:
            hashcode = hashlib.md5(str(shingle).encode('utf-8')).hexdigest()
            value = int(hashcode,16)
            hashed_shingles.add(value ^ permutation)
        if len(hashed_shingles) is 0:
            return set(), set()
        sketch.add(min(hashed_shingles))
        hashed_shingles.clear()

    hashed_super_shingles = set()
    sketch_list = list(sketch)
    super_shingle_set = set()
    elements_in_sketches = len(sketch)

    non_overlapping_super_sketches = [sketch_list[i * super_shingle_size:(i + 1) * super_shingle_size]for i in range((elements_in_sketches + super_shingle_size - 1) // super_shingle_size)]

    for super_shingle in non_overlapping_super_sketches:
        super_shingle_set.add(str(super_shingle))

    for super_shingle in super_shingle_set:
        hashcode = hashlib.md5(str(super_shingle).encode('utf-8')).hexdigest()
        value = int(hashcode, 16)
        hashed_super_shingles.add(value)
    return sketch, hashed_super_shingles


def duplicate_detection(new_page,pages, threshold_super_shingle=2, threshold_similarity=0.9):
    is_duplicate = False
    for page in pages:
        if len(page.super_shingles.intersection(new_page.super_shingles)) >= threshold_super_shingle:
            if len(page.shingles.intersection(new_page.shingles))/len(page.shingles.union(new_page.shingles) >= threshold_similarity):
                is_duplicate = True
                return is_duplicate
    return is_duplicate



'''
page = crawler.Page("meh1")
page.content = ["test", "term", "virker", "eller", "hvad", "eller"]

page2 = crawler.Page("meh2")
page2.content = ["test", "term", "auto", "nope", "term", "please"]

page3 = crawler.Page("meh3")
page3.content = ["hallo", "du", "auto"]

page_list = []
page_list.append(page)
page_list.append(page2)
page_list.append(page3)
inverted_index = create_inverted_index_from_pages(page_list)
champion_index = create_champlist(inverted_index, 10)
query_inverted_index = create_query_document("Klar til perfekte values, bare det virker, please, noget at teste med")
result = get_k_best_results(query_inverted_index,champion_index, 1)
print("re")
'''


