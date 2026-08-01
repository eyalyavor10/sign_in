import pickle
import hashlib
import random
import string

pepper='deafpugfdea i'


def remove_email(email):
    print(email)
    if user_exists(email):

        with open('dic.pkl', 'rb') as file:
            dic = pickle.load(file)
        dic.pop(email)

        with open('dic.pkl','wb') as file:
            pickle.dump(dic,file)
        print('deleted')


def generate_salt(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string
def sign_up(username,password):

    if user_exists(username):
        return False
    with open('dic.pkl', 'rb') as file:
        dic = pickle.load(file)
    salt=generate_salt(4)
    dic[username] = [hashlib.sha256((salt+password+pepper).encode()).hexdigest(),salt]
    with open('dic.pkl', 'wb') as file:
        dic = pickle.dump(dic,file)

    return True

def user_exists(username):
    global pepper
    with open('dic.pkl', 'rb') as file:
        dic = pickle.load(file)
    return username in dic.keys()
def login_okay(username,password):
    with open('dic.pkl', 'rb') as file:
        dic = pickle.load(file)
    if user_exists(username):
        if hashlib.sha256((dic[username][1]+password+pepper).encode()).hexdigest() == dic[username][0]:
            return True
        return False
    return False






