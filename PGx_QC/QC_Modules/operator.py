import operator
import sys
import re

a = sys.argv[1]
string = 'poor: <=0.75; intermediate: >0.75 & <=1.25; normal: >1.25 & <= 2.5; High inducibility: >2.5'

parsescore = {'<': operator.lt,
            '>': operator.gt,
            '>=': operator.ge,
            '<=': operator.le}


operator_pattern = re.compile(r'(<|>|>=|<=)')
num_pattern = re.compile(r'\d\.*\d*')
level = {level.split(":")[0] : level.split(":")[1] for level in string.strip().split('; ')}
phenotype = {value : key for key,value in level.items()}

a = float(a)
for val in level.values():
    compare = operator_pattern.findall(val)
    num = num_pattern.findall(val)
    #print val
    #print compare
    #print num
    result = [parsescore[opt](a, float(num[compare.index(opt)])) for opt in compare]
    for opt in compare:
        print a
        print opt
        print parsescore[opt]
        print num[compare.index(opt)]
        print parsescore[opt](a, float(num[compare.index(opt)]))
    print result
    if all(result):
       print phenotype[val]
       break
    #if all(result):
     #   print('%s %s %s'%(a, compare, num))
      #  break

#nums = [float(n) for n in num_pattern.findall(a)]
#compare = operator_pattern.findall(a)
print(level.items())
