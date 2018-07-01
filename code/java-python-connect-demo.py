# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 16:12:45 2017

@author: bob

function:
    
    get the number from input file path of command window, and output the number + 1 
        to the out.txt of the current file 

example：

python java-python-connect-demo.py D:/Spyder/in.txt

"""


from sys import argv

in_path = argv[1]
out_path = './out.txt'

try:
    with open(in_path) as file:
        out_data = int(file.readline()) + 1
    with open(out_path, 'w') as out_file:
        print(out_data, file = out_file)
except IOError as err:
    print('File error:' + str(err))
    



