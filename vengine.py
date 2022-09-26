def error(disc="<3"):
    raise Exception(f"Error {disc}")

def ltz_round(num):
    return round(float(num),8)

def add_sq(string):
    return "'"+string+"'"

def is_num(chk):
    try:
        ltz_round(chk)
        return True
    except:
        return False

def is_valid_var_name(varname):
    allowed="abcdefghijklmnopqrstuvwxyz"
    allowed+=allowed.upper()
    allowed+="_"
    for x in allowed:
        varname=varname.replace(x,"")
    if varname=="":
        return True
    else:
        return False

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
    operators=["*","/","%","+","-","=","<",">"]
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
        if x == "=" and x==tokens[len(tokens)-1]:
            del tokens[len(tokens)-1]
            tokens.append("==")
            continue
        if x in operators:
            append_before=""
            if cache!="":
                if cache[-1]=="!":
                    cache=cache[:-1]
                    append_before+='!'
                tokens.append(cache)
            cache=""
            msg=""
            tokens.append((append_before+x))
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
        if x==",":
            if cache!="":
                if cache[-1]==",":
                    tokens.append(cache[:-1])
                    cache=""
                    msg=""
                else:
                    tokens.append(cache)
                    cache=""
                    msg=""
            tokens.append(",")
            continue
        if x==" " and msg=="":
            if cache=="":
                pass
            else:
                if cache!=" ":
                    tokens.append(cache)
                    cache=""
                    msg=""
        if x=="'":
            if msg!="str":
                msg="str"
                cache+=x
                continue
            if msg=="str":
                msg=""
                tokens.append(cache+"'")
                cache=""
        if cache=="in" or cache=="or" or cache=="and" or cache=="import" or cache=="not":
            tokens.append(" "+cache+" ")
            cache=""
    if cache!="":
        tokens.append(cache)
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
    global tokens,cache,state,alt,last,msg
    code=code.replace("\n","")
    tokens=[]
    cache=""
    state=""
    alt=""
    last=""
    msg=""
    def appender(to_append):
        global tokens,cache,state,alt,last,msg
        tokens.append(to_append)
        msg=""
        cache=""
        state=""
        alt=""
        last=to_append
    for x in code:
        execd=False
        if x==" " and cache!="" and state!="str" and state!="expr" and msg!="first_quote":
            execd=True
            appender(cache)
        if x==" " and cache=="" and state!="str" and state!="expr" and msg!="first_quote":
            execd=True
        if execd==False and x==" " and state=="str":
            cache+=x
        if x=="'":
            if msg=="":
                execd=True
                state="str"
                msg="first_quote"
            elif msg=="first_quote":
                msg=""
                cache+="'"
        if state=="str" and msg=="first_quote":
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

def expr_pre_processor(expr,partial=False):
    operators="%/+-*,<>"
    expr_tokens=break_expr(expr)
    i=-1
    new_exprs=[]
    for x in expr_tokens:
        i+=1
        if x=="true":
            expr_tokens[i]=True
            new_exprs.append(True)
        elif x=="false":
            expr_tokens[i]==False
            new_exprs.append(False)
        else:
            new_exprs.append(x)
    expr_tokens=new_exprs
    if " import " in expr_tokens:
        raise Exception("Dangerous Input detected")
    new_expr_tokens=[]
    for x in expr_tokens:
        if x in symbol_table["vars"]:
            if type(symbol_table[x])==type("") and not partial:
                new_expr_tokens.append("'"+symbol_table[x]+"'")
            elif partial:
                if x=="vars":
                    new_expr_tokens.append(f"vars")
                else:
                    new_expr_tokens.append(x)
            else:
                new_expr_tokens.append(symbol_table[x])
            continue
        new_expr_tokens.append(x)
    for x in new_expr_tokens:
        if type(x)==type(0.1):
            if x>18446744073709551616:
                error("Integer larger than 2**64")
    new_expr=""
    for x in new_expr_tokens:
        new_expr+=str(x)
    i=-1
    for x in new_expr:
        i+=1
        if i==0:
            continue
        if new_expr[i]=="(" and (new_expr[i-1]!="(" and new_expr[i-1] not in operators):
            raise Exception("Dangerous Input detected")
    i=-1
    for x in new_expr:
        i+=1
        if i==0:
            continue
        if new_expr[i]=="*" and (new_expr[i-1]=="*" or new_expr[i-1]=="'"):
            raise Exception("Dangerous Input detected")
    new_expr=""
    for x in new_expr_tokens:
        if x=="vars":
            new_expr+=str("list(locals().keys())")
        else:
            new_expr+=str(x)
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
            if type(x)==type((1,2)):
                val[i]=list(x)
    try:
        if type(val)!=type(True):
            return ltz_round(val)
        return val
    except:
        return val

def parser(tokenz,st={},debug=True,gas=False,compile=False):
    global symbol_table,funcs,trans,omit
    if compile:
        global compiled,indents
        compiled="tx={}"
        indents=0
        def add_compile(script):
            global compiled,indents
            compiled+="\n"+("    "*indents)+script
    if gas:
        global fees
        fees=0
        st["txamount"]=1
        st["txsender"]="x"*64
        st["txcurr"]="LTZ"
        st["txmsg"]="test"
    trans=None
    funcs={}
    omit=None
    symbol_table=st
    symbol_table["vars"]=list(symbol_table.keys())
    identifiers=["var","list","print","if","tx",";","int","str","float"]
    def internal(tokenz,infunc=False):
        i=-1
        ignore=[]
        global symbol_table,funcs,trans,omit
        if gas:
            global fees
        if compile:
            global compiled,indents
        for x in tokenz:
            if gas:
                fees+=len(str(x))
            i+=1
            if i not in ignore and x!=";":
                args=0
                n=0
                while True:
                    if gas:
                        fees+=1
                    n+=1
                    try:
                        if tokenz[i+n]==";":
                            break
                    except:
                        error("Missing ';' for line break")
                    args+=1
                if x == "var":
                    if args==3 and tokenz[i+2]=="=" and ((tokenz[i+3][0]=="'" and tokenz[i+3][-1]=="'") or (tokenz[i+3]=="true" or tokenz[i+3]=="false") or (tokenz[i+3][0]=="(" and tokenz[i+3][-1]==")") or is_num(tokenz[i+3]) or tokenz[i+3] in symbol_table["vars"]) and is_valid_var_name(tokenz[i+1]) and tokens[i+1]!="tx" and tokens[i+1]!="vars":
                        if tokenz[i+3] in symbol_table['vars']:
                            if gas:
                                fees+=len(str(tokenz[i+1]))
                                fees+=len(str(tokenz[i+3]))
                                fees+=len(str(symbol_table[tokenz[i+3]]))
                            if compile:
                                add_compile(f"{tokenz[i+1]}={tokenz[i+3]}")
                            symbol_table[tokenz[i+1]]=refactor_temp(symbol_table[tokenz[i+3]])
                        elif tokenz[i+3][0]=="(" and tokenz[i+3][-1]==")":
                            value=expr_post_processor(expr_pre_processor(tokenz[i+3]))
                            if gas:
                                fees+=len(str(expr_pre_processor(tokenz[i+3])))
                                fees+=len(str(tokenz[i+1]))
                            if type(value)==type((1,2)):
                                value=list(value)
                            if compile:
                                add_compile(f"{tokenz[i+1]}=[{tokenz[i+3][1:-1]}]")
                            symbol_table[tokenz[i+1]]=value
                        elif tokenz[i+3]=="true" or tokenz[i+3]=='false':
                            if gas:
                                fees+=len(str(tokenz[i+3]))
                                fees+=5
                            if tokenz[i+3]=="true":
                                if compile:
                                    add_compile(f"{tokenz[i+1]}={add_sq(tokenz[i+3])}.capitalize()=='True'")
                                symbol_table[tokenz[i+1]]=True 
                            else:
                                if compile:
                                    add_compile(f"{tokenz[i+1]}={add_sq(tokenz[i+3])}.capitalize()=='True'")
                                symbol_table[tokenz[i+1]]=False
                        else:
                            if gas:
                                fees+=len(str(tokenz[i+1]))
                                fees+=len(str(tokenz[i+3]))
                            if compile:
                                if is_num(tokenz[i+3]):
                                    add_compile(f"{tokenz[i+1]}={(tokenz[i+3])}")
                                else:
                                    add_compile(f"{tokenz[i+1]}={add_sq(refactor_temp(tokenz[i+3]))}")
                            symbol_table[tokenz[i+1]]=refactor_temp(tokenz[i+3])
                        ignore.append(i+1)
                        ignore.append(i+2)
                        ignore.append(i+3)
                        symbol_table["vars"].append(tokenz[i+1])
                        if gas:
                            fees+=len(str(tokenz[i+1]))
                        continue
                    else:
                        if debug:
                            print("Syntax Error detected while defining variable.", (tokenz[i+3][0]=="(" and tokenz[i+3][-1]==")"),tokenz[i+3])
                        error("Syntax Error detected while defining variable.")
                if x=="append" and args==2 and tokenz[i+1] in symbol_table["vars"]:
                    if tokenz[i+2][0]=="(" and tokenz[i+2][-1]==")":
                        symbol_table[tokenz[i+1]].append(expr_post_processor(expr_pre_processor(tokenz[i+2])))
                    elif tokenz[i+2] in symbol_table["vars"]:
                        symbol_table[tokenz[i+1]].append(symbol_table[tokenz[i+2]])
                    else:
                        symbol_table[tokenz[i+1]].append(refactor_temp(tokenz[i+2]))
                    if tokenz[i+1] not in symbol_table["vars"]:
                        symbol_table["vars"].append(tokenz[i+1])
                    if compile:
                        add_compile(f"{tokenz[i+1]}.append({tokenz[i+2]})")
                    if gas:
                        fees+=len(str(f"{tokenz[i+1]}={symbol_table[tokenz[i+2]]}"))
                    ignore.append(i+1)
                    ignore.append(i+2)
                    continue
                if x=="remove" and args==2 and tokenz[i+1] in symbol_table["vars"]:
                    if tokenz[i+2][0]=="(" and tokenz[i+2][-1]==")":
                        symbol_table[tokenz[i+1]].remove(expr_post_processor(expr_pre_processor(tokenz[i+2])))
                    elif tokenz[i+2] in symbol_table["vars"]:
                        symbol_table[tokenz[i+1]].remove(symbol_table[tokenz[i+2]])
                    else:
                        symbol_table[tokenz[i+1]].remove(refactor_temp(tokenz[i+2]))
                    if tokenz[i+1] not in symbol_table["vars"]:
                        symbol_table["vars"].remove(tokenz[i+1])
                    if compile:
                        add_compile(f"{tokenz[i+1]}.remove({tokenz[i+2]})")
                    if gas:
                        fees+=len(str(f"{tokenz[i+1]}={symbol_table[tokenz[i+2]]}"))
                    ignore.append(i+1)
                    ignore.append(i+2)
                    continue
                if x=="store" and args==3 and tokenz[i+3] in symbol_table["vars"] and tokenz[i+1] in symbol_table["vars"] and type(symbol_table[tokenz[i+1]])==type([]) and (tokenz[i+2] in symbol_table["vars"] or is_num(tokenz[i+2])):
                    val=None
                    if tokenz[i+2] in symbol_table["vars"]:
                        val=int(symbol_table[tokenz[i+2]])
                    else:
                        val=int(tokenz[i+2])
                    try:
                        symbol_table[tokenz[i+1]][val]
                    except:
                        error("Invalid index for list")
                    symbol_table[tokenz[i+3]]=symbol_table[tokenz[i+1]][val]
                    if tokenz[i+2] not in symbol_table["vars"]:
                        symbol_table["vars"].append(tokenz[i+2])
                    if compile:
                        add_compile(f"{tokenz[i+3]}={tokenz[i+1]}[{tokenz[i+2]}]")
                    if gas:
                        fees+=len(str(symbol_table[tokenz[i+1]][val]))
                    ignore.append(i+1)
                    ignore.append(i+2)
                    ignore.append(i+3)
                    continue
                if x=="print" and args==1:
                    ignore.append(i+1)
                    if debug:
                        if tokenz[i+1] not in identifiers:
                            if tokenz[i+1] in symbol_table['vars']:
                                if gas:
                                    fees+=len(str(tokenz[i+1]))
                                print(symbol_table[tokenz[i+1]])
                                continue
                            if tokenz[i+1][0]=="(" and tokenz[i+1][-1]==")":
                                if gas:
                                    fees+=len(str(expr_pre_processor(tokenz[i+1])))
                                print(expr_post_processor(expr_pre_processor(tokenz[i+1])))
                                continue
                            if gas:
                                fees+=len(str(tokenz[i+1]))
                            print(refactor_temp(tokenz[i+1]))
                            continue
                        else:
                            print("Invalid print statement specified")
                            error("Invalid print statement")
                    continue
                if x=="tx":
                    if args==3 and tokenz[i+1] not in identifiers and tokenz[i+2] not in identifiers:
                        if compile:out_str=""
                        if gas:
                            fees+=100
                        amount=""
                        receiver=""
                        if is_num(tokenz[i+1]):
                            if compile:
                                add_compile(f"amount=float({tokenz[i+1]})")
                            amount=ltz_round(tokenz[i+1])
                        elif tokenz[i+1] in symbol_table['vars'] and is_num(symbol_table[tokenz[i+1]]):
                            amount=ltz_round(symbol_table[tokenz[i+1]])
                            if compile:
                                add_compile(f"amount={tokenz[i+1]}")
                        elif tokenz[i+1][0]=="(" and tokenz[i+1][-1]==")":
                            amount=expr_post_processor(expr_pre_processor(tokenz[i+1]))
                            if compile:
                                add_compile(f"amount=float{tokenz[i+1]}")
                        else:
                            if debug:
                                print("Invalid amount for transaction",tokenz[i+1])
                            error(("Invalid amount for transaction",tokenz[i+1]))
                        if tokenz[i+2] in symbol_table['vars'] and is_valid_addr(symbol_table[tokenz[i+2]]):
                            receiver=symbol_table[tokenz[i+2]]
                            if compile:
                                add_compile(f"receiver={tokenz[i+2]}")
                        elif is_valid_addr(tokenz[i+2]):
                            receiver=tokenz[i+2]
                            if compile:
                                add_compile(f"receiver={tokenz[i+2]}")
                        else:
                            if debug:
                                print("Invalid receiver",tokenz[i+2])
                            error("Invalid Receiver")
                        
                        if tokenz[i+3] in symbol_table['vars']:
                            curr=symbol_table[tokenz[i+3]]
                            if compile:
                                add_compile(f"currency={tokenz[i+3]}")
                        else:
                            if compile:
                                add_compile(f"currency={(tokenz[i+3])}")
                            curr=refactor_temp(tokenz[i+3])
                        if amount=="" or receiver=="":
                            if debug:
                                print("Syntax Error while defining transaction")
                            error("Syntax Error while defining transaction")
                        trans={"to":receiver,"amount":amount,"currency":curr}
                        if compile:
                            add_compile("tx={'to':receiver,'amount':amount,'currency':currency}")
                        ignore.append(i+1)
                        ignore.append(i+2)
                        ignore.append(i+3)
                        continue
                if x=="if" and args==2:
                    if gas:
                        fees+=len(str(expr_pre_processor(tokenz[i+1])))
                        fees+=len(str(tokenz[i+1]))
                        fees+=len(str(tokenz[i+2]))
                        fees+=len(str(tokeniser(tokenz[i+2][1:-1])))
                        internal(tokeniser(tokenz[i+2][1:-1]))
                    if compile:
                        add_compile(f"if {expr_pre_processor(tokenz[i+1],partial=True)}:")
                        indents+=1
                    if expr_post_processor(expr_pre_processor(tokenz[i+1])):
                        internal(tokeniser(tokenz[i+2][1:-1]))
                    elif compile:
                        internal(tokeniser(tokenz[i+2][1:-1]))
                        indents-=1
                    ignore.append(i+1)
                    ignore.append(i+2)
                    continue
                if x=="function" and args==2:
                    if refactor_temp(tokenz[i+1]) not in symbol_table['vars'] and refactor_temp(tokenz[i+1]) not in list(funcs.keys()):
                        ignore.append(i+1)
                        ignore.append(i+2)
                        if gas:
                            fees+=len(str(tokenz[i+1]))
                            fees+=len(str(tokeniser(tokenz[i+2][1:-1]+";")))
                        if compile:
                            add_compile(f"def {tokenz[i+1]}():")
                            indents+=1
                            internal(tokeniser(tokenz[i+2][1:-1]+";"))
                            add_func="for x in locals().copy():"
                            add_compile(add_func)
                            indents+=1
                            add_func="globals()[x]=locals()[x]"
                            add_compile(add_func)
                            indents-=1
                            indents-=1
                        funcs[tokenz[i+1]]=tokeniser(tokenz[i+2][1:-1]+";")
                    continue
                if x=="exec" and args==1 or (args==2 and is_valid_var_name(tokenz[i+2])):
                    if infunc:
                        error("Cannot execute functions inside of running function instances")
                    if tokenz[i+1] in list(funcs.keys()) and args==1:
                        ignore.append(i+1)
                        if compile:
                            add_compile(f"{tokenz[i+1]}()")
                        internal(funcs[tokenz[i+1]],infunc=True)
                        omit=None
                        continue
                    if tokenz[i+1] in list(funcs.keys()) and args==2:
                        ignore.append(i+1)
                        ignore.append(i+2)
                        if compile:
                            add_compile(f"{tokenz[i+2]}={tokenz[i+1]}()")
                        internal(funcs[tokenz[i+1]],infunc=True)
                        if gas:
                            fees+=len(str(tokenz[i+2]))
                            fees+=len(str(omit))
                        symbol_table[tokenz[i+2]]=omit
                        symbol_table["vars"].append(tokenz[i+2])
                        omit=None
                        continue
                if x=="str" and args==1:
                    if tokenz[i+1] in symbol_table["vars"] and type(symbol_table["vars"])!=type(""):
                        symbol_table[tokenz[i+1]]=add_sq(tokenz[i+1])
                        if compile:
                            add_compile(f"{tokenz[i+1]}=str({tokenz[i+1]})")
                        ignore.append(i+1)
                        continue
                if x=="float" and args==1:
                    if tokenz[i+1] in symbol_table["vars"] and type(symbol_table["vars"])!=type(0.1):
                        symbol_table[tokenz[i+1]]=float(tokenz[i+1])
                        if compile:
                            add_compile(f"{tokenz[i+1]}=float({tokenz[i+1]})")
                        ignore.append(i+1)
                        continue
                if x=="del" and args==1 and tokenz[i+1] in symbol_table["vars"]:
                    del symbol_table[tokenz[i+1]]
                    symbol_table["vars"].remove(tokenz[i+1])
                    if compile:
                        add_compile(f"del locals()[{add_sq(tokenz[i+1])}]")
                    ignore.append(i+1)
                    continue
                if x=="omit" and args==1:
                    ignore.append(i+1)
                    if tokenz[i+1][0]=="(" and tokenz[i+1][-1]==")":
                        omit=expr_post_processor(expr_pre_processor(tokenz[i+1]))
                        if compile:
                            add_compile(f"return {tokenz[i+1]}")
                        if gas:
                            fees+=len(str(expr_pre_processor(tokenz[i+1])))
                    elif tokenz[i+1] in symbol_table["vars"]:
                        omit=symbol_table[tokenz[i+1]]
                        if compile:
                            add_compile(f"return {tokenz[i+1]}")
                        if gas:
                            fees+=len(str(symbol_table[tokenz[i+1]]))
                    else:
                        if compile:
                            if is_num(tokenz[i+1]):
                                add_compile(f"return {tokenz[i+1]}")
                            else:
                                add_compile(f"return {add_sq(tokenz[i+1])}")
                        omit=refactor_temp(tokenz[i+1])
                        if gas:
                            fees+=len(str(tokenz[i+1]))
                    break
                else:
                    if debug:
                        print(f"Syntax Error : {x} is an invalid token")
                    error(f"Syntax Error : {x} is an invalid token")
    internal(tokenz)
    del symbol_table['vars']
    if gas:
        return fees
    if compile:
        return compiled
    return symbol_table,trans

def run(script,symbol_table={},debug=True,gas=False,compile=False):
    if '"' in script or '{' in script or '}' in script:
        raise Exception('Double quote character " is not allowed')
    parse_tokens=tokeniser(script)
    print(parse_tokens)
    return parser(parse_tokens,symbol_table,debug,gas,compile)

if __name__=="__main__":
    env={}
    while True:
        line=input(">> ")
        try:
            env=run(line,env)[0]
        except Exception as e:
            print(e)