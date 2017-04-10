from jinja2 import Environment
import random
import string
import os

'''
generates a random string of uppercase characters and digits of the given length
see http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
'''
def genid(size) :
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))

class DCBEnvironment(Environment):
    def __init__(self,**kwargs):
        super(DCBEnvironment, self).__init__(**kwargs)
	
        self.globals['genid'] = genid
	self.globals['getenv'] = lambda (e, dflt): e in os.getenv(e, dflt)

