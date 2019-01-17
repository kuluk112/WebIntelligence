import nltk
import math
import string
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize


class DocumentValues:
    def __init__(self):
        self.tf = 1
        self.tf_star = 0
        self.tf_idf = 0
        self.weight = 0
        self.normalised = 0

class RowEntry:
    def __init__(self, document):
        self.df = 1
        self.documents = [document]
        self.idf = 0
        self.query_weight = 0


class Document:
    def __init__(self,tokenized_content,page=None, document_id=None):
        if page is not None:
            self.term_dictionary = {}
            self.page = page
            self.tokekenized_content  = tokenized_content
            self.document_id = document_id
            self.product = 0
            self.weight_sum_not_squared = 0
        else:
            self.term_dictionary = {}
            self.query = tokenized_content


class Indexer:
    def __init__(self):
        self.inverted_index = {}
        self.champion_index = {}
        self.documents = []

    def tokenize(self,input):
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


    def create_inverted_index_from_pages(self, pages):
        inverted_index = {}
        document_list = []

        document_id = 0
        for page in pages:
            tokenized_content = self.tokenize(page.content)
            document = Document(tokenized_content,page, document_id)
            document_list.append(document)
            for term in document.tokekenized_content:
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
        self.calc_ranking(inverted_index, len(document_list))
        self.inverted_index = inverted_index

    def calc_ranking(self,inverted_index, number_of_documents):
        self.calc_tf_star(inverted_index)
        self.calc_idf(inverted_index,number_of_documents)
        self.calc_tf_idf(inverted_index,number_of_documents)

    def calc_score(self,query,inverted_index):
        tokenized_query = self.tokenize(query)
        query_document = Document(id=-1, query=query)
        #Need tf*-idf for query

    def create_query_document(self,query):
        tokenized_query = self.tokenize(query)
        query_document = Document(tokenized_query)
        return query_document

    def create_inverted_index_from_query(self, document):
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
        self.calc_tf_star(inverted_index)
        return inverted_index

    def calc_tf_star(self,inverted_index):
        for key, value in inverted_index.items():
            for document in value.documents:
                document_values = document.term_dictionary[key]
                document_values.tf_star = 1 + math.log10(document_values.tf)

    def calc_tf_idf(self,inverted_index, number_of_documents):
        for key, value in inverted_index.items():
            for document in value.documents:
                document_values = document.term_dictionary[key]
                document_values.tf_idf = document_values.tf_star*value.idf
                document.weight_sum_not_squared += document_values.tf_idf**2


    def calc_idf(self,inverted_index,number_of_documents):
        for key in inverted_index:
            row = inverted_index[key]
            row.idf = math.log10(number_of_documents/row.df)

    def create_champlist(self, r):
        inverted_index_champlist = {}

        for key, value in self.inverted_index.items():
            top_r_contenders = []
            amount_of_docs = 0
            for doc in sorted(value.documents, key=lambda doc: doc.term_dictionary[key].tf_idf):
                if amount_of_docs < r:
                    amount_of_docs += 1
                    top_r_contenders.append(doc)
            inverted_index_champlist[key] = value
            inverted_index_champlist[key].documents = list(top_r_contenders)
        self.champion_index = inverted_index_champlist
        return inverted_index_champlist

    def search(self,query,top_k_results=10):
        query_document = self.create_query_document(query)
        query_inverted_index = self.create_inverted_index_from_query(query_document)
        documents = self.get_k_best_results(query_inverted_index, self.champion_index, top_k_results)
        return documents

    def get_k_best_results(self,query_inverted_index,inverted_index, k):
        intersection_list = []

        # Calc weight for each term of query, which is present in the terms of the inverted_index
        for key, value in query_inverted_index.items():
            if key in inverted_index:
                row = inverted_index[key]
                weight = row.idf*value.documents[0].term_dictionary[key].tf_star
                intersection_list.append((key, weight, row))

        document_set = set()
        for item in intersection_list:
            for doc in item[2].documents:
                document_set.add(doc)

        for doc in document_set:
            doc.length = math.sqrt(doc.weight_sum_not_squared)
            for value in doc.term_dictionary.values():
                value.normalised = value.tf_idf/doc.length

        for doc in document_set:
            product = 0
            for entry in intersection_list:
                term = entry[0]
                query_weight = entry[1]
                if term in doc.term_dictionary:
                    term_normalised_weight = doc.term_dictionary[term].normalised
                    product += query_weight*term_normalised_weight
            doc.product = product * 1 #doc.page.pagerank

        document_list = list(document_set)
        document_list = sorted(document_list, key=lambda doc: doc.product,reverse=True)
        if len(document_list)<k:
            return document_list
        return document_list[:k]


