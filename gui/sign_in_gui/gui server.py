import socket
import pickle
import threading
import picklemodule

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import ECC
from Crypto.Hash import SHAKE128
from Crypto.Protocol.DH import key_agreement

size_of_size=8
key=b''
going_dark=[]
lock=threading.Lock()
public_key=RSA.generate(3072)

def rec_amount(sock, size):
    d = b''
    while len(d) < size:
        data = sock.recv(size - len(d))
        if len(data) == 0:
            return b''
        d += data
    return d


def rec_buy_size(sock,decrypt):
    global size_of_size
    global key
    global first
    length = rec_amount(sock, size_of_size).decode()
    if length=='':
        return b''
    x = rec_amount(sock, int(length))
    if decrypt:
        cipher = AES.new(key, AES.MODE_CTR, nonce=x[:8])
        x = cipher.decrypt(x[8:])
    return x

def send(data,clisock,i):
    global key
    global going_dark

    if going_dark[i]:
        cipher = AES.new(key, AES.MODE_CTR)
        data = cipher.encrypt(data)
        data=cipher.nonce+data
    if going_dark[i]==False and pickle.loads(data)[0]=='key' and pickle.loads(data)[1]=='succ':
        going_dark[i]=True
    length=str(len(data)).zfill(8).encode()
    clisock.send(length+data)

    print (f'sent {i}')

def checkdic(username,password):
    dic={}
    answer=[]
    if picklemodule.login_okay(username,password):
        answer = ['login', 'succ']
    else:
        answer = ['login', 'err', '0']
    return answer

def add_user(username,password):
    with lock:
        did_it=picklemodule.sign_up(username,password)
        if did_it:
            return ['signup','succ']
        return ['signup', 'err', '0']

def remove_user(email):
    with lock:
        did_it=picklemodule.remove_email(email)
        return did_it

def kdf(x):
    return SHAKE128.new(x).read(32)
def handle_client(clisock,a,i):
    global key
    global going_dark
    global public_key
    going_dark.append(False)
    while True:
        answer = []
        data=rec_buy_size(clisock,going_dark[i])
        if data == b'':
            break

        elif not going_dark[i]:
            arr = pickle.loads(data)
            if arr[0]=='swap':

                if arr[1]=='RSA':
                    answer=['swap','ok']
                elif arr[1]=='DH':
                    peer_key=ECC.import_key(arr[2])
                    V = ECC.generate(curve='p256')
                    arr=['swap','ok',V.public_key().export_key(format='PEM')]
                    send(pickle.dumps(arr), clisock, i)
                    key= key_agreement(static_priv=V, static_pub=peer_key,kdf=kdf)
                    answer=['key','succ']
                else:
                    answer=['swap','err']


            elif arr[0]=='request':
                if arr[1]=='public_key':
                    answer=['request',public_key.public_key().export_key()]
                send(pickle.dumps(answer), clisock, i)
                d=rec_buy_size(clisock,going_dark[i])
                private_key = public_key.export_key(pkcs=8,protection='PBKDF2WithHMAC-SHA512AndAES256-CBC',prot_params={'iteration_count': 131072})
                cipher = PKCS1_OAEP.new(RSA.import_key(private_key))
                message = cipher.decrypt(d)
                message=pickle.loads(message)
                if message[0] == 'key':
                    try:
                        key = message[1]
                        answer = ['key', 'succ']
                    except:
                        answer = ['key', 'err']





        else:

            print (f'recived packet from client number {i}')

            #here you decrypt


            arr=pickle.loads(data)
            if arr[0]=='login':
                answer=checkdic(arr[1],arr[2])

            elif arr[0]=='signup':
                answer=add_user(arr[1],arr[2])


            elif arr[0]=='exists':
                answer=picklemodule.user_exists(arr[1])
                if answer:
                    answer=['exists','succ']
                else:
                    answer = ['exists', 'err']

            elif arr[0]=='remove':
                answer=remove_user(arr[1])
                if answer:
                    answer=['exists','succ']
                else:
                    answer = ['exists', 'err']

        send(pickle.dumps(answer),clisock,i)

    clisock.close()
    print (f'bye client {i}')
def main():
    print ("starting")
    i=0
    arr=[]
    sock = socket.socket()
    sock.bind(('0.0.0.0', 12346))
    sock.listen(15)
    while True:
        c,a=sock.accept()
        print (f'new client: {i}')

        t=threading.Thread(target=handle_client,args=(c,a,i))
        i += 1
        arr.append(t)
        t.start()





if __name__=="__main__":
    main()
