symbol_table={}
def is_num(chk):
    try:
        float(chk)
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
        if cache=="in" or cache=="or" or cache=="and":
            tokens.append(" "+cache+" ")
            cache=""
    return tokens

def refactor_temp(str):
    if str[0] == "'" and str[-1]=="'":
        return str[1:-1]
    try:
        return float(str)
    except:
        pass
    return str

def tokeniser(code):
    global tokens,cache,state,alt,last
    code=code.split("\n")
    tokens=[]
    cache=""
    state=""
    alt=""
    last=""
    def appender(to_append):
        global tokens,cache,state,alt,last
        tokens.append(to_append)
        msg=""
        cache=""
        state=""
        alt=""
        last=to_append
    for y in code:
        msg=""
        for x in y:
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
            if x==";" and cache!="":
                execd=True
                appender(cache)
            elif x==";":
                execd=True
                state=""
                msg=""
                cache=""
            if x==")" and state=="expr" and msg==1:
                execd=True
                cache+=x
                appender(cache)
            elif x==")" and state=="expr" and msg!=1:
                cache+=x
                msg=msg-1
                continue
            if state=="expr" and alt!="first":
                execd=True
                cache+=x
            if x=="(":
                alt="first"
                execd=True
                state="expr"
                cache+=x
                if msg=="":
                    msg=1
                msg+=1
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
            if not execd:
                cache+=x
    return tokens

def expr_pre_processor(expr):
    expr_tokens=break_expr(expr)
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
    return new_expr

def expr_post_processor(prep_expr):
    val=eval(prep_expr)
    if type(val)==type((1,2)):
        val=list(val)
        i=-1
        for x in val:
            i+=1
            if type(x)==type(1):
                val[i]=float(x)
    return val

def parser(tokenz,debug=True):
    identifiers=["var","list","print","if","tx"]
    global symbol_table
    symbol_table={}
    def internal(tokenz):
        i=-1
        ignore=[]
        global symbol_table
        for x in tokenz:
            i+=1
            if i not in ignore:
                if x == "var":
                    if tokenz[i+2]=="=" and ((tokenz[i+3][0]=="'" and tokenz[i+3][-1]=="'") or (tokenz[i+3]=="true" or tokenz[i+3]=="false") or (tokenz[i+3][0]=="(" and tokenz[i+3][-1]==")") or is_num(tokenz[i+3]) or tokenz[i+3] in list(symbol_table.keys())) and is_valid_var_name(tokenz[i+1]):
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
                if x == "list":
                    list_operators=["append","remove"]
                    if tokenz[i+1] not in list(symbol_table.keys()) and is_valid_var_name(tokenz[i+1]) and tokenz[i+1] not in list_operators and tokenz[i+1] not in identifiers:
                        symbol_table[tokenz[i+1]]=[]
                        ignore.append(i+1)
                        continue
                    if tokenz[i+1] == "append" and tokenz[i+2] in list(symbol_table.keys()) and type(symbol_table[tokenz[i+2]])==type([]) and tokenz[i+3] not in identifiers:
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
                    if tokenz[i+1] == "remove" and tokenz[i+2] in list(symbol_table.keys()) and type(symbol_table[tokenz[i+2]])==type([]) and tokenz[i+3] not in identifiers:
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
                    if debug:
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
                    if tokenz[i+1] not in identifiers and tokenz[i+2] not in identifiers:
                        amount=""
                        receiver=""
                        if is_num(tokenz[i+1]):
                            amount=float(tokenz[i+1])
                        elif tokenz[i+1] in list(symbol_table.keys()) and is_num(symbol_table[tokenz[i+1]]):
                            amount=float(symbol_table[tokenz[i+1]])
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
                    if symbol_table[tokenz[i+1]]:
                        ignore.append(i+1)
                        ignore.append(i+2)
                        internal(tokeniser(tokenz[i+2][1:-1]+";"))
                    continue
                else:
                    if debug:
                        print(f"Syntax Error : {x} is an invalid token")
                    error()
    internal(tokenz)

def run(script,debug=True):
    try:
        parse_tokens=tokeniser(script)
    except:
        if debug:
            print("Problem while generating tokens")
        error()
    try:
        parser(parse_tokens,debug)
    except:
        if debug:
            print("Problem while parsing tokens")
        error()