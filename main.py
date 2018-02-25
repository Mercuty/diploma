from random import randint
from time import sleep

import numpy as np
import vk
from igraph import Graph, plot

from tok import *

# researched_id = 22846933
researched_id = 53523636


# researched_id = 13221877


def initialisation():  # инициализация для вк апи
    session = vk.Session(access_token=my_token)
    api = vk.API(session, v='5.71', lang='ru', timeout=10)
    return api


def get_friends(api, userid):
    user_friends = api.friends.get(user_id=userid)
    return user_friends


def friends_clusterising(mutural_list):
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
        friends_common[i][3] = ''  # цвет кластера
        friends_common[i][4] = mutural_list[friend]  # id общих друзей
        i += 1
    friends_common.sort(
        key=lambda friends_sorter: friends_sorter[1])  # сортируем по возрастанию количества общих друзей
    cluster_num = 0
    for friend in friends_common:  # первоначальное распределение в кластера
        if friend[2] == '':
            friend[2] = cluster_num
            for common_friend in mutural_list[friend[0]]:
                for j in range(mutural_list_col):
                    if (friends_common[j][0] == common_friend) & (friends_common[j][2] == ''):
                        friends_common[j][2] = cluster_num
            cluster_num += 1
    for i in range(mutural_list_col):  # калибруем кластера
        for friend in friends_common:
            common_friends_clusters = np.zeros(cluster_num)
            people_in_cluster = np.zeros(cluster_num)
            for friends in friends_common:
                people_in_cluster[friends[2]] += 1
            for common_friend in friend[4]:
                for my_friend in friends_common:
                    if my_friend[0] == common_friend:
                        common_friends_clusters[my_friend[2]] += 1
            for iter_num in range(cluster_num):
                if people_in_cluster[iter_num] != 0:
                    common_friends_clusters[iter_num] /= people_in_cluster[iter_num]
            friend[2] = common_friends_clusters.argmax()
    for i in range(mutural_list_col // 10):  # схлопываем недокластеры
        for cluster in range(cluster_num):
            cluster_col = [0] * cluster_num
            for friend in friends_common:  # считаем количество друзей друга в разных кластерах
                if friend[2] == cluster:
                    for m_friend in friend[4]:
                        for friend_1 in friends_common:
                            if friend_1[0] == m_friend:
                                cluster_col[friend_1[2]] += 1
            for cluster_c in range(cluster_num):
                if (cluster_col[cluster_c] != 0) & (cluster_col[cluster] != 0) & (cluster != cluster_c):
                    if cluster_col[cluster_c] / cluster_col[cluster] > 1:
                        for k in range(len(friends_common)):
                            if friends_common[k][2] == cluster_c:
                                friends_common[k][2] = cluster
    return friends_common


# 27012093 53523636
# noinspection PyBroadException
def plot_graf(friends_common, name, common):
    if common:
        print("COMMON!")
    friends_ids = []
    cluster_color = []
    friends_color = []
    cluster_num = 0

    for friend in friends_common:
        if cluster_num < friend[2]:
            cluster_num = friend[2]
    cluster_num += 1
    print(cluster_num)
    for cluster in range(cluster_num):  # присваеваем каждому кластеру рандомный цвет
        cluster_color.append(str(randint(100, 255)) + ", " + str(randint(100, 255)) + ", " + str(randint(100, 255)))
    for friend in friends_common:  # передаем каждому юзеру цвет его кластера
        friend[3] = cluster_color[friend[2]]
        friends_color.append(cluster_color[friend[2]])
    if common:
        friends_color.append("255, 255, 255")

    for friend in friends_common:
        friends_ids.append(friend[0])
    api = initialisation()
    sleep(0.4)
    friend_names = api.users.get(user_ids=friends_ids)
    if common:
        sleep(0.4)
        researched_name = api.users.get(user_ids=str(researched_id))[0]["last_name"]

    ids_in_string = []
    names_in_string = []
    g = Graph()
    nodes_col = len(friends_common)
    if common:
        g.add_vertices(nodes_col + 1)
    else:
        g.add_vertices(nodes_col)  # +1 для самого пользователя
    friend_num = 0
    for friend in friends_common:
        names_in_string.append(friend_names[friend_num]["last_name"])
        ids_in_string.append(str(friend[0]))
        friend_num += 1
    if common:
        ids_in_string.append(str(researched_id))
        names_in_string.append(researched_name)
    g.vs["name"] = ids_in_string  # называем вершины графа айдишниками юзеров
    g.vs["color"] = friends_color  # красим вершины в соответствии с кластером юзера
    if common:
        user_index = g.vs.find(str(researched_id)).index
    for friend in friends_common:  # строим связи между вершинами
        friend_node = g.vs.find(str(friend[0]))
        if common:
            g.add_edges([(friend_node.index, user_index)])  # связываем юзера с исследуемым пользователем
        for common_friend in friend[4]:  # связываем каждого юзера с общими друзьями
            try:
                common_friend_node = g.vs.find(str(common_friend))
                connections = g.es.select(_within=(friend_node.index, common_friend_node.index))
                try:  # проверяем, не добавляли ли мы уже эту связь
                    a = (connections[0])
                except:  # если не добавляли, то добавляем
                    g.add_edges([(friend_node.index, common_friend_node.index)])
            except Exception as e:
                e
    g.vs["label"] = names_in_string
    g.vs["label.color"] = ("255,0,0")*len(names_in_string)
    print("ids_in_string: " + str(len(ids_in_string)))
    plot(
        g,
        "social_network_" + name + ".png",
        bbox=(1500, 1200),
        margin=20,
        vertex_label_color="black",
        edge_width=0.1,
        vertex_label_size=14,
        vertex_label_font=2
    )  # сохраняем картинку графа


def get_mutural_list(friends_list, api):
    couples_of_friends = int(friends_list["count"] / 20)
    my_friends = friends_list["items"]
    print(couples_of_friends)
    mutual_list = {}  # словарь [юзер]:[общий друг1, общий друг2 ...]
    for i in range(couples_of_friends + 1):
        sleep(0.25)
        slice_20 = my_friends[i * 20:(i + 1) * 20]
        try:  # идем за информацией о пачке юзеров в апи, если ошибка не венулась, аве нам
            mutual = api.friends.getMutual(source_uid=researched_id, target_uids=slice_20)
            print("ok " + str(i))
            for friend in mutual:
                mutual_list[friend["id"]] = friend["common_friends"]
        except:  # если вернулась ошибка, то идем в апи за каждым юзером в отдельности
            print("error API " + str(i))
            for k in range(len(slice_20)):
                try:
                    sleep(0.4)
                    mutual = api.friends.getMutual(source_uid=researched_id, target_uids=slice_20[k])
                    for friend in mutual:
                        mutual_list[friend["id"]] = friend["common_friends"]
                except:
                    print("error " + str(slice_20[k]))
    return mutual_list


def plot_subclusters(clustered_friends_common):
    subcluster_friends_common = []
    cluster_num = 0
    i = 0
    friend_col = len(clustered_friends_common)
    clustered_friends_common.sort(key=lambda friends_sorter: friends_sorter[2])
    while i < friend_col - 1:
        while clustered_friends_common[i][2] == cluster_num:
            subcluster_friends_common.append(clustered_friends_common[i])
            i += 1
            if i >= friend_col:
                break
        if subcluster_friends_common:
            print("----")
            print("subcluster len: " + str(len(subcluster_friends_common)))
            plot_graf(subcluster_friends_common, str(cluster_num), False)
            print("cluster num: " + str(cluster_num))
        cluster_num += 1
        subcluster_friends_common = []


# noinspection PyBroadException
def main():
    api = initialisation()
    my_friends = get_friends(api, researched_id)
    print(my_friends["count"])
    # mutual_list = get_mutual_list(my_friends, api)
    clustered_friends_common = friends_clusterising(m_list)
    plot_subclusters(clustered_friends_common)
    plot_graf(clustered_friends_common, "all", True)


main()
