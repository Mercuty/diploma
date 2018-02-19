from time import sleep

import numpy as np
import vk
from random import randint
from igraph import Graph, plot

from tok import my_token

researched_id = 13221877


def initialisation():  # инициализация для вк апи
    session = vk.Session(access_token=my_token)
    api = vk.API(session, v='5.71', lang='ru', timeout=10)
    return api


def get_friends(api, userid):
    user_friends = api.friends.get(user_id=userid)
    return user_friends


def friends_clusterising(mutural_list):
    cluster_color = []
    friends_color = []
    mutural_list_col = len(mutural_list)
    print(mutural_list_col)
    friends_common = [0] * mutural_list_col
    for l in range(mutural_list_col):
        friends_common[l] = [0] * 5
    i = 0
    for friend in mutural_list:
        friends_common[i][0] = friend  # id друга
        friends_common[i][1] = len(mutural_list[friend])  # количество общих друзей с юзером
        friends_common[i][2] = ''  # номер кластера
        friends_common[i][3] = '' # цвет кластера
        friends_common[i][4] = mutural_list[friend] # id общих друзей
        i += 1
    friends_common.sort(key=lambda friends: friends[1]) # сортируем по возрастанию количества общих друзей
    cluster_num = 0
    i = 0
    for friend in friends_common: #первоначальное распределение в кластера
        if friend[2] == '':
            friend[2] = cluster_num
            for common_friend in mutural_list[friend[0]]:
                for j in range(mutural_list_col):
                    if ((friends_common[j][0] == common_friend) & (friends_common[j][2] == '')):
                        friends_common[j][2] = cluster_num
            cluster_num += 1
    for i in range(500):  # калибруем кластера
        for friend in friends_common:
            common_friends_clusters = np.zeros(cluster_num)
            people_in_cluster = np.zeros(cluster_num)
            for friends in friends_common:
                people_in_cluster[friends[2]] += 1
            for common_friend in friend[4]:
                for my_friend in friends_common:
                    if my_friend[0] == common_friend:
                        common_friends_clusters[my_friend[2]] += 1
            for iter in range(cluster_num):
                if people_in_cluster[iter] != 0:
                    common_friends_clusters[iter] /= people_in_cluster[iter]
            friend[2] = common_friends_clusters.argmax()
            for cluster in range(cluster_num): # присваеваем каждому кластеру рандомный цвет
                cluster_color.append(str(randint(0, 255)) + ", " + str(randint(0, 255)) + ", " + str(randint(0, 255)))
            for friend in friends_common: # передаем каждому юзеру цвет его кластера
                friend[3] = cluster_color[friend[2]]
                friends_color.append(cluster_color[friend[2]])
            friends_color.append("255, 255, 255")
    plot_graf(friends_common, mutural_list, friends_color)


# 27012093 53523636
def plot_graf(friends_common, mutural_list, friends_color):
    ids_in_string = []
    g = Graph()
    nodes_col = len(friends_common)
    g.add_vertices(nodes_col + 1) # +1 для самого пользователя
    for friend in friends_common:
        ids_in_string.append(str(friend[0]))
    ids_in_string.append(str(researched_id))
    g.vs["name"] = ids_in_string #называем вершины графа айдишниками юзеров
    g.vs["color"] = friends_color #красим вершины в соответствии с кластером юзера
    user_index = g.vs.find(str(researched_id)).index
    for friend in mutural_list: #строим связи между вершинами
        friend_node = g.vs.find(str(friend))
        g.add_edges([(friend_node.index, user_index)]) # связываем юзера с исследуемым пользователем
        for common_friend in mutural_list[friend]: # связываем каждого юзера с общими друзьями
            try:
                common_friend_node = g.vs.find(str(common_friend))
                connections = g.es.select(_within=(friend_node.index, common_friend_node.index))
                try: # проверяем, не добавляли ли мы уже эту связь
                    a = (connections[0])
                    # print("connection exists")
                except: # если не добавляли, то добавляем
                    g.add_edges([(friend_node.index, common_friend_node.index)])
            except Exception as e:
                print(e)
    g.vs["label"] = g.vs["name"]
    print(len(ids_in_string))
    layout = g.layout("kk")
    plot(g, "social_network.png") # сохраняем картинку графа
    # plot(g, layout=layout, margin=10)


def main():
    api = initialisation()
    my_friends = get_friends(api, researched_id)
    print(my_friends["count"])
    couples_of_friends = int(my_friends["count"] / 20) # ходим в апи пачками по 20 человек, чтобы в случае ошибки не было больно
    my_friends = my_friends["items"]
    print(couples_of_friends)
    mutural_list = {} # словарь [юзер]:[общий друг1, общий друг2 ...]
    for i in range(couples_of_friends + 1):
        sleep(0.25)
        slice = my_friends[i * 20:(i + 1) * 20]
        try: # идем за информацией о пачке юзеров в апи, если ошибка не венулась, аве нам
            mutural = api.friends.getMutual(source_uid=researched_id, target_uids=slice)
            print("ok " + str(i))
            for friend in mutural:
                mutural_list[friend["id"]] = friend["common_friends"]
        except: # если вернулась ошибка, то идем в апи за каждым юзером в отдельности
            print("error API " + str(i))
            for k in range(len(slice)):
                try:
                    sleep(0.4)
                    mutural = api.friends.getMutual(source_uid=researched_id, target_uids=slice[k])
                    for friend in mutural:
                        mutural_list[friend["id"]] = friend["common_friends"]
                except:
                    print("error " + str(slice[k]))
    friends_clusterising(mutural_list)


main()
