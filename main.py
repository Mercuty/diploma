from time import sleep

import vk

from tok import my_token


def initialisation():
    session = vk.Session(access_token=my_token)
    api = vk.API(session, v='5.62', lang='ru', timeout=10)
    return api


def get_friends(api, userid):
    user_friends = api.friends.get(user_ids=userid)
    return user_friends


def main():
    api = initialisation()
    my_friends = get_friends(api, 53523636)
    couples_of_friends = int(my_friends["count"] / 20)
    my_friends = my_friends["items"]
    print(couples_of_friends)
    mutural_list={}
    for i in range(couples_of_friends):
        sleep(0.25)
        slice = my_friends[i * 20:(i + 1) * 20]
        try:
            mutural = api.friends.getMutual(target_uids=slice)
            # print(mutural)
        except:
            print("error")
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
    print(mutural_list[2784275])


main()
