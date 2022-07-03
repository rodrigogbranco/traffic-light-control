import os.path
import sys
from os import listdir
from os.path import isfile, join
import json
import numpy
import optparse
import sys
from statistics import mean
import matplotlib.pyplot as plt

def do_work(command): 
  results = command['results']
  method = command['method']
  basefolder = command['basefolder']
  location = command['location']
  instance = command['instance']
  jsonfile = command['jsonfile']
  prefix = command['prefix']

  results = dict({})

  if method == 'append' or method == 'override':
    if method == 'override' or location not in results:
      results[location] = {}

    i = instance

    current_base_folder = os.path.join(basefolder,location)
    current_base_folder = os.path.join(current_base_folder,'{}-{}'.format(location,i))
    current_base_folder = os.path.join(current_base_folder,'results')
    current_base_folder = os.path.join(current_base_folder,prefix)

    if method == 'override' or i not in results[location]:
      results[location][i] = {}

    if os.path.exists(current_base_folder):
      f = jsonfile
      name_parts = name_parts = f.split('.json')[0].split('/')[-1].split('_')
    

      alg_name = name_parts[2].split('!')[1]
      ev = name_parts[0].split('!')[1]
      seed = name_parts[1].split('!')[1]

      if method == 'override' or ev not in results[location][i]:
        results[location][i][ev] = {}

      if method == 'override' or alg_name not in results[location][i][ev]:
        results[location][i][ev][alg_name] = {}
      
      args_name = '_'.join(name_parts[3:len(name_parts)])

      if method == 'override' or args_name not in results[location][i][ev][alg_name]:
        results[location][i][ev][alg_name][args_name] = {}

      was_empty = False
      if seed not in results[location][i][ev][alg_name][args_name]:
        results[location][i][ev][alg_name][args_name][seed] = {}
        was_empty = True

      if method == 'override' or (method == 'append' and was_empty):
        print('processing {}'.format(os.path.join(current_base_folder,f)))
        return results
      else:
        print('{} from {}-{} was ignored!'.format(f,location,i))
  else:
    print('{} not exists'.format(current_base_folder))