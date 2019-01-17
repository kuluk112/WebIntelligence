import webIntelligence.clustering
import webIntelligence.sentiment_analysis
import webIntelligence.text_processing
import webIntelligence.crawler
import webIntelligence.PageRanker
import pickle


def assignment_1():
    priorities = 3
    threads = 1
    politeness_sec = 0.2
    number_of_pages = 1000

    '''
    url_seed = "https://curlie.org/News/Headline_Links/"
    crawler = webIntelligence.crawler.Crawler(priorities,threads,politeness_sec)
    crawler.run_crawler(url_seed,number_of_pages)
    pageranker = webIntelligence.PageRanker.PageRanker(crawler.page_list)
    pageranker.give_pageranks()
    search_engine = webIntelligence.text_processing.Indexer()
    search_engine.create_inverted_index_from_pages(crawler.page_list)
    search_engine.create_champlist(20)
    pickle.dump(search_engine,open("search_engine.p", "wb"))
    '''

    search_engine = pickle.load(open("search_engine.p", "rb"))
    query = "guitar concert"
    tokenized_query = search_engine.tokenize(query)
    print(tokenized_query)
    documents = search_engine.search(query)

    for doc in documents:
        print(doc.page.url.geturl())
        print(doc.tokekenized_content)
        print(doc.product)
        print(doc.page.pagerank)



def assignment_2():

    friendship_path = "C://Users//Simon//Desktop//friendships.reviews.txt"
    result_path = "C://Users//Simon//Desktop//friendships.reviews.results.txt"
    number_of_clusters = 4

    community_detector = webIntelligence.clustering.CommunityDetector()
    #communities = community_detector.do_spectral_clustering_initial(friendship_path, number_of_clusters)
    communities = community_detector.do_spectral_clustering_from_save(friendship_path, number_of_clusters)

    result = webIntelligence.clustering.CommunityDetector()
    result_users = result.load_friendship_network(result_path).values()

    SA = pickle.load(open("only_pos.p", "rb"))
    for comm in communities:
        SA.classify_users(comm.users, False, True)

    for comm in communities:
        SA.recommend_by_collaborative_filtering(comm.users)

    all_comm_users = []
    for comm in communities:
        for user in comm.users:
            print(user.name)
            print(user.would_purchase)
            print("\n")
            all_comm_users.append(user)

    correct = 0
    wrong = 0

    users_test = list(result_users)

    users_test = sorted(users_test, key=lambda user: user.id)
    all_comm_users = sorted(all_comm_users, key=lambda user: user.id)

    for i in range(len(all_comm_users)):
        test_user = users_test[i]
        comm_user = all_comm_users[i]

        if comm_user.review is None:
            if comm_user.name == test_user.name:
                if comm_user.would_purchase == test_user.would_purchase:
                    correct += 1
                else:
                    wrong += 1
    print("correct: ")
    print(correct)
    print("wrong: ")
    print(wrong)



def training():
    trainingset_path = "C://Users//Simon//Desktop////SentimentTrainingData.txt"
    testset_path = "C://Users//Simon//Desktop/SentimentTestData.txt"

    SA = webIntelligence.sentiment_analysis.SentimentAnalysis()
    training_set = SA.load_sentiment_data(trainingset_path)
    print("load trainingset complete")
    test_set = SA.load_sentiment_data(testset_path)
    print("load testset complete")

    pos_set = []
    neg_set = []
    for i in training_set:
        if i[1] is True:
            pos_set.append(i)
        else:
            neg_set.append(i)
    pos_set = pos_set[:len(neg_set)]
    balanced_training_set = []
    balanced_training_set.extend(pos_set)
    balanced_training_set.extend(neg_set)

    SA.train_NBC(balanced_training_set, True, True)
    print("training complete")
    pickle.dump(SA, open("BALANCED_negate_AND_POS.p", "wb"))

    precision, recall, accuracy, f1 = SA.evaluate(test_set, True, True)

    print(precision)
    print(recall)
    print(accuracy)
    #bad results below
    #1.0
    #0.8334427664696871
    #0.8334427664696871


def load_NBC():
    testset_path = "C://Users//Simon//Desktop////SentimentTestingData.txt"
    #SA = pickle.load(open("BALANCED_negate_AND_POS.p", "rb"))
    SA = pickle.load(open("only_pos.p", "rb"))
    test_set = SA.load_sentiment_data(testset_path)
    precision, recall, accuracy, f1 = SA.evaluate(test_set, False, True)
    print("Accuracy: ", accuracy)
    print("Precision: ", precision)
    print("Recall: ", recall)
    print("F1: ", f1)

#load_NBC()

assignment_2()
'''
BALANCED
Accuracy:  0.7314510833880499
Precision:  0.9092927370758008
Recall:  0.7528886554621849
F1:  0.8237322223818417

Accuracy:  0.27872619829284306
Precision:  0.7817482133040132
Recall:  0.18671218487394958
F1:  0.3014308426073132
--------------------------

negation and POS
Accuracy:  0.8334427664696871
Precision:  0.8334427664696871
Recall:  1.0
F1:  0.9091560224424018
--------------

negation only
Accuracy:  0.6088859706719194
Precision:  0.8181675062972292
Recall:  0.6823792016806722
F1:  0.7441294387170676
-----------------

nothing
Accuracy:  0.6088859706719194
Precision:  0.8180673591438464
Recall:  0.6825105042016807
F1:  0.7441660701503222
----------------------

only POS
Accuracy:  0.8079448456992777
Precision:  0.833276469919254
Recall:  0.9620535714285714
F1:  0.8930464988725698
 '''
