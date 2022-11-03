#Importing some libs
import os,json,sys,builtins
import traceback

#Null class object
class null:
    def __init__(self) -> None:
        pass
    def __add__(self,x):
        return 1
    def __sub__(self,x):
        return 1
    def __truediv__(self,x):
        return 1
    def __rtruediv__(self,x):
        return 1
    def __mod__(self,x):
        return 1
    def __eq__(self, __o: object) -> bool:
        if str(__o)=="null":
            return True
        return False

#These functions are responsible for preventing path traversal
def get_cwd():
    return os.getcwd().replace("\\","/")
def get_abs(path):
    return os.path.abspath(path).replace("\\","/")
def is_safe_path(path,folder=""):
    return str(get_cwd()+f"/"+folder) in str(get_abs(get_cwd()+f"/"+folder+path))

#To gracefully exit with an error
def error(disc="<3",line=1):
    line_on_error=formatted_code.split('\n')[line-1]
    if line!=0:
        sys.exit(f"Line {line} : {line_on_error} \n"+f"Error {disc}")
    else:
        sys.exit(f"Error {disc}")

#To round a number to its 8th decimal
def ltz_round(num):
    return round(float(num),8)

#To add single quotes to a string for ex : alu --> 'alu'
def add_sq(string):
    return "'"+string+"'"

#To check if an object is an integer or a float
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

#Check if the variable names are valid or not
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

#Check if the outgoing address for a transaction is valid or not
def is_valid_addr(addr):
    allowed="abcdefghijklmnopqrstuvwxyz"
    allowed+=allowed.upper()
    allowed+="1234567890"
    allowed+="_"
    for x in allowed:
        addr=addr.replace(x,"")
    if addr=="":
        return True

#To break an arithmetic expression into several tokens
def break_expr(expr):
    tokens=[]
    operators=["*","/","%","+","-","=","<",">"]
    cache=""
    msg=""
    token_i=-1
    for x in expr:
        token_i+=1
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
        if (cache=="in" or cache=="or" or cache=="and" or cache=="not") and tokens[token_i+1]==" ":
            tokens.append(" "+cache+" ")
            cache=""
    if cache!="":
        tokens.append(cache)
    return tokens

#This function return the string without its quotes if it is not a number otherwise as an integer
def refactor_temp(data):
    data=str(data)
    if data[0] == "'" and data[-1]=="'":
        return data[1:-1]
    try:
        return ltz_round(data)
    except:
        pass
    return data

#Break the whole script into tokens
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

#To break more complex arithmetic expressions before their final value can be evaluated
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
            elif type(symbol_table[x])==type(null()):
                new_expr_tokens.append(x)
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
        elif x in symbol_table["vars"] and type(symbol_table[x])==type(null()):
            new_expr+="null"
        elif x=="vars":
            new_expr+=str(list(symbol_table.keys()))
        else:
            new_expr+=str(x)
    return new_expr

#This evalutes the values of the broken down expressions
def expr_post_processor(prep_expr):
    try:
        val=eval(prep_expr,{"null":null()},{"null":null()})
    except Exception as e:
        error(str(e),line_i)
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

#This function is just for checking for overlapping items in lists
def x_notin_y(x1: str,x2: list):
    for x in x2:
        if x in x1:
            return False
    return True

#The main parser. This function parses all the tokens
def parser(tokenz,st={"txcurr":'LTZ',"txsender":'test','txamount':1,'txmsg':'test'},debug=True,gas=False,compile=False,working_dir="",runtime_func="main"):
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
    blacklist=["vars","tx","recursions","loopi","import","os","json","contract_tx","boot"]+dir(builtins)
    line_i=0
    #This the is internal function which processes a particular set of tokens
    def internal(tokenz,func_trace=1,inloop=False,main_func=False):
        i=-1
        ignore=[]
        global symbol_table,funcs,trans,omit,vars_initialized,recursions,line_i
        if gas:
            global fees
        if compile:
            global compiled,indents
        #Going into a for loop for each token
        for x in tokenz:
            if gas:
                fees+=len(str(x))
            i+=1
            #Since the parser has a dynamic seeker, the parser can point to different tokens or ignore some tokens.
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
                #Initialising variables
                if x=="vars:" or x=="recursions:" or x=="function":
                    pass
                elif func_trace==0:
                    #This error is thrown because all code is supposed to be packed inside a main function
                    error("Found tokens outside function body",line_i)
                if x=='vars:' and args>0 and not vars_initialized:
                    vars_initialized=True
                    init_vars=[]
                    for y in range(1,args+1):
                        if tokenz[i+y] not in blacklist and is_valid_var_name(tokenz[i+y]):
                            init_vars.append(tokenz[i+y])
                        else:
                            error("Invalid variable initialization")
                    if compile:
                        add_compile("if 'boot' not in list(locals().keys()):")
                        indents+=1
                        init_compile_str=""
                        for y in init_vars:
                            init_compile_str+=f"{y},"
                        init_compile_str+=f"=[1]*{len(init_vars)}"
                        add_compile(init_compile_str)
                        indents-=1
                        add_compile("boot=null()")
                    for y in init_vars:
                        if y not in symbol_table["vars"] and is_valid_var_name(y):
                            symbol_table[y]=null()
                            symbol_table["vars"].append(y)
                        if gas:
                            fees+=len(y)
                    for y in range(1,args+1):
                        ignore.append(i+y)
                    continue
                #These are the recursions for the number of loops the code will have to go through at max each time
                if x=="recursions:" and args==1 and is_num(tokenz[i+1]) and int(tokenz[i+1])<=50 and recursions[1]==0:
                    recursions=[int(tokenz[i+1]),1]
                    if compile:
                        add_compile(f"recursions={tokenz[i+1]}")
                    ignore.append(i+1)
                    continue
                #Importing scripts
                if x=="#include" and args==1 and is_safe_path(tokenz[i+1],working_dir) and os.path.exists(working_dir+tokenz[i+1]+".dat") and os.path.exists(working_dir+tokenz[i+1]):
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
                #Changing values of variables
                if x == "var":
                    if (args==3) and tokenz[i+1] not in blacklist and tokenz[i+1] in symbol_table["vars"] and tokenz[i+2]=="=" and ((tokenz[i+3][0]=="'" and tokenz[i+3][-1]=="'") or (tokenz[i+3]=="true" or tokenz[i+3]=="false") or (tokenz[i+3][0]=="(" and tokenz[i+3][-1]==")") or is_num(tokenz[i+3]) or tokenz[i+3] in symbol_table["vars"]) and is_valid_var_name(tokenz[i+1]):
                        if tokenz[i+3] in symbol_table['vars']:
                            if gas:
                                fees+=len(str(symbol_table[tokenz[i+3]]))
                            if compile:
                                add_compile(f"globals()['{tokenz[i+1]}']={tokenz[i+3]}")
                            symbol_table[tokenz[i+1]]=refactor_temp(symbol_table[tokenz[i+3]])
                        elif tokenz[i+3][0]=="(" and tokenz[i+3][-1]==")":
                            value=expr_post_processor(expr_pre_processor(tokenz[i+3]))
                            if gas:
                                fees+=len(str(expr_pre_processor(tokenz[i+3])))
                            if type(value)==type((1,2)):
                                value=list(value)
                            if compile:
                                if type(value)==type([]):
                                    add_compile(f"globals()['{tokenz[i+1]}']=[{tokenz[i+3][1:-1]}]")
                                else:
                                    add_compile(f"globals()['{tokenz[i+1]}']={tokenz[i+3][1:-1]}")
                            symbol_table[tokenz[i+1]]=value
                        elif tokenz[i+3]=="true" or tokenz[i+3]=='false':
                            if gas:
                                fees+=10
                            if tokenz[i+3]=="true":
                                if compile:
                                    add_compile(f"globals()['{tokenz[i+1]}']=True")
                                symbol_table[tokenz[i+1]]=True 
                            else:
                                if compile:
                                    add_compile(f"globals()['{tokenz[i+1]}']=False")
                                symbol_table[tokenz[i+1]]=False
                        else:
                            if compile:
                                if is_num(tokenz[i+3]):
                                    add_compile(f"globals()['{tokenz[i+1]}']={(tokenz[i+3])}")
                                else:
                                    add_compile(f"globals()['{tokenz[i+1]}']={add_sq(refactor_temp(tokenz[i+3]))}")
                            symbol_table[tokenz[i+1]]=refactor_temp(tokenz[i+3])
                        ignore.append(i+1)
                        ignore.append(i+2)
                        ignore.append(i+3)
                        if args==4:
                            ignore.append(i+4)
                        symbol_table["vars"].append(tokenz[i+1])
                        continue
                    else:
                        error(f"Syntax Error detected while defining variable on line {line_i}",line_i)
                #Printing (not available on nodes)
                if x=="print" and args==1:
                    ignore.append(i+1)
                    if debug:
                        if tokenz[i+1] not in identifiers:
                            if tokenz[i+1] in symbol_table.keys():
                                print(symbol_table[tokenz[i+1]])
                                continue
                            if tokenz[i+1][0]=="(" and tokenz[i+1][-1]==")":
                                print(expr_post_processor(expr_pre_processor(tokenz[i+1])))
                                continue
                            print(refactor_temp(tokenz[i+1]))
                            continue
                        else:
                            print("Invalid print statement specified")
                            error(f"Invalid print statement on line {line_i}",line_i)
                    continue
                #Output TX from contract
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
                #If statements
                if x=="if" and args==2:
                    if gas:
                        fees+=len(str(expr_pre_processor(tokenz[i+1])))
                        fees+=len(str(tokeniser(tokenz[i+2][1:-1])))
                        last_st=symbol_table
                        internal(tokeniser(tokenz[i+2][1:-1]))
                        symbol_table=last_st
                    if compile:
                        add_compile(f"if {expr_pre_processor(tokenz[i+1],partial=True,use_st=False)}:")
                        indents+=1
                    if expr_post_processor(expr_pre_processor(tokenz[i+1])) and not compile:
                        #As you can see the internal function is again called with the tokens inside of the if true statement
                        internal(tokeniser(tokenz[i+2][1:-1]))
                    elif compile:
                        pre_compile=compiled
                        internal(tokeniser(tokenz[i+2][1:-1]))
                        if compiled==pre_compile:
                            add_compile("pass")
                        indents-=1
                    ignore.append(i+1)
                    ignore.append(i+2)
                    continue
                #Initlializing functions
                if x=="function" and args==2:
                    if tokenz[i+2].replace(" ","")=="()":
                        #Empty functions aren't allowed
                        error("Empty Function Detected",line_i)
                    if (refactor_temp(tokenz[i+1]) not in symbol_table['vars'] or symbol_table['vars']=="") and refactor_temp(tokenz[i+1]) not in list(funcs.keys()):
                        ignore.append(i+1)
                        ignore.append(i+2)
                        if gas:
                            fees+=len(str(tokeniser(tokenz[i+2][1:-1]+";")))
                        if compile:
                            add_compile(f"def {tokenz[i+1]}():")
                            indents+=1
                            last_compiled_state=compiled
                            internal(tokeniser(tokenz[i+2][1:-1]+";"))
                            if last_compiled_state==compiled:
                                add_compile("pass")
                            indents-=1
                        funcs[tokenz[i+1]]=tokeniser(tokenz[i+2][1:-1]+";")
                    continue
                #The next 2 if statements are for type conversion
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
                #To delete / free a variable
                if x=="del" and args==1 and tokenz[i+1] in symbol_table["vars"]:
                    del symbol_table[tokenz[i+1]]
                    symbol_table["vars"].remove(tokenz[i+1])
                    if compile:
                        add_compile(f"del locals()[{add_sq(tokenz[i+1])}]")
                    ignore.append(i+1)
                    continue
                #To return a value from a function
                if x=="omit" and args==1:
                    ignore.append(i+1)
                    if tokenz[i+1][0]=="(" and tokenz[i+1][-1]==")":
                        omit=expr_post_processor(expr_pre_processor(tokenz[i+1]))
                        if compile:
                            add_compile(f"return {tokenz[i+1]}")
                        if gas:
                            fees+=20
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
                #Loops
                if x=="loop" and args==1 and not inloop:
                    if compile:
                        add_compile("for loopi in range(1,recursions+1):")
                        indents+=1
                        pre_compile=compiled
                        internal(tokeniser(tokenz[i+1][1:-1]),inloop=True)
                        if pre_compile==compiled:
                            add_compile("pass")
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
                            internal(tokeniser(tokenz[i+1][1:-1]),inloop=True,func_trace=func_trace+1)
                    ignore.append(i+1)
                    continue
                #This part of the code is responsible for calling arrays and functions
                if x[0]=="." and (x.split(".")[1] in symbol_table["vars"] or x.split(".")[1] in list(funcs.keys())):
                    object_val=x.split(".")[1]
                    if object_val in list(funcs.keys()):
                        #If the called object is a function
                        if func_trace>2:
                            #If the func trace that is the number of total function instances executed in a series to get to this call is more than 2 then a error is produced.
                                error(f"Cannot execute functions inside of multiple running function instances on line {line_i}",line_i)
                        if args==0:
                            if object_val in list(funcs.keys()):
                                if compile:
                                    add_compile(f"{object_val}()")
                                else:
                                    internal(funcs[object_val],func_trace=func_trace+1)
                                continue
                        if args==1:
                            if tokenz[i+1] not in symbol_table["vars"]:
                                error("Variable Undefined",line_i)
                            ignore.append(i+1)
                            if compile:
                                add_compile(f'globals()["{tokenz[i+1].replace("$","")}"]={object_val}()')
                            else:
                                internal(funcs[object_val],func_trace=func_trace+1)
                            if gas:
                                fees+=len(str(omit))
                            symbol_table[tokenz[i+1].replace("$","")]=omit
                            symbol_table["vars"].append(tokenz[i+1].replace("$",""))
                            omit=None
                            continue
                    if object_val in symbol_table["vars"] and type(symbol_table[object_val])==type([]):
                        #If the object called is an array
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
                                    fees+=len(str(tokenz[i+2]))
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
                                    fees+=len(str(tokenz[i+2]))
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
                                fees+=len(str(tokenz[i+1]))
                            ignore.append(i+1)
                            ignore.append(i+2)
                            ignore.append(i+3)
                            continue
                        if tokenz[i+1]=="len" and args==2 and tokenz[i+2].replace("$","") in symbol_table["vars"]:
                            symbol_table[tokenz[i+2].replace("$","")]=len(symbol_table[object_val])
                            if compile:
                                add_compile(f'{tokenz[i+2].replace("$","")}=len({object_val})')
                            if gas:
                                fees+=len(str(len(symbol_table[object_val])))
                            ignore.append(i+1)
                            ignore.append(i+2)
                            ignore.append(i+3)
                            continue
                        if tokenz[i+1]=="insert" and args==3:
                            if tokenz[i+2] in symbol_table["vars"] and is_num(symbol_table[tokenz[i+2]],True) and int(symbol_table[tokenz[i+2]])<=len(symbol_table[object_val]):
                                val = tokenz[i+3]
                                if val[0]=="(" and val[1]==")":
                                    symbol_table[symbol_table[tokenz[i+2]]]=expr_post_processor(expr_pre_processor(tokenz[i+3][1:-1]))
                                else:
                                    symbol_table[symbol_table[tokenz[i+2]]]=tokenz[i+3]
                                if gas:
                                    fees+=len(tokenz[i+3])
                                if compile:
                                    add_compile(f"{object_val}.insert({tokenz[i+2]},{tokenz[i+3]})")
                            elif is_num(tokenz[i+2],integer=True) and int(tokenz[i+2])<=len(symbol_table[object_val]):
                                val = tokenz[i+3]
                                if val[0]=="(" and val[1]==")":
                                    symbol_table[int(tokenz[i+2])]=expr_post_processor(expr_pre_processor(tokenz[i+3][1:-1]))
                                else:
                                    symbol_table[int(tokenz[i+2])]=tokenz[i+3]
                                if gas:
                                    fees+=len(tokenz[i+3])
                                if compile:
                                    add_compile(f"{object_val}.insert({tokenz[i+2]},{tokenz[i+3]})")
                            else:
                                error("Error while inserting item in list",line_i)
                            ignore.append(i+1)
                            ignore.append(i+2)
                            ignore.append(i+3)
                            continue

                        if tokenz[i+1]=="obj" and args==3:
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
                                try:
                                    if val[0]=="'" and val[-1]=="'":
                                        val=val[1:-1]
                                except:
                                    pass
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
                #Comments
                if x=="//":
                    comments=""
                    for argx in range(1,args+1):
                        comments+=tokenz[i+argx]+" "
                    if gas:
                        fees+=len(comments)
                    if compile:
                        add_compile(f"# {comments}")
                    for argx in range(1,args+1):
                        ignore.append(i+argx)
                    continue
                else:
                    error(f"Syntax Error : {x} is an invalid token on line {line_i}",line_i)
    internal(tokenz)
    internal(["."+runtime_func,";"])
    del symbol_table['vars']
    omit,vars_initialized,recursions,line_i=(None,)*4
    if not compile:
        funcs=None
    if gas:
        return fees
    if compile:
        if compiled[-1]=="\n":
            compiled=compiled[:-1]
        return compiled,list(funcs.keys())
    return symbol_table,trans

#Running the script
def run(script,symbol_table={"txcurr":'LTZ',"txsender":'test','txamount':1,'txmsg':'test'},debug=True,gas=False,compile=False,working_dir="",runtime_func="main"):
    global formatted_code
    formatted_code=formatter(script)
    if '"' in script:
        error('Double quote character " is not allowed',0)
    parse_tokens=tokeniser(script)
    return parser(parse_tokens,symbol_table,debug,gas,compile,working_dir,runtime_func)

#A temporary formatter
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
        env=run(line,env)[0]
