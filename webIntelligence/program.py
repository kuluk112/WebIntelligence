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
    number_of_pages = 20
    url_seed = "https://curlie.org/News/Headline_Links/"
    crawler = webIntelligence.crawler.Crawler(priorities,threads,politeness_sec)
    crawler.run_crawler(url_seed,number_of_pages)
    pageranker = webIntelligence.PageRanker.PageRanker(crawler.page_list)
    pageranker.give_pageranks()

    search_engine = webIntelligence.text_processing.Indexer()
    search_engine.create_inverted_index_from_pages(crawler.page_list)
    search_engine.create_champlist(20)
    query = "Trump's reference to Wounded Knee evokes the dark history of suppression of indigenous religions"
    documents = search_engine.search(query)



def training():
    trainingset_path = "C://Users//Simon//Desktop//SentimentTrainingData.txt"
    testset_path = "C://Users//Simon//Desktop//SentimentTestingData.txt"

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
    testset_path = "C://Users//Simon//Desktop//SentimentTestingData.txt"
    SA = pickle.load(open("BALANCED_negate_AND_POS.p", "rb"))
    test_set = SA.load_sentiment_data(testset_path)
    precision, recall, accuracy, f1 = SA.evaluate(test_set, False, False)
    print(precision)
    print(recall)
    print(accuracy)
    print(f1)


def assignment_2():

    friendship_path = "C://Users//Lasse//Desktop//Web intelligence//friendships.reviews.txt"
    number_of_clusters = 4

    community_detector = webIntelligence.clustering.CommunityDetector()
    #communities = community_detector.do_spectral_clustering_initial(friendship_path, number_of_clusters)
    communities = community_detector.do_spectral_clustering_from_save(friendship_path, number_of_clusters)

    SA = pickle.load(open("negation_and_pos.p", "rb"))
    for comm in communities:
        SA.classify_users(comm.users)

    for comm in communities:
        SA.recommend_by_collaborative_filtering(comm.users)

    for comm in communities:
        for user in comm.users:
            if user.review is None:
                print(user.name)
                print(user.would_purchase)
                print("\n")


assignment_2()
