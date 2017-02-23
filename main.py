from itertools import count
from random import randint
from time import sleep

import vk
from igraph import Graph, summary, plot

from tok import my_token


def initialisation():
    session = vk.Session(access_token=my_token)
    api = vk.API(session, v='5.62', lang='ru', timeout=10)
    return api


def get_friends(api, userid):
    user_friends = api.friends.get(user_ids=userid)
    return user_friends


def friends_clusterising(mutural_list):
    cluster_color = []
    friends_color = []
    mutural_list_col = len(mutural_list)
    friends_common = [0] * mutural_list_col
    for l in range(mutural_list_col):
        friends_common[l] = [0] * 4
    i = 0
    for friend in mutural_list:
        friends_common[i][0] = friend
        friends_common[i][1] = len(mutural_list[friend])
        friends_common[i][2] = ''
        friends_common[i][3] = ''
        i += 1
    friends_common.sort(key=lambda friends: friends[1], reverse=True)
    cluster_num = 0
    i = 0
    for friend in friends_common:
        if friend[2] == '':
            friend[2] = cluster_num
            for common_friend in mutural_list[friend[0]]:
                for j in range(mutural_list_col):
                    if ((friends_common[j][0] == common_friend) & (friends_common[j][2] == '')):
                        friends_common[j][2] = cluster_num
            cluster_num += 1
    for cluster in range(cluster_num):
        cluster_color.append(str(randint(0, 255)) + ", " + str(randint(0, 255)) + ", " + str(randint(0, 255)))
    for friend in friends_common:
        friend[3] = cluster_color[friend[2]]
        friends_color.append(cluster_color[friend[2]])
    friends_color.append("255, 255, 255")
    plot_graf(friends_common, mutural_list, friends_color)


def plot_graf(friends_common, mutural_list, friends_color):
    ids_in_string = []
    ids_friends = []
    g = Graph()
    nodes_col = len(friends_common)
    g.add_vertices(nodes_col + 1)
    for friend in friends_common:
        ids_in_string.append(str(friend[0]))
    ids_in_string.append(str(53523636))
    g.vs["name"] = ids_in_string
    g.vs["color"] = friends_color
    user_index = g.vs.find(str(53523636)).index
    print(user_index)
    for friend in mutural_list:
        friend_node = g.vs.find(str(friend))
        g.add_edges([(friend_node.index, user_index)])
        for common_friend in mutural_list[friend]:
            try:
                common_friend_node = g.vs.find(str(common_friend))
                connections = g.es.select(_within=(friend_node.index, common_friend_node.index))
                try:
                    print(connections[0])
                    print("connection exists")
                except:
                    g.add_edges([(friend_node.index, common_friend_node.index)])
            except:
                print("error EDGING or already exists")
    g.vs["label"] = g.vs["name"]
    layout = g.layout("kk")
    plot(g, layout=layout, margin=5)


def main():
    api = initialisation()
    my_friends = get_friends(api, 53523636)
    couples_of_friends = int(my_friends["count"] / 20)
    my_friends = my_friends["items"]
    print(couples_of_friends)
    mutural_list = {}
    for i in range(couples_of_friends):
        sleep(0.25)
        slice = my_friends[i * 20:(i + 1) * 20]
        try:
            mutural = api.friends.getMutual(target_uids=slice)
            print("ok " + str(i))
        except:
            print("error API")
            # for k in range(20):
            #     try:
            #         sleep(0.25)
            #         mutural = api.friends.getMutual(target_uids=slice[k])
            #     except:
            #         print("error" + " " + str(slice[k]))
        for friend in mutural:
            mutural_list[friend["id"]] = friend["common_friends"]
    friends_clusterising(mutural_list)
    # plot_graf(mutural_list)


main()
