from itertools import count
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


def plot_graf(mutural_list):
    dict_keys = []
    g = Graph()
    nodes_col = len(mutural_list)
    g.add_vertices(nodes_col + 1)
    dict_keyss = mutural_list.keys()
    for key in dict_keyss:
        dict_keys.append(str(key))
    dict_keys.append(str(53523636))
    g.vs["name"] = dict_keys
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
    print(g)
    g.vs["label"] = g.vs["name"]
    layout = g.layout("kk")
    plot(g, layout=layout)


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
            # print(friend)
            # print(friend["id"])
            mutural_list[friend["id"]] = friend["common_friends"]
    plot_graf(mutural_list)


main()
