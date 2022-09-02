def ltz_round(num):
    return round(float(num),8)

def is_num(chk):
    try:
        ltz_round(chk)
        return True
    except:
        return False

def error():
    raise Exception("Error <3")

def is_valid_var_name(varname):
    allowed="abcdefghijklmnopqrstuvwxyz"
    allowed+=allowed.upper()
    allowed+="_"
    for x in allowed:
        varname=varname.replace(x,"")
    if varname=="":
        return True

def is_valid_addr(addr):
    allowed="abcdefghijklmnopqrstuvwxyz"
    allowed+=allowed.upper()
    allowed+="1234567890"
    allowed+="_"
    for x in allowed:
        addr=addr.replace(x,"")
    if addr=="":
        return True


def break_expr(expr):
    tokens=[]
    operators=["*","/","%","+","-","="]
    cache=""
    msg=""
    for x in expr:
        if x=="(":
            if cache!="":
                tokens.append(cache)
            tokens.append("(")
            cache=""
            msg=""
            continue
        if x in operators:
            if cache!="":
                tokens.append(cache)
            cache=""
            msg=""
            tokens.append(x)
            continue
        if x==")":
            if cache!="":
                tokens.append(cache)
            cache=""
            msg=""
            tokens.append(")")
            continue
        if x!=" " and x!="'":
            cache+=x
        if x=="'":
            if msg!="str":
                msg="str"
                cache+=x
                continue
            if msg=="str":
                msg=""
                tokens.append(cache+"'")
                cache=""
        if cache=="in" or cache=="or" or cache=="and" or cache=="import":
            tokens.append(" "+cache+" ")
            cache=""
    return tokens

def refactor_temp(data):
    data=str(data)
    if data[0] == "'" and data[-1]=="'":
        return data[1:-1]
    try:
        return ltz_round(data)
    except:
        pass
    return data

def tokeniser(code):
    global tokens,cache,state,alt,last
    code=code.replace("\n","")
    tokens=[]
    cache=""
    state=""
    alt=""
    last=""
    msg=""
    def appender(to_append):
        global tokens,cache,state,alt,last
        tokens.append(to_append)
        msg=""
        cache=""
        state=""
        alt=""
        last=to_append
    for x in code:
        execd=False
        if x==" " and cache!="" and state!="str" and state!="expr":
            execd=True
            appender(cache)
        if x==" " and execd==False and state!="str" and state!="expr":
            continue
        if x=="'":
            if msg=="":
                execd=True
                state="str"
                msg="first_quote"
            elif msg=="first_quote":
                msg=""
        if state=="str":
            execd=True
            cache+=x
        if x=="'" and state=="str" and msg!="first_quote":
            execd=True
            appender(cache)
        if x==";" and cache!="" and state!="expr":
            execd=True
            appender(cache)
            appender(x)
        elif x==";" and state!="expr":
            appender(x)
        if x==")" and state=="expr":
            cache+=x
            msg=msg-1
            if msg==0:
                appender(cache)
            continue
        if x=="(":
            execd=True
            state="expr"
            if msg=="":
                msg=0
            msg+=1
        if state=="expr":
            execd=True
            cache+=x
        if x=="=" and state!="expr":
            execd=True
            if cache!="":
                appender(cache)
            if last=="=":
                del tokens[len(tokens)-1]
                appender("==")
            else:
                appender(x)
            continue
        if not execd and x!=";":
            cache+=x
    return tokens

def expr_pre_processor(expr):
    expr_tokens=break_expr(expr)
    if " import " in expr_tokens:
        raise Exception("Dangerous Input detected")
    new_expr_tokens=[]
    for x in expr_tokens:
        if x in list(symbol_table.keys()):
            if type(symbol_table[x])==type(""):
                new_expr_tokens.append("'"+symbol_table[x]+"'")
            else:
                new_expr_tokens.append(symbol_table[x])
            continue
        new_expr_tokens.append(x)
    new_expr=""
    for x in new_expr_tokens:
        new_expr+=str(x)
    i=-1
    for x in new_expr:
        i+=1
        if i==0:
            continue
        if new_expr[i]=="(" and new_expr[i-1]!="(":
            raise Exception("Dangerous Input detected")
    return new_expr

def expr_post_processor(prep_expr):
    val=eval(prep_expr,{},{})
    if type(val)==type((1,2)):
        val=list(val)
        i=-1
        for x in val:
            i+=1
            if type(x)==type(1):
                val[i]=ltz_round(x)
    try:
        return ltz_round(val)
    except:
        return val

def parser(tokenz,st={},debug=True):
    global symbol_table
    symbol_table=st
    identifiers=["var","list","print","if","tx",";","int","str","float"]
    def internal(tokenz):
        i=-1
        ignore=[]
        global symbol_table
        for x in tokenz:
            i+=1
            if i not in ignore and x!=";":
                args=0
                n=0
                while True:
                    n+=1
                    if tokenz[i+n]==";":
                        break
                    args+=1
                if x == "var":
                    if args==3 and tokenz[i+2]=="=" and ((tokenz[i+3][0]=="'" and tokenz[i+3][-1]=="'") or (tokenz[i+3]=="true" or tokenz[i+3]=="false") or (tokenz[i+3][0]=="(" and tokenz[i+3][-1]==")") or is_num(tokenz[i+3]) or tokenz[i+3] in list(symbol_table.keys())) and is_valid_var_name(tokenz[i+1]):
                        if tokenz[i+3] in list(symbol_table.keys()):
                            symbol_table[tokenz[i+1]]=refactor_temp(symbol_table[tokenz[i+3]])
                        elif tokenz[i+3][0]=="(" and tokenz[i+3][-1]==")":
                            value=expr_post_processor(expr_pre_processor(tokenz[i+3]))
                            if type(value)==type((1,2)):
                                value=list(value)
                            symbol_table[tokenz[i+1]]=value
                        elif tokenz[i+3]=="true" or tokenz[i+3]=='false':
                            if tokenz[i+3]=="true":
                                symbol_table[tokenz[i+1]]=True
                            else:
                                symbol_table[tokenz[i+1]]=False
                        else:
                            symbol_table[tokenz[i+1]]=refactor_temp(tokenz[i+3])
                        ignore.append(i+1)
                        ignore.append(i+2)
                        ignore.append(i+3)
                        continue
                    else:
                        if debug:
                            print("Syntax Error detected while defining variable.")
                        error()
                if x=="int" and args==1:
                    symbol_table[tokenz[i+1]]=int(ltz_round(symbol_table[tokenz[i+1]]))
                    ignore.append(i+1)
                    continue
                if x=="float" and args==1:
                    symbol_table[tokenz[i+1]]=ltz_round(symbol_table[tokenz[i+1]])
                    ignore.append(i+1)
                    continue
                if x=="str" and args==1:
                    symbol_table[tokenz[i+1]]=str(symbol_table[tokenz[i+1]])
                    ignore.append(i+1)
                    continue
                if x == "list":
                    list_operators=["append","remove"]
                    if args==1 and tokenz[i+1] not in list(symbol_table.keys()) and is_valid_var_name(tokenz[i+1]) and tokenz[i+1] not in list_operators and tokenz[i+1] not in identifiers:
                        symbol_table[tokenz[i+1]]=[]
                        ignore.append(i+1)
                        continue
                    if args==3 and tokenz[i+1] == "append" and tokenz[i+2] in list(symbol_table.keys()) and type(symbol_table[tokenz[i+2]])==type([]) and tokenz[i+3] not in identifiers:
                        if tokenz[i+3] in list(symbol_table.keys()):
                            symbol_table[tokenz[i+2]].append(symbol_table[tokenz[i+3]])
                            ignore.append(i+1)
                            ignore.append(i+2)
                            ignore.append(i+3)
                            continue
                        if tokenz[i+3][0]=="(" and tokenz[i+3][-1]==")":
                            symbol_table[tokenz[i+2]].append(expr_pre_processor(tokenz[i+3]))
                            ignore.append(i+1)
                            ignore.append(i+2)
                            ignore.append(i+3)
                            continue
                        symbol_table[tokenz[i+2]].append(refactor_temp(tokenz[i+3]))
                        ignore.append(i+1)
                        ignore.append(i+2)
                        ignore.append(i+3)
                        continue
                    if args==3 and tokenz[i+1] == "remove" and tokenz[i+2] in list(symbol_table.keys()) and type(symbol_table[tokenz[i+2]])==type([]) and tokenz[i+3] not in identifiers:
                        if tokenz[i+3] in list(symbol_table.keys()):
                            symbol_table[tokenz[i+2]].remove(symbol_table[tokenz[i+3]])
                            ignore.append(i+1)
                            ignore.append(i+2)
                            ignore.append(i+3)
                            continue
                        if tokenz[i+3][0]=="(" and tokenz[i+3][-1]==")":
                            symbol_table[tokenz[i+2]].remove(expr_post_processor(expr_pre_processor(tokenz[i+3])))
                            ignore.append(i+1)
                            ignore.append(i+2)
                            ignore.append(i+3)
                            continue
                        symbol_table[tokenz[i+2]].remove(refactor_temp(tokenz[i+3]))
                        ignore.append(i+1)
                        ignore.append(i+2)
                        ignore.append(i+3)
                        continue
                if x=="print":
                    if debug and args==1:
                        if tokenz[i+1] not in identifiers:
                            ignore.append(i+1)
                            if tokenz[i+1] in list(symbol_table.keys()):
                                print(symbol_table[tokenz[i+1]])
                                continue
                            if tokenz[i+1][0]=="(" and tokenz[i+1][-1]==")":
                                print(expr_post_processor(expr_pre_processor(tokenz[i+1])))
                                continue
                            print(refactor_temp(tokenz[i+1]))
                            continue
                        else:
                            print("Invalid print statement specified")
                            error()
                    else:
                        if tokenz[i+1] not in identifiers:
                            ignore.append(i+1)
                        continue
                if x=="tx":
                    if args==3 and tokenz[i+1] not in identifiers and tokenz[i+2] not in identifiers:
                        amount=""
                        receiver=""
                        if is_num(tokenz[i+1]):
                            amount=ltz_round(tokenz[i+1])
                        elif tokenz[i+1] in list(symbol_table.keys()) and is_num(symbol_table[tokenz[i+1]]):
                            amount=ltz_round(symbol_table[tokenz[i+1]])
                        else:
                            if debug:
                                print("Invalid amount for transaction",tokenz[i+1])
                            error()
                        if tokenz[i+2] in list(symbol_table.keys()) and is_valid_addr(symbol_table[tokenz[i+2]]):
                            receiver=symbol_table[tokenz[i+2]]
                        elif is_valid_var_name(tokenz[i+2]):
                            receiver=tokenz[i+2]
                        else:
                            if debug:
                                print("Invalid receiver",tokenz[i+2])
                            error()
                        if debug:
                            print("Tx",amount,receiver)
                        if amount=="" or receiver=="":
                            if debug:
                                print("Syntax Error while defining transaction")
                            error()
                        ignore.append(i+1)
                        ignore.append(i+2)
                        continue
                if x=="if":
                    if expr_post_processor(expr_pre_processor(tokenz[i+1])):
                        ignore.append(i+1)
                        ignore.append(i+2)
                        internal(tokeniser(tokenz[i+2][1:-1]+";"))
                    continue
                else:
                    if debug:
                        print(f"Syntax Error : {x} is an invalid token")
                    error()
    internal(tokenz)
    return symbol_table

def run(script,symbol_table={},debug=True):
    try:
        parse_tokens=tokeniser(script)
    except:
        if debug:
            print("Problem while generating tokens")
        error()
    try:
        return parser(parse_tokens,symbol_table,debug)
    except:
        if debug:
            print("Problem while parsing tokens")
        error()