import numpy

def generate(n=11):
    index = 0
    for i,l3 in enumerate(numpy.linspace(0,1,n)):
        for l2 in numpy.linspace(0,max(0,1-l3),n-i):
            l1 = max(0,1 - l2 - l3)
            yield index,l1,l2,l3
            index+=1
            
