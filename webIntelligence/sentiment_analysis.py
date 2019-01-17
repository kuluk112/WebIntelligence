
import nltk
import re

class DictEntry:
    def __init__(self):
        self.pos_count = 0
        self.neg_count = 0

    def tot_count(self):
        return self.neg_count + self.pos_count

class SentimentAnalysis:
    def __init__(self):
        self.bag_of_words = {}
        self.positive_class_count = 0
        self.negative_class_count = 0
        self.positive_probability = 0
        self.negative_probability = 0
        self.negation_words = ["never", "no", "nothing", "nowhere", "not", "havent", "haven't", "hasnt", "hasn't", "hadnt", "hadn't", "cant", "can't", "couldnt", "couldn't",
                         "shouldnt", "shouldn't", "wont", "won't", "wouldnt", "wouldn't", "dont", "don't", "dosnt", "dosn't", "didnt", "didn't", "isnt", "isn't", "arent", "aren't", "aint", "ain't"]

    def classify_with_NBC(self, text, negate, pos):
        features = self.tokenize_and_extract_features(text, negate, pos)
        pos_word_given_class = []
        neg_word_given_class = []
        sentiment_positive_probability = 1
        sentiment_negative_probability = 1
        for i in features:
            if i in self.bag_of_words:
                # 1 and len(dict) --> laplacian smoothing
                pwc_pos = (self.bag_of_words[i].pos_count + 1) / (self.bag_of_words[i].tot_count() + len(self.bag_of_words))
            else: 
                pwc_pos = (0 + 1) / (0 + len(self.bag_of_words))
            pos_word_given_class.append(pwc_pos)

            if i in self.bag_of_words:
                # 1 and len(dict) --> laplacian smoothing
                pwc_neg = (self.bag_of_words[i].neg_count + 1) / (self.bag_of_words[i].tot_count() + len(self.bag_of_words))
            else:
                pwc_neg = (0 + 1) / (0 + len(self.bag_of_words))
            neg_word_given_class.append(pwc_neg)

        #P(word|class)
        for probability in pos_word_given_class:
            sentiment_positive_probability *= probability
        # mult(P(word|class)) * P(class)
            sentiment_positive_probability *= self.positive_probability

        for probability in neg_word_given_class:
            sentiment_negative_probability *= probability
        sentiment_negative_probability *= self.negative_probability

        return sentiment_positive_probability, sentiment_negative_probability



    def train_NBC(self, list_tuples, negate, pos):
        train_len = len(list_tuples)
        count = 0
        for i in list_tuples:
            self.train_with_item(i, negate, pos)
            count += 1
            if count == 1:
                print(1)
                print(train_len)
            if count % 1000 == 0:
                print(count)
            #                                          1 and 2 --> smoothing                   2 --> number of classes
        self.positive_probability = (self.positive_class_count + 1) / ((self.positive_class_count + self.negative_class_count) + 2)
        self.negative_probability = (self.negative_class_count + 1) / ((self.positive_class_count + self.negative_class_count) + 2)



    def train_with_item(self, tuple, negate, pos):
        text = tuple[0]
        sentiment_class = tuple[1]
        list_of_key_val = self.tokenize_and_extract_features(text, negate=negate, pos=pos)

        #positive review
        if sentiment_class:
            self.positive_class_count += 1
            for i in list_of_key_val:
                if i in self.bag_of_words:
                    self.bag_of_words[i].pos_count += 1
                else:
                    entry = DictEntry()
                    entry.pos_count = 1
                    self.bag_of_words[i] = entry

        #negetive review
        else:
            self.negative_class_count += 1
            for i in list_of_key_val:
                if i in self.bag_of_words:
                    self.bag_of_words[i].neg_count += 1
                else:
                    entry = DictEntry()
                    entry.neg_count = 1
                    self.bag_of_words[i] = entry



    def negate_words(self, string):
        negate_tag = False
        split = re.findall(r"[\w']+|[.,!?;]", string)
        result = str()
        temp = []
        for i in split:
            if i in self.negation_words:
                negate_tag = not negate_tag

            if '.' in i or '!' in i or '?' in i:
                negate_tag = False

            if negate_tag and ',' not in i:
                i += "_NEG"
                temp.append(i)
            else:
                temp.append(i)

        result = " ".join(temp)
        return result

    def tokenize_and_extract_features(self, string, negate=True, pos=True):
        if negate and pos:
            negated = self.negate_words(string)
            tokens = nltk.word_tokenize(negated)
            list_key_val = nltk.pos_tag(tokens)
            return list_key_val

        if negate and not pos:
            negated = self.negate_words(string)
            split = negated.split(' ')
            list_key_val = []
            for i in split:
                list_key_val.append((i, None))
            return list_key_val

        if not negate and pos:
            tokens = nltk.word_tokenize(string)
            list_key_val = nltk.pos_tag(tokens)
            return list_key_val

        if not negate and not pos:
            split = re.findall(r"[\w']+|[.,!?;]", string)
            list_key_val = []
            for i in split:
                list_key_val.append((i, None))
            return list_key_val

    def evaluate(self, testset, negate, pos):
        true_positive = 0
        false_positive = 0
        true_negative = 0
        false_negative = 0
        total_correct = 0
        total_false = 0
        guess_true = 0
        guess_false = 0
        test_len = len(testset)
        count = 0

        for item in testset:

            label = item[1]
            text = item[0]

            pos, neg = self.classify_with_NBC(text, negate, pos)

            if pos >= neg:
                result = True
            else:
                result = False

            if result is label:
                if result is True:
                    guess_true += 1
                    true_positive += 1
                    total_correct += 1
                if result is False:
                    guess_false += 1
                    true_negative += 1
                    total_correct += 1
            else:
                if result is True:
                    guess_true += 1
                    false_positive += 1
                    total_false += 1
                if result is False:
                    guess_false += 1
                    false_negative += 1
                    total_false += 1
            count += 1
            if count == 1:
                print(1)
                print(test_len)
            if count % 1000 == 0:
                print(count)

        precision = true_positive / (true_positive + false_positive)
        recall = true_positive / (true_positive + false_negative)
        accuracy = total_correct / (total_correct + total_false)
        f1 = 2 * ((precision * recall)/(precision + recall))
        return precision, recall, accuracy, f1

    def load_sentiment_data(self, path):
        dataset = []
        with open(path, "r") as lines:
            for line in lines:
                if line.startswith("review/score"):
                    current_score = int(float(line.split("review/score: ")[1].rstrip()))
                    positive = None
                    if current_score > 3:
                        positive = True
                    elif current_score < 3:
                        positive = False
                if line.startswith("review/summary:") and current_score is not 3:
                    review = line.split("review/summary: ")[1].rstrip()

                if line.startswith("review/text:") and current_score is not 3:
                    review += " " + line.split("review/text: ")[1].rstrip()
                    dataset.append((review,positive))
        return dataset


    def classify_users(self,users, negative, pos):

        for user in users:
            if user.review is not None:
                positive, negative = self.classify_with_NBC(user.review,negative,pos)
                if positive >= negative:
                    user.score = 5
                else:
                    user.score = 1

    def recommend_by_collaborative_filtering(self,users):

        for user in users:
            if user.review is None:
                score = 0
                for friend in user.friends:
                    if user.community_id is not friend.community_id and friend.name is "kyle":
                        if friend.score < 5:
                            score += friend.score/100
                        else:
                            score += friend.score * 100
                    elif user.community_id is not friend.community_id or friend.name is "kyle":
                        if friend.score < 5:
                            score += friend.score/10
                        else:
                            score += friend.score * 10
                    else:
                        score += friend.score
                friends_with_review = [i for i in user.friends if i.review is not None]
                if not friends_with_review:
                    user.score = 1
                else:
                    user.score = score/len(friends_with_review)
                if abs(user.score-1) <= abs(user.score-5):
                    user.would_purchase = False
                else:
                    user.would_purchase = True



#text = nltk.word_tokenize("They won't refuse to permit us to obtain the refuse permit......")
#insert in token words

#for i in nltk.pos_tag(text):
#    print(i)
#SA = SentimentAnalysis()
#negated = SA.negate_words("i didnt, like it... i did not not like it")
#tokens = nltk.word_tokenize(negated)
#for i in SA.tokenize_and_extract_features("i didnt, like it... i did not not like it", negate=True, pos=True):
#    print(i)

#SA.train_with_item(("this is a sentence sentence", True), True, True)
#SA.train_with_item(("this is a sentence sentence", False), True, True)
#SA.train_NBC([("a good movie", True), ("a good movie", True), ("a bad film", False)], True, True)
#pos, neg = SA.classify_with_NBC("bad film", True, True)
#print(pos, neg)

