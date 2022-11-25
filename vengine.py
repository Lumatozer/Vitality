#Importing some libs
import os,json,sys,builtins
import traceback

def valid_type(type_query):
    if type_query in ["num","arr","str","bool","set"]:
        return True
    return False

def type_default(type_query):
    if type_query=="arr":
        return []
    if type_query=="str":
        return ""
    if type_query=="num":
        return 1
    if type_query=="bool":
        return True
    if type_query=="set":
        return {}

def type2vartype(type_query):
    if type_query==type([]):
        return "arr"
    if type_query==type(""):
        return "str"
    if type_query==type(1) or type_query==type(0.1):
        return "num"
    if type_query==type(True):
        return "bool"
    if type_query==type_query({}):
        return {}

#These functions are responsible for preventing path traversal
def get_cwd():
    return os.getcwd().replace("\\","/")
def get_abs(path):
    return os.path.abspath(path).replace("\\","/")
def is_safe_path(path,folder=""):
    return str(get_cwd()+f"/"+folder) in str(get_abs(get_cwd()+f"/"+folder+path))

#To gracefully exit with an error
def error(disc="<3",line=1):
    try:
        line_on_error=formatted_code.split('\n')[line-1]
    except:
        line_on_error="---"
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
    if varname[0]==".":
        return False
    if is_num(varname[0]):
        return False
    allowed="abcdefghijklmnopqrstuvwxyz."
    allowed+=allowed.upper()
    allowed+="1234567890_"
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
        elif x=="[":
            if cache!="":
                tokens.append(cache)
            tokens.append("]")
            cache=""
            msg=""
            continue
        elif x=="{":
            if cache!="":
                tokens.append(cache)
            tokens.append("}")
            cache=""
            msg=""
            continue
        elif x == "=" and x==tokens[len(tokens)-1]:
            del tokens[len(tokens)-1]
            tokens.append("==")
            continue
        elif x in operators:
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
        elif x==")":
            if cache!="":
                tokens.append(cache)
            cache=""
            msg=""
            tokens.append(")")
            continue
        elif x=="]":
            if cache!="":
                tokens.append(cache)
            cache=""
            msg=""
            tokens.append("]")
            continue
        elif x=="}":
            if cache!="":
                tokens.append(cache)
            cache=""
            msg=""
            tokens.append("}")
            continue
        elif x!=" " and x!="'":
            cache+=x
        elif x==",":
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
        elif x==" ":
            if msg=="":
                if cache=="":
                    pass
                else:
                    if cache!=" ":
                        tokens.append(cache)
                        cache=""
                        msg=""
            elif msg=="str":
                cache+=x
        elif x=="'":
            if msg!="str":
                msg="str"
                cache+=x
                continue
            if msg=="str":
                msg=""
                tokens.append(cache+"'")
                cache=""
        elif (cache=="in" or cache=="or" or cache=="and" or cache=="not") and tokens[token_i+1]==" ":
            tokens.append(" "+cache+" ")
            cache=""
    if cache!="":
        tokens.append(cache)
    return tokens

#This function return the string without its quotes if it is not a number otherwise as an integer
def refactor_temp(data,res=False):
    data=str(data)
    print(data)
    if data[0] == "'" and data[-1]=="'":
        if res:
            return data
        return data[1:-1]
    try:
        return ltz_round(data)
    except:
        pass
    return data

#Break the whole script into tokens
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
        if x==" " and cache!="" and state!="str" and state!="expr" and msg!="first_quote" and state!="arcall" and state!="set":
            execd=True
            appender(cache)
        elif x==" " and cache=="" and state!="arcall" and state!="set":
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
        if x==";" and cache!="" and state!="expr" and state!="arcall" and state!="str" and state!="set":
            execd=True
            appender(cache)
            appender(x)
        elif x==";" and state!="expr" and state!="arcall" and msg=="" and state!="str" and state!="set":
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
        if x=="]" and state=="arcall":
            cache+=x
            msg=msg-1
            if msg==0:
                appender(cache)
            continue
        if x=="[":
            cache+=x
            execd=True
            state="arcall"
            if msg=="":
                msg=0
            msg+=1
        if x=="}" and state=="set":
            cache+=x
            msg=msg-1
            if msg==0:
                appender(cache)
            continue
        if x=="{":
            cache+=x
            execd=True
            state="set"
            if msg=="":
                msg=0
            msg+=1
        if state=="expr":
            execd=True
            cache+=x
        if x=="=" and state!="expr" and state!="arcall" and state!="set":
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
        error("Dangerous Input detected",line_i)
    new_expr_tokens=[]
    for x in expr_tokens:
        if x in symbol_table["vars"]:
            if type(symbol_table[x])==type("") and not partial:
                new_expr_tokens.append("'"+symbol_table[x]+"'")
            elif len(x.split("."))==2 and x.split(".")[0] in symbol_table["vars"] and x.split(".")[1] in symbol_table["vars"] and type(symbol_table[x.split(".")[0]])=={} and x.split(".")[1] in symbol_table[x.split(".")[1]]:
                new_expr_tokens(symbol_table[x.split(".")[0]][symbol_table[x.split(".")[1]]])
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
        new_expr+=str(str(x)+" ")
    i=-1
    for x in new_expr:
        i+=1
        if i==0:
            continue
        if new_expr[i]=="*" and (new_expr[i-1]=="*" or new_expr[i-1]=="'"):
            error("Dangerous Input detected",line_i)
    new_expr=""
    for x in new_expr_tokens:
        if x in dir(builtins):
            error("Dangerous Input detected",line_i)
        if x=="vars" and use_st==False:
            new_expr+=str("list(locals().keys())")
        elif x=="vars":
            new_expr+=str(list(symbol_table.keys()))
        else:
            new_expr+=str(str(x)+" ")
    return new_expr

#This evalutes the values of the broken down expressions
def expr_post_processor(prep_expr):
    try:
        val=eval(prep_expr,{'__builtins__':{}},{'__builtins__':{}})
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
    if type(val)==type(None):
        error(f"Expression {prep_expr} has no valid output")
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
    symbol_table=st
    funcs=func_mapper(tokenz,init=True)
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
    omit=None
    symbol_table["vars"]=list(symbol_table.keys())
    identifiers=["var","list","print","if","tx",";","int","str","float"]
    blacklist=["vars","tx","recursions","loopi","import","os","json","contract_tx","boot"]+dir(builtins)+["var","list","print","if","tx",";","int","str","float"]
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
                        if tokenz[i+y].split(":")[0] not in blacklist and is_valid_var_name(tokenz[i+y].split(":")[0]) and valid_type(tokenz[i+y].split(":")[1]):
                            init_vars.append(tokenz[i+y])
                        else:
                            error("Invalid variable initialization")
                    if compile:
                        add_compile("if 'boot' not in list(locals().keys()):")
                        indents+=1
                        init_compile_str_1=""
                        init_compile_str_2="="
                        for y in init_vars:
                            init_compile_str_1+=f"{y.split(':')[0]},"
                            if type_default(y.split(':')[1])!='':
                                init_compile_str_2+=f"{str(type_default(y.split(':')[1]))},"
                            else:
                                init_compile_str_2+=f"'',"
                        add_compile(init_compile_str_1+init_compile_str_2)
                        indents-=1
                        add_compile("boot=1")
                    for y in init_vars:
                        if y.split(':')[0] not in symbol_table["vars"]:
                            symbol_table[y.split(':')[0]]=type_default(y.split(':')[1])
                            symbol_table["vars"].append(y.split(':')[0])
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
                elif x=="#require" and args==1 and is_safe_path(tokenz[i+1],working_dir) and os.path.exists(working_dir+tokenz[i+1]+".dat") and os.path.exists(working_dir+tokenz[i+1]):
                    with open(working_dir+tokenz[i+1]) as fs:
                        imported_script=fs.read()
                    imported_vars=json.loads(imported_vars)["symbol_table"]
                    for x in imported_vars.keys():
                        symbol_table[x]=imported_vars[x]
                        symbol_table["vars"].append(x)
                    if compile:
                        add_compile("import json")
                        add_compile(f"working_dir='{working_dir}'")
                        add_compile(f"imported_vars=json.loads(open('{working_dir}'+'{tokenz[i+1]}').read())['symbol_table']")
                        add_compile(f"for x in imported_vars: locals()[x]=imported_vars[x]")
                    if gas:
                        with open(tokenz[i+1]+".dat") as fees_data:
                            fees+=int(fees_data.read())
                    ignore.append(i+1)
                    continue
                #Changing values of variables
                elif x == "var":
                    if (args==3) and tokenz[i+1].split(".")[0] not in blacklist and tokenz[i+1].split(".")[0] in symbol_table["vars"] and is_valid_var_name(tokenz[i+1].split(".")[0]) and "|" not in tokenz[i+3]:
                        if len(tokenz[i+1].split(","))==2:
                            if tokenz[i+1].split(".")[1] in symbol_table["vars"]:
                                pass
                            error("Invalid set type var declaration",line_i)
                        if tokenz[i+3] in symbol_table['vars'] and len(tokenz[i+3].split("."))==1:
                            if type(symbol_table[tokenz[i+1]])!=type(symbol_table[tokenz[i+3]]):
                                error(f"Cannot assign variable '{tokenz[i+1]}' of type {type(symbol_table[tokenz[i+1]])} a value of type {type(symbol_table[tokenz[i+3]])}")
                            if gas:
                                fees+=len(str(symbol_table[tokenz[i+3]]))
                            if compile:
                                add_compile(f"globals()['{tokenz[i+1]}']={tokenz[i+3]}")
                            symbol_table[tokenz[i+1]]=refactor_temp(symbol_table[tokenz[i+3]])
                        elif len(tokenz[i+1].split("."))==2 and tokenz[i+1].split(".")[0] in symbol_table and type(symbol_table[tokenz[i+1].split(".")[0]])==type({}):
                            if compile:
                                sq="'"
                                add_compile(f'globals()["{tokenz[i+1].split(".")[0]}[{sq}{symbol_table[tokenz[i+1].split(".")[1]]}{sq}]"]'+f'={tokenz[i+3]}')
                            if gas:
                                fees+=len(tokenz[i+3])
                            symbol_table[tokenz[i+1].split(".")[0]][symbol_table[tokenz[i+1].split(".")[1]]]=expr_post_processor(expr_pre_processor(tokenz[i+3]))
                        elif len(tokenz[i+3].split("."))==2 and tokenz[i+3].split(".")[0] in symbol_table and type(symbol_table[tokenz[i+3].split(".")[0]])==type({}) and tokenz[i+3].split(".")[1] in symbol_table:
                            if compile:
                                add_compile(f'globals()["{tokenz[i+1]}"]={tokenz[i+3].split(".")[0]}["{symbol_table[tokenz[i+3].split(".")[1]]}"]')
                            if gas:
                                fees+=len(tokenz[i+3].split(".")[1])
                            symbol_table[tokenz[i+1]]=symbol_table[tokenz[i+3].split(".")[0]][symbol_table[tokenz[i+3].split(".")[1]]]
                        elif tokenz[i+3]=="true" or tokenz[i+3]=='false':
                            if type(symbol_table[tokenz[i+1]])!=type(True):
                                error(f"Cannot assign variable '{tokenz[i+1]}' of type {type(symbol_table[tokenz[i+1]])} a value of type {type(True)}")
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
                                    add_compile(f"globals()['{tokenz[i+1]}']={(tokenz[i+3])}")
                            var_val=expr_post_processor(expr_pre_processor(tokenz[i+3]))
                            if type(var_val)!=type(symbol_table[tokenz[i+1]]):
                                error(f"Cannot assign variable '{tokenz[i+1]}' of type {type(symbol_table[tokenz[i+1]])} a value of type {type(var_val)}")
                            symbol_table[tokenz[i+1]]=expr_post_processor(expr_pre_processor(tokenz[i+3]))
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
                elif x=="print" and args==1:
                    ignore.append(i+1)
                    if debug:
                        if tokenz[i+1] not in identifiers:
                            if tokenz[i+1] in symbol_table.keys():
                                print(symbol_table[tokenz[i+1]])
                                continue
                            print(expr_post_processor(expr_pre_processor(tokenz[i+1])))
                            continue
                        else:
                            error(f"Invalid print statement on line {line_i}",line_i)
                    continue
                #Output TX from contract
                elif x=="tx":
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
                            amount=expr_post_processor(expr_pre_processor(tokenz[i+1]))
                            if compile:
                                add_compile(f"amount={tokenz[i+1]}")
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
                elif x=="if" and args==2:
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
                elif x=="function" and args==2:
                    if tokenz[i+2].replace(" ","")=="()":
                        #Empty functions aren't allowed
                        error("Empty Function Detected",line_i)
                    if (refactor_temp(tokenz[i+1]) not in symbol_table['vars'] or symbol_table['vars']=="") and refactor_temp(tokenz[i+1]) in list(funcs.keys()):
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
                            add_compile(f"globals()['{tokenz[i+1]}']={tokenz[i+1]}")
                        funcs[tokenz[i+1]]=tokeniser(tokenz[i+2][1:-1]+";")
                    continue
                #To delete / free a variable
                elif x=="del" and args==1 and tokenz[i+1] in symbol_table["vars"]:
                    if not compile:
                        del symbol_table[tokenz[i+1]]
                        symbol_table["vars"].remove(tokenz[i+1])
                    if compile:
                        add_compile(f"del locals()[{add_sq(tokenz[i+1])}]")
                    ignore.append(i+1)
                    continue
                #To delete / free a sub variable
                elif x=="del" and args==2 and tokenz[i+1] in symbol_table["vars"] and type(symbol_table[tokenz[i+1]])==type({}) and tokenz[i+2] in symbol_table[tokenz[i+1]]:
                    if not compile:
                        del symbol_table[tokenz[i+1]][tokenz[i+2]]
                    if compile:
                        add_compile(f"del locals()[{add_sq(tokenz[i+1])}][{add_sq(tokenz[i+2])}]")
                    ignore.append(i+1)
                    ignore.append(i+2)
                    continue
                #To return a value from a function
                elif x=="omit" and args==1:
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
                elif x=="loop" and args==1 and not inloop:
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
                elif x[0]=="." and (x.split(".")[1] in symbol_table["vars"] or x.split(".")[1] in list(funcs.keys())):
                    object_val=x.split(".")[1]
                    if object_val in list(funcs.keys()):
                        #If the called object is a function
                        if func_trace>2:
                            #If the func trace that is the number of total function instances executed in a series to get to this call is more than 2 then a error is produced.
                                error(f"Cannot execute functions inside of multiple running function instances on line {line_i}",line_i)
                        elif args==0:
                            if object_val in list(funcs.keys()):
                                if compile:
                                    add_compile(f"{object_val}()")
                                else:
                                    internal(funcs[object_val],func_trace=func_trace+1)
                                continue
                        elif args==1:
                            if tokenz[i+1] not in symbol_table["vars"]:
                                error("Variable Undefined",line_i)
                            ignore.append(i+1)
                            if compile:
                                add_compile(f'globals()["{tokenz[i+1].replace("$","")}"]={object_val}()')
                            else:
                                internal(funcs[object_val],func_trace=func_trace+1)
                            if type(omit)==type(None):
                                error(f"Function returned 'None' while a value type of {type(symbol_table[tokenz[i+1].replace('','')])} was expected")
                            if gas:
                                fees+=len(str(omit))
                            if type(symbol_table[tokenz[i+1].replace("$","")])!=type(omit):
                                error(f"Cannot assign variable '{symbol_table[tokenz[i+1].replace('$','')]}' of type {type(symbol_table[tokenz[i+1].replace('$','')])} a value of type {type(omit)}")
                            symbol_table[tokenz[i+1].replace("$","")]=omit
                            symbol_table["vars"].append(tokenz[i+1].replace("$",""))
                            omit=None
                            continue
                    elif object_val in symbol_table["vars"] and type(symbol_table[object_val])==type([]):
                        #If the object called is an array
                        if args==2:
                            if tokenz[i+1] == "+":
                                if tokenz[i+2] in symbol_table["vars"]:
                                    symbol_table[object_val].append(symbol_table[tokenz[i+2]])
                                else:
                                    symbol_table[object_val].append(expr_post_processor(expr_pre_processor(tokenz[i+2])))
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
                            elif tokenz[i+1] == "-":
                                if not compile:
                                    if tokenz[i+2] in symbol_table["vars"]:
                                        symbol_table[object_val].remove(symbol_table[tokenz[i+2]])
                                    else:
                                        symbol_table[object_val].remove(expr_post_processor(expr_pre_processor(tokenz[i+2])))
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
                        elif tokenz[i+1]=="$" and args==3:
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
                            if type(symbol_table[tokenz[i+3].replace('$','')])!=type(symbol_table[object_val][val]):
                                error(f"Cannot assign variable '{tokenz[i+3].replace('$','')}' of type {type(symbol_table[tokenz[i+3].replace('$','')])} a value of type {type(symbol_table[object_val][val])}")
                            symbol_table[tokenz[i+3].replace("$","")]=symbol_table[object_val][val]
                            if compile:
                                add_compile(f'{tokenz[i+3].replace("$","")}={object_val}[{tokenz[i+2]}]')
                            if gas:
                                fees+=len(str(tokenz[i+1]))
                            ignore.append(i+1)
                            ignore.append(i+2)
                            ignore.append(i+3)
                            continue
                        elif tokenz[i+1]=="len" and args==2 and tokenz[i+2].replace("$","") in symbol_table["vars"]:
                            if type(tokenz[i+2].replace("$",""))!=type(len(symbol_table[object_val])):
                                error(f"Cannot assign variable '{tokenz[i+2].replace('$','')}' of type {type(tokenz[i+2].replace('$',''))} a value of type {type(len(symbol_table[object_val]))}")
                            symbol_table[tokenz[i+2].replace("$","")]=len(symbol_table[object_val])
                            if compile:
                                add_compile(f'{tokenz[i+2].replace("$","")}=len({object_val})')
                            if gas:
                                fees+=len(str(len(symbol_table[object_val])))
                            ignore.append(i+1)
                            ignore.append(i+2)
                            ignore.append(i+3)
                            continue
                        elif tokenz[i+1]=="insert" and args==3:
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
                                symbol_table[int(tokenz[i+2])]=expr_post_processor(expr_pre_processor(tokenz[i+3][1:-1]))
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

                        elif tokenz[i+1]=="obj" and args==3:
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
                            if type(symbol_table[tokenz[i+3].replace("$","")])!=type(symbol_table[object_val].index(val)):
                                error(f"Cannot assign variable '{tokenz[i+3].replace('$','')}' of type {type(tokenz[i+3].replace('$',''))} a value of type {type(symbol_table[object_val].index(val))}")
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
                elif x=="//":
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
        return_out=compiled,list(funcs.keys())
        funcs={}
        symbol_table={}
        return return_out
    st_export={}
    for x in symbol_table:
        if type(symbol_table[x]) in [type(1),type(1.0),type(""),type([])]:
            st_export[x]=symbol_table[x]
    symbol_table={}
    return st_export,trans

def vtx2vt(script,new=True):
    if type(script)!=type([]):
        script=tokeniser(script)
    tokenz=script
    i=-1
    ignore=[]
    global final_tokens,include_vars,instance
    if new:
        final_tokens=[]
        include_vars={}
        instance=0
    instance+=1
    local_instance=instance
    for x in tokenz:
        i+=1
        #Since the vtx2vt parser also has the same dynamic seeker, this parser can also point to different tokens or ignore some tokens.
        if i not in ignore:
            args=0
            n=0
            if x!=";":
                while True:
                    n+=1
                    try:
                        if tokenz[i+n]==";":
                            n+=2
                            break
                    except:
                        error(f"Missing ';' for line break on line")
                    args+=1
            if x[0]=="(" and x[-1]==")" and tokenz[i-1] not in ["vars","tx","recursions","loopi","import","os","json","contract_tx","boot","omit"]+dir(builtins)+["var","list","print","if","tx",";","int","str","float"]:
                final_tokens.append("(")
                vtx2vt(x[1:-1],new=False)
                final_tokens.append(")")
            elif x=="include" and args==1:
                vtx2vt(open(tokenz[i+1].replace("'","")).read(),new=False)
                ignore.append(i+1)
                ignore.append(i+2)
            elif x=="var":
                if tokenz[i+1] not in include_vars:
                    if tokenz[i+3] not in include_vars:
                        if tokenz[i+3] not in ["true","false"]:
                            include_vars[tokenz[i+1]]=type2vartype(type(eval(tokenz[i+3])))
                        else:
                            include_vars[tokenz[i+1]]="bool"
                    else:
                        include_vars[tokenz[i+1]]=include_vars[tokenz[i+3]]
                final_tokens.append(x)
            else:
                final_tokens.append(x)
    translated_vt=""
    for x in final_tokens:
        translated_vt+=(x+" ")

    if local_instance==1:
        var_str="vars: "
        for x in include_vars:
            var_str+=(f"{x}:{include_vars[x]}"+" ")
        if var_str=="vars: ":
            var_str=""
        else:
            var_str+=";"
        translated_vt=var_str+"\n"+translated_vt
    return formatter(translated_vt)

#Running the script
def run(script,symbol_table={"txcurr":'LTZ',"txsender":'test','txamount':1,'txmsg':'test'},debug=True,gas=False,compile=False,working_dir="",runtime_func="main"):
    global formatted_code
    formatted_code=formatter(script)
    if '"' in script:
        error('Double quote character " is not allowed',0)
    parse_tokens=tokeniser(script)
    parser_output=parser(parse_tokens,symbol_table,debug,gas,compile,working_dir,runtime_func)
    return parser_output

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

def vtx_debug(script,exe=True):
    global formatted_code
    formatted_code=formatter(script)
    if exe:
        try:
            print("-"*10+"Compiling-VTX-VT"+"-"*10)
            compiled_vtx=vtx2vt(script)
            print(compiled_vtx)
            print("Success")
        except Exception as e:
            return f"Failed Compiling VTX --> VT : {str(e)}"
        try:
            print("-"*10+"Executing-VT"+"-"*11)
            compiled_vt=run(compiled_vtx,debug=False)
            print(compiled_vt)
            print("Success")
        except Exception as e:
            traceback.print_exc()
            return f"Failed Executing-VT : {str(e)}"
    else:
        return vtx2vt(script)

def func_mapper(tokenz,init=False):
    global funcs_mapped
    if init:
        funcs_mapped={}
    i=-1
    for x in tokenz:
        i+=1
        if x=="function":
            funcs_mapped[tokenz[i+1]]=tokenz[i+2][1:-1]
        elif x[0]=="(" and x[-1]==")":
            func_mapper(tokeniser(x[1:-1]))
    if init:
        return funcs_mapped

if __name__=="__main__":
    env={}
    while True:
        line=input(">> ")
        env=run(line,env)[0]
