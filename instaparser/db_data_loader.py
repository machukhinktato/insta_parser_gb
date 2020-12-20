from pymongo import MongoClient
from pprint import pprint
from spiders.VARIABLES import *


def check_db_data(username, interest):
    db = MongoClient('localhost', 27017)
    table = db['instagram_parsing']
    for elm in table['instaspider'].find({'data': f'{username} {interest}'}):
        pprint(f"{username} {interest} : {elm['username'][0]}")


if __name__ == '__main__':
    check_db_data(USER_1, 'follow')
    check_db_data(USER_1, 'follower')
    check_db_data(USER_2, 'follow')
    check_db_data(USER_2, 'follower')
