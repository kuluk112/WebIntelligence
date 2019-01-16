import webIntelligence.clustering
import webIntelligence.sentiment_analysis
import webIntelligence.text_processing
import pickle

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

def fix_probs():
    file = "only_pos.p"
    SA = pickle.load(open(file, "rb"))
    SA.positive_probability = (SA.positive_class_count + 1) / (
                (SA.positive_class_count + SA.negative_class_count) + 2)
    SA.negative_probability = (SA.negative_class_count + 1) / (
                (SA.positive_class_count + SA.negative_class_count) + 2)
    pickle.dump(SA, open(file, "wb"))

def assignment_2():



    users = []#method to cluster

    SA = webIntelligence.sentiment_analysis.SentimentAnalysis()
    SA.classify_users(users)
    SA.recommend_by_collaborative_filtering(users)

    for user in users:
        if user.review is None:
            print(user.name)
            print(user.would_purchase)
            print("\n")



