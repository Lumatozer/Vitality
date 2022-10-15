# Vitality
Vitality is a python-based interpreted language used primarily for smart contracts on the LTZ-Chain.\
The engine which interprets vitality is called Vengine (Vitality Engine).
## Example
```python
import vengine
script="print 'Hello world.';"
vengine.run(script)
```
## Formatter
```
import vengine
script="print 'Hello world.';"
print(vengine.formatter(script))
```
## Basics
To create a variable and assign a value to it
```python
vars: {variable_name};
var {variable_name} = {variable_value};
Example
var a = 10;
```
To change a variable's value  you also need to use the above syntax.
## Pre Assigned Variables
When a smart contract is invoked, 4 variables are injected into the code.
```python
1. txsender (Address of Invoker)
2. txamount (Amount sent to contract)
3. txmsg (Data provided along with transaction)
4. txcurr (Currency of transaction)
```
### Note Expressions like 1+1 should be enclosed within '()' brackets
\
To print a variables value
```python
print {var_name};
```
To print a literal
```python
print 0;
OR
print 'hi';
```
In Vitality you can store string literals without quotes if there are no spaces.\
For example if i want to store the literal 'ltz' in a variable.
```python
var a = ltz;
```
But this cannot be done is the string contains any white spaces ro if you want to compile the code and upload it as a smart contract.

There are two methods to create a list/array
```python
var a = ();
```
To append something to an array
```python
append {list_name} {data_to_append};
```
To remove something from an array
```python
remove {list_name} {data_to_remove};
```
If statements
```python
if (condition or variable) (
    #code here
);
```
Examples
```python
vars: a;
var a = (1==1);
if (a) (print 1;);
```
```python
vars: a;
var a = (1==1);
if (a) (
print 1;
);
```
```python
if ((1==1)) (
print 1;
);
```
To perform a transaction (Only in Smart Contracts)
```python
tx {amount} {receiver} {currency};
```
To change a variable to float type
```python
float {var_name};
```
To change a variable to int type
```python
int {var_name};
```
To change a variable to str type
```python
str {var_name};
```
To check if a variable name already exists
```python
if ('var_name_in_quotes' in vars) (
    print true;
);
```
Since 'vars' is an environment variable, the script cannot modify its value directly.

To create a function
```python
function {function_name} ({function_code});
```
Example
```python
function main (
    print LTZ;
);
```
To execute Functions;
```python
exec {func_name};
```
To add a loop:
```
recursions: {number_of_loops};
loop ({code_here});
```
To import a compiled vitality file:
```python
#note : make sure you keep the compiled file in a subfolder and mention it in the run function | example: vengine.run(script,working_dir="{dir_name}/")
require {script_name};
```
You can return data from inside of functions also using the "omit" token
```python
function main (
    omit LTZ;
);
```
The syntax for executing such function which return a value is
```python
exec {func_name} {var_name};
```
This stores the value omitted by the function in the variable provided.
## Smart Contract Examples
### Funding Page
```python
vars: funding_page fund_receiver percent funding_page_money sending_amount funding_page_money booted ltz_bal ltzs_bal dissolve to_pay;
var funding_page = '404cdd7bc109c432f8cc2443b45bcfe95980f5107215c645236e577929ac3e52';
var fund_receiver = '1dd8754d7f4192e973e0774edd395251621322f386fc02fd6b267bf4ba982cc9';
var percent = 10;
if (funding_page_money == None) (var funding_page_money= 0;);
if (txcurr=='LTZ' and txsender != funding_page) (
    var sending_amount = ((txamount/100)*(100-percent));
    tx sending_amount fund_receiver 'LTZ';
    var funding_page_money = (funding_page_money+(txamount-sending_amount));
);
if (txcurr=='LTZ' and txsender==funding_page) (
    tx funding_page_money fund_receiver 'LTZ';
);
```
### LTZ && LTZ-S Exchange
```python
vars: booted ltz_bal ltzs_bal dissolve to_pay;
if (booted == None) (
var booted=false;
);

if (booted) (
if (ltz_bal == None) (var ltz_bal=1;);
if (ltzs_bal == None) (var ltzs_bal=1;);
if (dissolve == None) (var dissolve=false;);
if (txsender=='0x0' and txmsg=='dissolve') (var dissolve=true;);
if (dissolve!=true) (
if (txcurr=='LTZ' and txmsg!='reserve') (
    var to_pay= (txamount*(ltz_bal/ltzs_bal));
    tx to_pay txsender 'LTZS';
    var ltz_bal=(ltz_bal+txamount);
    var ltzs_bal=(ltzs_bal-to_pay);
);
if (txcurr=='LTZS' and txmsg!='reserve') (
    var to_pay= (txamount*(ltzs_bal/ltz_bal));
    tx to_pay txsender 'LTZ';
    var ltzs_bal=(ltzs_bal+txamount);
    var ltz_bal=(ltz_bal-to_pay);
);
);
if (txcurr=='LTZ' and txmsg=='reserve') (
    var ltz_bal=(ltz_bal+txamount);
);
if (txcurr=='LTZS' and txmsg=='reserve') (
    var ltzs_bal=(ltzs_bal+txamount);
);
);

if (booted==false) (
    var ltz_bal=0;
    var ltzs_bal=0;
    var booted=true;
);
```
### Persistent script example 2
```python
vars: booted;
if (booted == None) (
var booted=false;
);

if (booted) (

);

if (booted==false) (
    var booted=true;
);
```