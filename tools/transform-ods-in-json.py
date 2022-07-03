from os import listdir, system
from os.path import isfile, join, exists, isdir
import os
import sys

import optparse

def recursive_navigate(path, parent):
  commands_with_errors = []
  if isdir(path) and len(listdir(path)) > 0:
    #recursive navigate
    for child in listdir(path):
      commands_with_errors = commands_with_errors + recursive_navigate(join(path, child), path)
  elif isdir(path) and len(listdir(path)) == 0:
    #empty dir
    pass
  elif isfile(path) and '.ods' not in path:
    #not a ods file
    pass
  elif isfile(path) and '.ods' in path and parent != None:
    print('transforming '+path+' in '+parent)

    command = 'python3 transform-single-ods.py --folder '+parent+' --odsfile '+path

    if(system(command) != 0):
      commands_with_errors.append(command)
    else:
      print('deleting '+path+'...')
      os.remove(path)   
  else:
    #invalid path
    pass
  return commands_with_errors

def get_options():
  opt_parser = optparse.OptionParser()
  opt_parser.add_option("--basefolder", dest="basefolder", 
                        help="Base folder of scenarios", metavar="FILE")
  (options, args) = opt_parser.parse_args()
  return options                        

# this is the main entry point of this script
if __name__ == "__main__":
  options = get_options()

  if not options.basefolder:
    sys.exit("Error: You must specify the Base Folder of scenarios using the '--basefolder' option")

  path = options.basefolder
  commands_with_errors = []
  commands_with_errors = commands_with_errors + recursive_navigate(options.basefolder, None)

                   