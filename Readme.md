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
### Note Expressions like 1+1 should be enclosed inside of '()' brackets
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