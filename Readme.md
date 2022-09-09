# Vitality
Vitality is a python-based interpreted language used primarily for smart contracts on the LTZ-Chain.\
The engine which interprets vitality is called Vengine (Vitality Engine).
## Example
```python
import vengine
script="print 'Hello world.'"
vengine.run(script)
```
## Basics
To create a variable and assign a value to it
```python
var {variable_name} = {variable_value};
Example
var a = 10;
```
To change a variable's value  you also need to use the above syntax
\
## Pre Assigned Variables
When a smart contract is invoked, 4 variables are injected into the code.\
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
But this cannot be done is the string contains any white spaces.

There are two methods to create a list/array
```python
var a = ();
OR
list a;
```
To append something to an array
```python
list append {list_name} {data_to_append};
```
To remove something from an array
```python
list remove {list_name} {data_to_remove};
```
If statements
```python
if ({condition/variable}) ({code_to_execute_if_satisfied})
```
Examples
```python
var a = (1==1);
if (a) (print 1;);
```
```python
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
if ('var_name' in vars) (
    print true;
);
Since vars is an environment variable you cannot modify its value
```
## Smart Contract Examples
### Funding Page
```python
var txamount=10;
var txsender='0d1eb95fa56ceb3d72c06dc1f04eb19495616afbcd3ec248b203e95f95196ba1';
var txcurr='LTZ';
var funding_page = '404cdd7bc109c432f8cc2443b45bcfe95980f5107215c645236e577929ac3e52';
var fund_receiver = '1dd8754d7f4192e973e0774edd395251621322f386fc02fd6b267bf4ba982cc9';
var percent = 10;
if ('funding_page_money' not in vars) (
var funding_page_money = 0;
);
if (txcurr=='LTZ' and txsender != funding_page) (
    var sending_amount = ((txamount/100)*(100-percent));
    tx sending_amount fund_receiver 'LTZ';
    var funding_page_money = (funding_page_money+(txamount-sending_amount));
);
if (txcurr=='LTZ' and txsender==funding_page) (
    tx funding_page_money fund_receiver 'LTZ';
);
del txsender;
del txamount;
del txcurr;
```