import sys
from engine import Engine

if __name__ == "__main__":
  if len(sys.argv)>1:
    is_server = True
  else:
    is_server = False
  engine = Engine(is_server=is_server)
  engine.run()
  engine.close()


"""
there different issues

get the data to the network system

I can pass then engine to the objects and they can pass certain communication types that can be converted
convert the data to bytes
convert the data from bytes


get the data to the things that need it



there are certain variable types that need to be communicated fundamentally

types

float
int
string
flags

route id? 


register yourself to get the data for a type and route id?


entity 10 is a type and route number
not float 20 that would be too ambiguous

what about traversing? I could have a table for the sizes of the information, I could encode the size too.

player 0 data
player 1 data
player 2 data
player 3 data

entities 0 2^16-1 data 

"""



# 1.) the port number recieved on the server side can be used to distinguish 