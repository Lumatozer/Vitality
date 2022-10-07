import vengine,os,json
print("Choose environment type :\n1. Persistent\n2. Static")
choice=input("Your choice >> ")
try:
    choice=int(choice)
except:
    print("Defaulting to static...")
    choice=1
print("Input file name :")
file_name=input(">> ")
if os.path.exists(file_name):
    pass
else:
    print("Invalid file address")
    exit()
print("Initializing Environment")
script=open(file_name).read()
if choice==1:
    st={}
    print("Environment initialized")
    while True:
        command=input(">> ")
        if command=="provoke":
            txsender=input("tx sender : ")
            txamount=float(input("tx amount : "))
            txcurr=input("tx currency : ")
            txmsg=input("tx msg : ")
            st["txsender"]=txsender
            st["txamount"]=txamount
            st["txcurr"]=txcurr
            st["txmsg"]=txmsg
            st=vengine.run(script,st)[0]
        if command=="view state":
            print(json.dumps(st,indent=4))
else:
    print("Environment initialized")
    while True:
        command=input(">> ")
        if command=="provoke":
            txsender=input("tx sender : ")
            txamount=float(input("tx amount : "))
            txcurr=input("tx currency : ")
            txmsg=input("tx msg : ")
            st={}
            st["txsender"]=txsender
            st["txamount"]=txamount
            st["txcurr"]=txcurr
            st["txmsg"]=txmsg
            print(json.dumps(vengine.run(script,st)[0],indent=4))