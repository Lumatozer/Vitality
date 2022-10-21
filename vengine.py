import os,json,sys,builtins
import traceback

def get_cwd():
    return os.getcwd().replace("\\","/")
def get_abs(path):
    return os.path.abspath(path).replace("\\","/")
def is_safe_path(path,folder=""):
    return str(get_cwd()+f"/"+folder) in str(get_abs(get_cwd()+f"/"+folder+path))

def error(disc="<3",line=1):
    line_on_error=formatted_code.split('\n')[line-1]
    if line!=0:
        sys.exit(f"Line {line} : {line_on_error} \n"+f"Error {disc}")
    else:
        sys.exit(f"Error {disc}")

def ltz_round(num):
    return round(float(num),8)

def add_sq(string):
    return "'"+string+"'"

def is_num(chk,integer=False):
    try:
        if not integer:
            ltz_round(chk)
            return True
        if integer:
            int(chk)
            return True
    except:
        return False

def is_valid_var_name(varname):
    allowed="abcdefghijklmnopqrstuvwxyz"
    allowed+=allowed.upper()
    allowed+="_"
    if varname[0]=="_":
        return False
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
        elif x==" " and cache=="":
            execd=True
        if execd==False and x==" " and state=="str":
            cache+=x
            continue
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
    if cache!="":
        appender(cache)
    return tokens

def expr_pre_processor(expr,partial=False,use_st=True):
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
                error("Numbers are too large",0)
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
        if x=="vars" and use_st==False:
            new_expr+=str("list(locals().keys())")
        elif x=="vars":
            new_expr+=str(list(symbol_table.keys()))
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

def parser(tokenz,st={},debug=True,gas=False,compile=False,working_dir=""):
    global symbol_table,funcs,trans,omit,vars_initialized,recursions,line_i
    recursions=[50,0]
    vars_initialized=False
    if compile:
        global compiled,indents
        compiled="tx={}\n"
        indents=0
        def add_compile(script):
            global compiled,indents
            compiled+=("    "*indents)+script+"\n"
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
    blacklist=["vars","tx","recursions","loopi","import","os","json","contract_tx"]+dir(builtins)
    line_i=0
    def internal(tokenz,infunc=False,inloop=False):
        i=-1
        ignore=[]
        global symbol_table,funcs,trans,omit,vars_initialized,recursions,line_i
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
                        error(f"Missing ';' for line break on line {line_i}",line_i)
                    args+=1
                line_i+=1
                if x=='vars:' and args>0 and not vars_initialized:
                    vars_initialized=True
                    init_vars=[]
                    for y in range(1,args+1):
                        if y not in blacklist:
                            init_vars.append(tokenz[i+y])
                    for y in init_vars:
                        if y not in symbol_table["vars"]:
                            symbol_table[y]=None
                            symbol_table["vars"].append(y)
                        if compile:
                            add_compile(f"{y}=None")
                        if gas:
                            fees+=len(y)
                    for y in range(1,args+1):
                        ignore.append(i+y)
                    continue
                if x=="recursions:" and args==1 and is_num(tokenz[i+1]) and int(tokenz[i+1])<=50 and recursions[1]==0:
                    recursions=[int(tokenz[i+1]),1]
                    if compile:
                        add_compile(f"recursions={tokenz[i+1]}")
                    if gas:
                        fees+=len(f"recursions={tokenz[i+1]}")
                    ignore.append(i+1)
                    continue
                if x=="require" and args==1 and is_safe_path(tokenz[i+1],working_dir) and os.path.exists(working_dir+tokenz[i+1]+".dat") and os.path.exists(working_dir+tokenz[i+1]):
                    imported_vars=json.loads(open(working_dir+tokenz[i+1]).read())["symbol_table"]
                    for x in imported_vars.keys():
                        symbol_table[x]=imported_vars[x]
                        symbol_table["vars"].append(x)
                    if compile:
                        add_compile("import json")
                        add_compile(f"working_dir='{working_dir}'")
                        add_compile(f"imported_vars=json.loads(open('{working_dir}'+'{tokenz[i+1]}').read())['symbol_table']")
                        add_compile(f"for x in imported_vars: locals()[x]=imported_vars[x]")
                    if gas:
                        fees+=int(open(tokenz[i+1]+".dat").read())
                    ignore.append(i+1)
                    continue
                if x == "var":
                    if (args==3) and tokenz[i+1] not in blacklist and tokenz[i+1] in symbol_table["vars"] and tokenz[i+2]=="=" and ((tokenz[i+3][0]=="'" and tokenz[i+3][-1]=="'") or (tokenz[i+3]=="true" or tokenz[i+3]=="false") or (tokenz[i+3][0]=="(" and tokenz[i+3][-1]==")") or is_num(tokenz[i+3]) or tokenz[i+3] in symbol_table["vars"]) and is_valid_var_name(tokenz[i+1]):
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
                                if type(value)==type([]):
                                    add_compile(f"{tokenz[i+1]}=[{tokenz[i+3][1:-1]}]")
                                else:
                                    add_compile(f"{tokenz[i+1]}={tokenz[i+3][1:-1]}")
                            symbol_table[tokenz[i+1]]=value
                        elif tokenz[i+3]=="true" or tokenz[i+3]=='false':
                            if gas:
                                fees+=len(str(tokenz[i+3]))
                                fees+=5
                            if tokenz[i+3]=="true":
                                if compile:
                                    add_compile(f"{tokenz[i+1]}=True")
                                symbol_table[tokenz[i+1]]=True 
                            else:
                                if compile:
                                    add_compile(f"{tokenz[i+1]}=False")
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
                        if args==4:
                            ignore.append(i+4)
                        symbol_table["vars"].append(tokenz[i+1])
                        if gas:
                            fees+=len(str(tokenz[i+1]))
                        continue
                    else:
                        error(f"Syntax Error detected while defining variable on line {line_i}",line_i)
                if x=="print" and args==1:
                    ignore.append(i+1)
                    if debug:
                        if tokenz[i+1] not in identifiers:
                            if tokenz[i+1] in symbol_table.keys():
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
                            error(f"Invalid print statement on line {line_i}",line_i)
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
                            error(f"Invalid amount for transaction {tokenz[i+1]} on line {line_i}",line_i)
                        if tokenz[i+2] in symbol_table['vars'] and is_valid_addr(symbol_table[tokenz[i+2]]):
                            receiver=symbol_table[tokenz[i+2]]
                            if compile:
                                add_compile(f"receiver={tokenz[i+2]}")
                        elif is_valid_addr(tokenz[i+2]):
                            receiver=tokenz[i+2]
                            if compile:
                                add_compile(f"receiver={tokenz[i+2]}")
                        else:
                            error(f"Invalid Receiver on line {line_i}",line_i)
                        
                        if tokenz[i+3] in symbol_table['vars']:
                            curr=symbol_table[tokenz[i+3]]
                            if compile:
                                add_compile(f"currency={tokenz[i+3]}")
                        else:
                            if compile:
                                add_compile(f"currency={(tokenz[i+3])}")
                            curr=refactor_temp(tokenz[i+3])
                        if amount=="" or receiver=="":
                            error(f"Syntax Error while defining transaction on line {line_i}",line_i)
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
                        last_st=symbol_table
                        print(symbol_table)
                        internal(tokeniser(tokenz[i+2][1:-1]))
                        symbol_table=last_st
                    if compile:
                        add_compile(f"if {expr_pre_processor(tokenz[i+1],partial=True,use_st=False)}:")
                        indents+=1
                    if expr_post_processor(expr_pre_processor(tokenz[i+1])) and not compile:
                        internal(tokeniser(tokenz[i+2][1:-1]))
                    elif compile:
                        add_compile("pass")
                        internal(tokeniser(tokenz[i+2][1:-1]))
                        indents-=1
                    ignore.append(i+1)
                    ignore.append(i+2)
                    continue
                if x=="function" and args==2:
                    if (refactor_temp(tokenz[i+1]) not in symbol_table['vars'] or symbol_table['vars']==None) and refactor_temp(tokenz[i+1]) not in list(funcs.keys()):
                        ignore.append(i+1)
                        ignore.append(i+2)
                        if gas:
                            fees+=len(str(tokenz[i+1]))
                            fees+=len(str(tokeniser(tokenz[i+2][1:-1]+";")))
                        if compile:
                            add_compile(f"def {tokenz[i+1]}():")
                            indents+=1
                            add_compile("pass")
                            internal(tokeniser(tokenz[i+2][1:-1]+";"))
                            add_compile("for x in locals().copy():")
                            indents+=1
                            add_compile("globals()[x]=locals()[x]")
                            indents-=1
                            indents-=1
                        funcs[tokenz[i+1]]=tokeniser(tokenz[i+2][1:-1]+";")
                    continue
                if x=="str" and args==1:
                    if tokenz[i+1] in symbol_table["vars"] and type(symbol_table["vars"])!=type(""):
                        symbol_table[tokenz[i+1]]=add_sq(str(symbol_table[tokenz[i+1]]))
                        if compile:
                            add_compile(f"{tokenz[i+1]}=str({tokenz[i+1]})")
                        ignore.append(i+1)
                        continue
                if x=="float" and args==1:
                    if tokenz[i+1] in symbol_table["vars"] and type(symbol_table["vars"])!=type(0.1):
                        symbol_table[tokenz[i+1]]=float(symbol_table[tokenz[i+1]])
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
                if x=="loop" and args==1 and not inloop:
                    if compile:
                        add_compile("for loopi in range(1,recursions+1):")
                        indents+=1
                        add_compile("pass")
                        internal(tokeniser(tokenz[i+1][1:-1]),inloop=True)
                        indents-=1
                    if gas:
                        initial_gas=fees
                        last_st=symbol_table
                        internal(tokeniser(tokenz[i+1][1:-1]),inloop=True)
                        symbol_table=last_st
                        new_gas=fees
                        differ_gas=new_gas-initial_gas
                        new_gas=initial_gas
                        fees+=differ_gas*recursions[0]
                    if not compile:
                        for loopi in range(1,recursions[0]+1):
                            internal(tokeniser(tokenz[i+1][1:-1]),inloop=True)
                    ignore.append(i+1)
                    continue
                if x[0]=="." and (x.split(".")[1] in symbol_table["vars"] or x.split(".")[1] in list(funcs.keys())):
                    object_val=x.split(".")[1]
                    if object_val in list(funcs.keys()):
                        if args==0:
                            if infunc:
                                error(f"Cannot execute functions inside of running function instances on line {line_i}",line_i)
                            if object_val in list(funcs.keys()) and args==0:
                                if compile:
                                    add_compile(f"{object_val}()")
                                else:
                                    internal(funcs[object_val],infunc=True)
                                continue
                            if object_val in list(funcs.keys()) and args==1:
                                ignore.append(i+1)
                                if compile:
                                    add_compile(f"{object_val}()")
                                else:
                                    internal(funcs[object_val],infunc=True)
                                omit=None
                                continue
                        if args==1:
                            ignore.append(i+1)
                            if compile:
                                add_compile(f'{tokenz[i+1].replace("$","")}={object_val}()')
                            else:
                                internal(funcs[object_val],infunc=True)
                            if gas:
                                fees+=len(str(tokenz[i+1].replace("$","")))
                                fees+=len(str(omit))
                            symbol_table[tokenz[i+1].replace("$","")]=omit
                            symbol_table["vars"].append(tokenz[i+1].replace("$",""))
                            omit=None
                            continue
                    if object_val in symbol_table["vars"] and type(symbol_table[object_val])==type([]):
                        if args==2:
                            if tokenz[i+1] == "+":
                                if tokenz[i+2][0]=="(" and tokenz[i+2][-1]==")":
                                    symbol_table[object_val].append(expr_post_processor(expr_pre_processor(tokenz[i+2])))
                                elif tokenz[i+2] in symbol_table["vars"]:
                                    symbol_table[object_val].append(symbol_table[tokenz[i+2]])
                                else:
                                    symbol_table[object_val].append(refactor_temp(tokenz[i+2]))
                                if object_val not in symbol_table["vars"]:
                                    symbol_table["vars"].append(object_val)
                                if compile:
                                    store=tokenz[i+2]
                                    if type(expr_post_processor(expr_pre_processor(store,use_st=False)))==type([]):
                                        store="["+store[1:-1]+"]"
                                    add_compile(f"{object_val}.append({store})")
                                if gas:
                                    fees+=len(str(f"{object_val}={symbol_table[tokenz[i+2]]}"))
                                ignore.append(i+1)
                                ignore.append(i+2)
                                continue
                            if tokenz[i+1] == "-":
                                if tokenz[i+2][0]=="(" and tokenz[i+2][-1]==")":
                                    symbol_table[object_val].remove(expr_post_processor(expr_pre_processor(tokenz[i+2])))
                                elif tokenz[i+2] in symbol_table["vars"]:
                                    symbol_table[object_val].remove(symbol_table[tokenz[i+2]])
                                else:
                                    symbol_table[object_val].remove(refactor_temp(tokenz[i+2]))
                                if object_val not in symbol_table["vars"]:
                                    symbol_table["vars"].remove(object_val)
                                if compile:
                                    store=tokenz[i+2]
                                    if type(expr_post_processor(expr_pre_processor(store,use_st=False)))==type([]):
                                        store="["+store[1:-1]+"]"
                                    add_compile(f"{object_val}.remove({store})")
                                if gas:
                                    fees+=len(str(f"{object_val}={symbol_table[tokenz[i+2]]}"))
                                ignore.append(i+1)
                                ignore.append(i+2)
                                continue
                        if tokenz[i+1]=="$" and args==3:
                            val=None
                            if tokenz[i+3].replace("$","") not in symbol_table["vars"]:
                                error(f"Undeclared Variable Detected on line {line_i}",line_i)
                            if tokenz[i+2] in symbol_table["vars"]:
                                val=int(symbol_table[tokenz[i+2]])
                            else:
                                val=int(tokenz[i+2])
                            try:
                                symbol_table[object_val][val]
                            except:
                                error(f"Invalid index for list on line {line_i}",line_i)
                            symbol_table[tokenz[i+3].replace("$","")]=symbol_table[object_val][val]
                            if compile:
                                add_compile(f'{tokenz[i+3].replace("$","")}={object_val}[{tokenz[i+2]}]')
                            if gas:
                                fees+=len(str(symbol_table[tokenz[i+1]][val]))
                            ignore.append(i+1)
                            ignore.append(i+2)
                            ignore.append(i+3)
                            continue
                        if tokenz[i+1]==":" and args==2 and tokenz[i+2].replace("$","") in symbol_table["vars"]:
                            symbol_table[tokenz[i+2].replace("$","")]=len(symbol_table[object_val])
                            if compile:
                                add_compile(f'{tokenz[i+2].replace("$","")}=len({object_val})')
                            if gas:
                                fees+=len(str(len(symbol_table[object_val])))
                            ignore.append(i+1)
                            ignore.append(i+2)
                            ignore.append(i+3)
                            continue
                        if tokenz[i+1]=="::" and args==3:
                            val=None
                            if tokenz[i+3].replace("$","") not in symbol_table["vars"]:
                                error(f"Undeclared Variable Detected on line {line_i}",line_i)
                            if tokenz[i+2] in symbol_table["vars"]:
                                val=symbol_table[tokenz[i+2]]
                            else:
                                val=tokenz[i+2]
                            try:
                                val=ltz_round(val)
                            except:
                                pass
                            try:
                                symbol_table[object_val].index(val)
                            except:
                                error(f"Invalid index for list on line {line_i}",line_i)
                            symbol_table[tokenz[i+3].replace("$","")]=symbol_table[object_val].index(val)
                            if compile:
                                add_compile(f'{tokenz[i+3].replace("$","")}={object_val}.index({tokenz[i+2]})')
                            if gas:
                                fees+=len(str(symbol_table[tokenz[i+1]][val]))
                            ignore.append(i+1)
                            ignore.append(i+2)
                            ignore.append(i+3)
                            continue
                if x=="//":
                    comments=""
                    for argx in range(1,args+1):
                        comments+=tokenz[argx]+" "
                    if gas:
                        fees+=len(comments)
                    if compile:
                        add_compile(f"#{comments}")
                    for argx in range(1,args+1):
                        ignore.append(argx)
                    continue
                else:
                    error(f"Syntax Error : {x} is an invalid token on line {line_i}",line_i)
    internal(tokenz)
    del symbol_table['vars']
    funcs,omit,vars_initialized,recursions,line_i=(None,)*5
    if gas:
        return fees
    if compile:
        return compiled
    return symbol_table,trans

def run(script,symbol_table={},debug=True,gas=False,compile=False,working_dir=""):
    global formatted_code
    formatted_code=formatter(script)
    if '"' in script:
        error('Double quote character " is not allowed',0)
    parse_tokens=tokeniser(script)
    return parser(parse_tokens,symbol_table,debug,gas,compile,working_dir)

def formatter(script):
    new_script=""
    indents=0
    for x in script.replace("\n",""):
        if x==")":
            indents-=4
            if new_script[-4:]=="    ":
                new_script=new_script[:-4]
        new_script+=(x)
        if x==";":
            new_script+="\n"+(" "*indents)
        if x=="(":
            indents+=4
            new_script+="\n"+(" "*indents)
    return new_script


if __name__=="__main__":
    env={}
    while True:
        line=input(">> ")
        try:
            env=run(line,env)[0]
        except Exception as e:
            print(e)