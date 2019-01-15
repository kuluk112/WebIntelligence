from numpy import array
import pickle
from numpy.linalg import eig
import numpy as np
import re
import networkx as nx
import random
import sys
import matplotlib.pyplot as plt
from scipy.cluster.vq import kmeans,vq,whiten


class Community:
    def __init__(self, community_id):
        self.community_id = community_id
        self.users = []


class User:
    id_counter = 0

    def __init__(self, name):
        self.name = name
        self.id = User.id_counter
        User.id_counter += 1
        self.friends = []
        self.community_id = None
        self.review = None
        self.score = 0
        self.would_purchase = False

def load_friendship_network(path):

    users = {}
    with open(path, "r") as lines:
        for line in lines:
            line = line.rstrip('\n')
            if line.startswith("user"):
                name = line.split(": ")[1].rstrip()
                if name in users:
                    current_user = users[name]
                else:
                    current_user = User(name)
                    users[name] = current_user
            if line.startswith("friends"):
                friends_tab_sep = line.split("friends:\t")[1]
                friends = re.split(r'\t+', friends_tab_sep)
                for friend in friends:
                    if friend in users:
                        current_user.friends.append(users[friend])
                    else:
                        new_user = User(friend)
                        users[friend] = new_user
                        current_user.friends.append(new_user)
            if line.startswith("summary"):
                if line.startswith("summary: *"):
                    continue
                else:
                    summary = line.split("summary: ")[1].rstrip()
                    current_user.review = remove_html_tags(summary)
            if line.startswith("review"):
                if line.startswith("review: *"):
                    continue
                else:
                    review = line.split("review: ")[1].rstrip()
                    current_user.review += " " + remove_html_tags(review)
    return users

def remove_html_tags(text):
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)



def create_degree_matrix(users):
    user_list = list(users.values())
    degree_matrix = np.zeros((len(users), len(users)))

    for user in user_list:
        degree_matrix[user.id][user.id] = len(user.friends)
    return degree_matrix

def create_adjecency_matrix(users):
    user_list = list(users.values())
    user_list = sorted(user_list, key=lambda user: user.id)
    adjacency_matrix = np.zeros((len(users), len(users)))

    row = 0
    column = 0
    for friend_with in user_list:
        for friend_of in user_list:
            if friend_of in friend_with.friends:
                adjacency_matrix[row][column] = 1
            column +=1
        row += 1
        column = 0

    return adjacency_matrix

def compute_eigenvectors_and_eigenvalues(laplacian_matrix):
    eigen_values,eigen_vectors = eig(laplacian_matrix)
    return eigen_values,eigen_vectors

def create_laplacian_matrix(adjacency_matrix,degree_matrix):
    laplacian_matrix = degree_matrix.__sub__(adjacency_matrix)
    return laplacian_matrix

def draw_network(adjacency_matrix):
    g = nx.from_numpy_matrix(adjacency_matrix)
    layout = nx.spring_layout(g, pos=nx.circular_layout(g))
    nx.spring_layout
    nx.draw(g, pos=layout, with_labels=True, node_color='white')
    plt.show()

def k_means(eigen_values,eigen_vectors,k):
    reduced_matrix = eigen_vectors[:, 0:k]
    centroids,_ = kmeans(reduced_matrix,k)
    clx,_ = vq(reduced_matrix,centroids)
    return clx
def correct_eigen_format(eigen_values,eigen_vectors):
    idx = np.argsort(eigen_values)
    eigen_values = eigen_values[idx]
    eigen_vectors = eigen_vectors[:, idx]

    eigen_values = eigen_values[1:]
    eigen_vectors = eigen_vectors[:, 1:]
    eigen_values = eigen_values.reshape((-1, 1))
    return eigen_values, eigen_vectors


def assign_users_to_communities(users, eigen_values, eigen_vectors, k):

    clx = k_means(eigen_values,eigen_vectors,k)
    communities = []
    user_list = list(users.values())
    user_list = sorted(user_list, key=lambda user: user.id)

    for community_id in range(k):
        communities.append(Community(community_id))

    user_index = 0
    for community_id_of_node in clx:
        current_user = user_list[user_index]
        current_user.community_id = community_id_of_node
        communities[community_id_of_node].users.append(current_user)
        user_index += 1
    return communities

def do_spectral_clustering_initial(path,number_of_clusters):
    users = load_friendship_network(path)
    adjacency_matrix = create_adjecency_matrix(users)
    degree_matrix = create_degree_matrix(users)
    laplacian_matrix = create_laplacian_matrix(adjacency_matrix,degree_matrix)

    eigen_values1,eigen_vectors1 = compute_eigenvectors_and_eigenvalues(laplacian_matrix)
    eigen_values, eigen_vectors = correct_eigen_format(eigen_values1,eigen_vectors1)
    pickle.dump(eigen_values, open("eigen_values.p", "wb"))
    pickle.dump(eigen_vectors, open("eigen_vectors.p", "wb"))

    communities = assign_users_to_communities(users, eigen_values, eigen_vectors, number_of_clusters)
    return communities

def do_spectral_clustering_from_save(path,number_of_clusters):
    users = load_friendship_network(path)
    eigen_values = pickle.load(open("eigen_values.p", "rb"))
    eigen_vectors = pickle.load(open("eigen_vectors.p", "rb"))

    communities = assign_users_to_communities(users, eigen_values, eigen_vectors, number_of_clusters)
    return communities

def load_sentiment_data(path):
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

def create_adjacency_matrix_from_communities(users):
    user_list = list(users.values())
    user_list = sorted(user_list, key=lambda user: user.id)
    adjacency_matrix = np.zeros((len(users), len(users)))
    row = 0
    column = 0
    for friend_with in user_list:
        for friend_of in user_list:
            if friend_of in friend_with.friends:
                adjacency_matrix[row][column] = 1
            column += 1
        row += 1
        column = 0

    return adjacency_matrix

path = "C://Users//Lasse//Desktop//Web intelligence//friendships.reviews.txt"
path_sentiment_training_set = "C://Users//Lasse//Desktop//Web intelligence//SentimentTrainingData.txt"
path_sentiment_test_set = "C://Users//Lasse//Desktop//Web intelligence//SentimentTestingData.txt"

training_set = load_sentiment_data(path_sentiment_training_set)
test_set = load_sentiment_data(path_sentiment_test_set)
pickle.dump(training_set, open("training_set.p", "wb"))
pickle.dump(test_set, open("test_set.p", "wb"))

#number_of_clusters = 4
#communities = do_spectral_clustering_from_save(path,number_of_clusters)

print("test")
