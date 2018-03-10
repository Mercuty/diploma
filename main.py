# -*- coding: utf-8 -*-
from random import randint
from time import sleep

import numpy as np
import vk
from igraph import Graph, plot

from tok import *

# reload(sys)
# sys.setdefaultencoding("utf-8")

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
def make_graf(friends_common, common):
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
	friend_info = api.users.get(user_ids=friends_ids, fields="last_name")
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
	friend_information = get_friend_information(api, friends_ids)
	for friend in friends_common:
		names_in_string.append(friend_info[friend_num]["last_name"] + ' ' + friend_information[friend_num])
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
	g.vs["label.color"] = ("255,0,0") * len(names_in_string)
	if not common:
		print("------")
		print(cluster_num)
		i = 0
		informative_friends = []
		opposite_informative_friends = []
		for i in range(len(g.vs)):
			if friend_information[i] == '+':
				informative_friends.append(i)
			if friend_information[i] == '-':
				opposite_informative_friends.append(i)
		print(informative_friends)
		print(opposite_informative_friends)
		print()
		print(g.vs["label"])
		print("CHECKING +:")
		is_ok_for_inf = is_subcluster_informative(g, informative_friends)
		print("CHECKING -:")
		is_ok_for_opposite = is_subcluster_informative(g, opposite_informative_friends)
		if (is_ok_for_inf == 2) & (is_ok_for_opposite == 0):
			print("++++++ IT IS PLUS ++++++")
		elif (is_ok_for_opposite == 2) & (is_ok_for_inf <= 1):
			print("------ IT IS MINUS -----")
		else:
			print("????? IT IS COMPLICATED ?????")
	return g


def is_subcluster_informative(g, cluster_to_check):
	is_informative_cluster = 2
	if (len(cluster_to_check) / len(g.vs)) < 0.15:
		print("not trully informative " + str(len(cluster_to_check) / len(g.vs)))
		is_informative_cluster -= 1
	if len(cluster_to_check) <= 1:
		print("not enougth information in cluster " + str(len(cluster_to_check) / len(g.vs)))
		is_informative_cluster -= 1
	else:
		shortest_paths = g.shortest_paths(cluster_to_check)
		diameter = g.diameter()
		print(diameter)
		min_dist_to_informative = [99999] * len(g.vs)
		for row in shortest_paths:
			for k in range(len(row)):
				if row[k] < min_dist_to_informative[k]:
					min_dist_to_informative[k] = row[k]
		for dist in min_dist_to_informative:
			if (dist > diameter - 1) | (diameter == 1):
				print("can't say anything")
				print(min_dist_to_informative)
				is_informative_cluster -= 1
				break
	if is_informative_cluster == 2:
		print("TRULLY INFORMATIVE!")
		print(min_dist_to_informative)
		return 2
	else:
		if is_informative_cluster == 1:
			print("SEVERELLY INFORMATIVE CLUSTER")
			return 1
		else:
			return 0


def plot_graph(g, name):
	plot(
		g,
		"social_network_" + name + ".png",
		bbox=(1000, 1000),
		margin=100,
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
			graph = make_graf(subcluster_friends_common, False)
			plot_graph(graph, str(cluster_num))
		cluster_num += 1
		subcluster_friends_common = []


def get_friend_information(api, friends_ids):
	sleep(0.25)
	friend_information = api.users.get(user_ids=friends_ids, fields="bdate")
	info = []
	friend_num = 0
	for friend in friend_information:
		if "bdate" in friend_information[friend_num]:
			if friend["bdate"].rfind(".") != -1:
				birth_year = friend["bdate"][friend["bdate"].rfind(".") + 3:]
				if birth_year in ["93", "94", "95", "96"]:
					info.append("+")
				else:
					if len(birth_year) == 2:
						info.append("-")
					else:
						info.append("")
			else:
				info.append("")
		else:
			info.append("")
		friend_num += 1
	return info


# noinspection PyBroadException
def main():
	api = initialisation()
	my_friends = get_friends(api, researched_id)
	print(my_friends["count"])
	# mutual_list = get_mutual_list(my_friends, api)
	clustered_friends_common = friends_clusterising(m_list)
	plot_subclusters(clustered_friends_common)
	graph = make_graf(clustered_friends_common, True)
	plot_graph(graph, "all")


main()
