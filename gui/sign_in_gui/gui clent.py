import tkinter
from tkinter import *
from tkinter import messagebox

import pickle
import socket

import emailmod
import time
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.PublicKey import ECC
from Crypto.Hash import SHAKE128
from Crypto.Protocol.DH import key_agreement


chose_encrypt=False
global sock
size_of_size=8
key=b''
going_dark=False


def rec_amount(sock, size):
    d = b''

    while len(d) < size:
        data = sock.recv(size - len(d))
        if len(data) == 0:
            return b''
        d += data
    return d

def rec_buy_size(sock):
    global size_of_size
    global key

    length = rec_amount(sock, size_of_size).decode()
    length = int(length)
    print(f"len data: {length}")
    x = rec_amount(sock, length)
    if going_dark:
        cipher = AES.new(key, AES.MODE_CTR, nonce=x[:8])
        x = cipher.decrypt(x[8:])
    return x

def open_eror(eror):
    messagebox.showerror('login failed', eror)

def open_succ_box(d):
    messagebox.showinfo('login',d)

def send(data):
    global key
    d=pickle.dumps(data)
    if going_dark:
        cipher = AES.new(key, AES.MODE_CTR)
        data = cipher.encrypt(data)
        data=cipher.nonce+data
    length=str(len(data)).zfill(8).encode()
    sock.send(length+data)
    print ('sent')

def get_user_and_pass(email,password):
    return emailobj.get(), passwordobj.get()



#tells the server to remove user, so when you change passwords its lik signing up again but with not entering the email (i know it already)
def remove_user(email):
    arr = ['remove', email]
    send(pickle.dumps(arr))
    d = rec_buy_size(sock)

    d = pickle.loads(d)
    if d[0] == 'remove' and d[1] == 'succ':
        return True
    return False




#asks the server if an email exists
def send_exists(email):
    arr=['exists',email]
    send(pickle.dumps(arr))
    d = rec_buy_size(sock)

    d = pickle.loads(d)
    if d[0]=='exists' and d[1]=='succ':
        return True
    return False

#sends the sign up to the server, also forget password
def pack_username_password_send(user,password,root):
    global sock
    root[len(root)-1].withdraw()
    arr=['signup',user,password]
    send(pickle.dumps(arr))
    d=rec_buy_size(sock)
    d=pickle.loads(d)
    if d[0]=='signup' and d[1]=='succ':
        open_succ_box('succes!!!')
    elif d[0]=='signup' and d[1]=='err':
        if d[2]=='0':
            open_eror('username already is taken')

    else:
        open_eror('eror, try again')

    for i in range(0,len(root)):
        if i !=0:
            root[i].destroy()

        else:
            root[0].deiconify()


def send_login(email,password):
    email,password=get_user_and_pass(email,password)
    arr=['login']
    arr.append(email)
    arr.append(password)
    data=pickle.dumps(arr)
    send(data)

    d=rec_buy_size(sock)
    d=pickle.loads(d)
    if d[0]=='login' and d[1]== 'err':
        if d[2]=='0':
            open_eror('login failed')
    elif d[0]=='login' and d[1]=='succ':
        open_succ_box('login was a succes')

















#here when you sign up you give the information
def send_sign_up(root):
    arr=[root]
    global sock
    root.withdraw()
    sign_up = Tk()
    arr.append(sign_up)
    sign_up.title("sign up")

    Label(sign_up, text='email').grid(row=0)
    newemailobj = Entry(sign_up)
    newemailobj.grid(row=1, padx=50)

    Label(sign_up, text='password').grid(row=2)
    newpasswordobj = Entry(sign_up,show='*')
    newpasswordobj.grid(row=3, padx=50)

    Label(sign_up, text=' auth password').grid(row=5)
    newauthpasswordobj = Entry(sign_up,show='*')
    newauthpasswordobj.grid(row=6)

    Button(sign_up, text='submit', command=lambda :auth_before_sign_up(newemailobj.get(),newpasswordobj.get(),newauthpasswordobj.get(),arr)).grid(row=1, column=5)

    mainloop()

# checks the authentication before signing up
def auth_before_sign_up(email,password,authpassword,root):
    if authpassword==password:
        root[len(root)-1].withdraw()
        real_code = emailmod.send_email_verefication(email)
        timenow=time.time()
        verifitication = Tk()
        root.append(verifitication)
        verifitication.title("verifitication code")
        Label(verifitication, text='temporary code').grid(row=0)
        code = Entry(verifitication)
        code.grid(row=1, padx=50)

        Button(verifitication, text='submit',command=lambda: end_sign_up(code.get(), real_code, root, email, password,timenow)).grid(row=1, column=5)
        verifitication.mainloop()
    else:
        open_eror('password and auth dont match')


#and then here it sends the info to the server
def end_sign_up(code,real_code,root,email,password,timenow):
   if code==real_code and time.time()-timenow<(5*60):
       open_succ_box('correct code')
       pack_username_password_send(email,password,root)

   else:
       open_eror('eror')
       root[len(root)-1].destroy()
       root.pop(len(root)-1)
       root[len(root)-1].deiconify()












def send_forgot_pass(root):
    global sock
    arr=[root]
    root.withdraw()
    forgot_password = Tk()
    arr.append(forgot_password)
    forgot_password.title("forgot password")

    Label(forgot_password, text='email').grid(row=0)
    emailobj = Entry(forgot_password)
    emailobj.grid(row=1, padx=50)

    Button(forgot_password, text='submit',command=lambda : send_verfitication(emailobj.get(),arr)).grid(row=1, column=5)
    forgot_password.mainloop()


def send_verfitication(email, root):
    root[len(root)-1].withdraw()
    if send_exists(email):
        timenow=time.time()
        real_code = emailmod.send_email_verefication(email)
        verifitication = Tk()
        root.append(verifitication)
        verifitication.title("verifitication code")
        Label(verifitication, text='temporary code').grid(row=0)

        code = Entry(verifitication)
        code.grid(row=1, padx=50)

        Button(verifitication, text='submit',command=lambda: check_code(code.get(), real_code, root, email,timenow)).grid(row=1, column=5)
        verifitication.mainloop()

    else:
        open_eror('user does not exist,try again')
        for i in range(len(root)):
            if i==0:
                root[0].deiconify()
            else:
                root[i].destroy()
                root.pop(i)


#checks if the verefication is okay and then lets the user change passwords
def check_code(code,real_code,root,email,timenow):
   root[len(root)-1].withdraw()
   if code==real_code and time.time()-timenow<(5*60):
       open_succ_box('correct code')
       remove_user(email)
       send_change_password(email,root)

   else:
    open_eror('not correct code:(')
    root[len(root) - 1].deiconify()


#updates new password
def send_change_password(email,root):
    global sock
    sign_up = Tk()
    root.append(sign_up)
    sign_up.title("change password")

    Label(sign_up, text='password').grid(row=2)
    newpasswordobj = Entry(sign_up,show='*')
    newpasswordobj.grid(row=3, padx=50)

    Label(sign_up, text=' auth password').grid(row=4)
    newauthpasswordobj = Entry(sign_up,show='*')
    newauthpasswordobj.grid(row=5)

    Button(sign_up, text='submit', command=lambda :pack_username_password_send(email,newpasswordobj.get(),root) if newauthpasswordobj.get()==newpasswordobj.get() else open_eror('password and auth dont match')).grid(row=1, column=5)
    mainloop()

def send_RSA(root):
    global sock
    global key
    root.deiconify()
    key = get_random_bytes(16)
    while True:
        arr = ['swap', 'RSA']
        data = pickle.dumps(arr)
        send(data)
        d = rec_buy_size(sock)
        d = pickle.loads(d)
        if d[0] == 'swap' and d[1] == 'ok':
            break
        else:
            open_eror('not good')
            root.iconify()
    arr=['request','public_key']
    data = pickle.dumps(arr)
    send(data)

    d=rec_buy_size(sock)
    d=pickle.loads(d)
    if d[0]=='request':
        arr = ['key', key]
        p_key = RSA.importKey(d[1])
        cipher = PKCS1_OAEP.new(p_key)
        ciphertext = cipher.encrypt(pickle.dumps(arr))
        send(ciphertext)

    d = rec_buy_size(sock)
    d = pickle.loads(d)
    while d[0] == 'key' and d[1] == 'err':
        arr = ['key', key]
        send(pickle.dumps(arr))
        d = rec_buy_size(sock)
        d = pickle.loads(d)

def kdf(x):
    return SHAKE128.new(x).read(32)
def send_DH(root):
    global sock
    global key
    root.deiconify()
    U = ECC.generate(curve='p256')
    while True:
        arr = ['swap', 'DH',U.public_key().export_key(format='PEM')]
        data = pickle.dumps(arr)
        send(data)
        d = rec_buy_size(sock)
        d = pickle.loads(d)
        if d[0] == 'swap' and d[1] == 'ok':
            peer_key=ECC.import_key(d[2])
            break
        else:
            open_eror('not good')
            root.deiconify()
    key= key_agreement(static_priv=U, static_pub=peer_key,kdf=kdf)
    d = rec_buy_size(sock)
    d = pickle.loads(d)
    while d[0] == 'key' and d[1] == 'err':
        arr = ['key', key]
        send(pickle.dumps(arr))
        d = rec_buy_size(sock)
        d = pickle.loads(d)



def send_key(num,root):
    global chose_encrypt
    global going_dark

    chose_encrypt = True
    if num==0:
        send_RSA(root)
    elif num==1:
        send_DH(root)
    root.destroy()

    going_dark=True





def choose():
    encryption = Tk()
    num=tkinter.IntVar()
    Radiobutton(encryption, text='RSA',value=0,variable=num).grid(row=0)
    Radiobutton(encryption, text='Diffie-Hellman',value=1,variable=num).grid(row=1)
    Button(encryption, text='submit', command=lambda:send_key(num.get(),encryption)).grid(row=2)
    encryption.mainloop()

def main():
    global emailobj
    global passwordobj
    global sock
    global chose_encrypt
    sock=socket.socket()
    sock.connect(("127.0.0.1",12346))
    print('connected')

    choose()

    if chose_encrypt:
        master = Tk()

        Label(master, text='email').grid(row=0)
        emailobj = Entry(master)
        emailobj.grid(row=1,padx=50)


        Label(master, text='password').grid(row=2)
        passwordobj= Entry(master,show='*')
        passwordobj.grid(row=3)

        Button(master,text='submit',command=lambda : send_login(emailobj,passwordobj)).grid(row=1,column=5)
        Button(master,text='sign up',command=lambda :send_sign_up(master)).grid(row=3,column=5)

        Button(master, text='forgot password?',command=lambda:send_forgot_pass(master) ).grid(row=5, column=5)

        mainloop()

if __name__=='__main__':
    main()