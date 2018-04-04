# -*- coding: utf-8 -*-
import sys
from random import randint
from time import sleep

import numpy as np
import vk
from igraph import Graph, plot, load
from transliterate import translit

from tok import *


def initialisation():  # инициализация для вк апи
	session = vk.Session(access_token=my_token)
	api = vk.API(session, v='5.71', lang='ru', timeout=10)
	return api

api = initialisation()
reload(sys)
sys.setdefaultencoding("utf-8")

# researched_id = 22846933
researched_id = 53523636
user_friends=[]


# researched_id = 13221877

researched_year = api.users.get(user_ids=researched_id, fields="bdate")
researched_year = int(researched_year[0]["bdate"][researched_year[0]["bdate"].rfind(".") + 3:])
years_threshold = [str(researched_year - 2), str(researched_year - 1), str(researched_year),
	str(researched_year + 1), str(researched_year + 2)]


def get_friends(api, userid):
	user_friends = api.friends.get(user_id=userid)
	return user_friends

def parse_year(x):
	if "bdate" in x:
		bdate=x["bdate"]
		if len(bdate)>5:
			return bdate[bdate.rfind(".")+3:]
	return ""

def write_ids_to_file(api, researched_id):
	user_friends = get_friends(api, researched_id)["items"]
	file = open("myfriends/myfriends", 'w')
	for line in user_friends:
		print>>file, line
	return user_friends

def add_year(friends_byear):
	file = open ("myfriends/myfriends", 'r')
	lines = file.read().splitlines()
	lines = zip(lines, friends_byear)
	file.close()
	file = open ("myfriends/myfriends", 'w')
	for line in lines:
		if line[1]:
			if line [1] in years_threshold:
				file.write(line[0]+' '+line[1]+' 1'+'\n')
				users_same_year.append(line[0])
			# else:
			# 	file.write(line[0] + ' ' + line[1] + ' 0' + '\n')
	file.close()

users_same_year=[]
write_ids_to_file(api,researched_id)
file=open("myfriends/myfriends", 'r')
for line in file:
	user_friends.append(line)

friends_byear = api.users.get(user_ids=user_friends, fields="bdate")
friends_byear = map(parse_year, friends_byear)
add_year(friends_byear)
api.users.get




