import sys
import os
from os import listdir, system
from os.path import isfile, join, exists
import optparse
import multiprocessing
import collections
import json
from functools import reduce

from classes.summarize_worker import do_work

def merge_dicts(dict1, dict2):
    """ Recursively merges dict2 into dict1 """
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict2
    for k in dict2:
        if k in dict1:
            dict1[k] = merge_dicts(dict1[k], dict2[k])
        else:
            dict1[k] = dict2[k]
    return dict1

def get_options():
  opt_parser = optparse.OptionParser()
  opt_parser.add_option("--basefolder", dest="basefolder", 
                        help="Base folder of scenarios", metavar="FILE")
  opt_parser.add_option("--outputfile", dest="outputfile", 
                        help="Output File", metavar="FILE")
  opt_parser.add_option("--prefix", type="string", dest="prefix")
  opt_parser.add_option("--locations", type="string", dest="locations")
  opt_parser.add_option("--targetdir", type="string", dest="targetdir")
  (options, args) = opt_parser.parse_args()
  return options

# this is the main entry point of this script
if __name__ == "__main__":
  multiprocessing.set_start_method("spawn")

  options = get_options()

  if not options.basefolder:
    sys.exit("Error: You must specify the Base Folder of scenarios using the '--basefolder' option")

  if not options.outputfile:
    sys.exit("Error: You must specify the Output file using the '--outputfile' option")

  if not options.prefix:
    sys.exit("Error: You must specify the prefix using '--prefix' option")

  if not options.targetdir:
    sys.exit("Error: You must specify the target folder using '--targetdir' option")    

  if not os.path.exists(options.targetdir):
    os.makedirs(options.targetdir, exist_ok=True)         

  base_folder = options.basefolder
  #locations = ['od']
  #locations = ['sp', 'ny']
  number_of_instances = [1,1]

  commands_with_errors = []

  processed_file = options.outputfile.split('.')
  error_file = '{}/{}-error.txt'.format(options.targetdir,processed_file[0])
  processed_file = '{}/{}-processed.txt'.format(options.targetdir,processed_file[0])

  results = {}
  if os.path.isfile(options.outputfile):
    file_tmp = open(options.outputfile,'r')
    results = json.loads(file_tmp.read())
    file_tmp.close()

  if os.path.isfile(processed_file):
    processed_array = set(line.strip() for line in open(processed_file,'r'))
  else:
    processed_array = set()

  commands = []
  files_checked = []

  pool = multiprocessing.Pool(processes=multiprocessing.cpu_count()*3) # using the number of cores to run concurrent commands at same time

  for location in options.locations.split(','):
    for i in range(number_of_instances[0],number_of_instances[1]+1):
      current_base_folder = os.path.join(base_folder,location)
      current_base_folder = os.path.join(current_base_folder,'{}-{}'.format(location,i))
      current_base_folder = os.path.join(current_base_folder,'results')
      current_base_folder = os.path.join(current_base_folder,options.prefix)

      if exists(current_base_folder):
        only_ods_files = [f for f in listdir(current_base_folder) if isfile(join(current_base_folder, f)) and '.json' in f]

        for j in only_ods_files:
          checkfile = os.path.join(location,'{}-{}'.format(location,i))
          checkfile = os.path.join(checkfile,'results')
          checkfile = os.path.join(checkfile,options.prefix)
          checkfile = os.path.join(checkfile,j)

          if checkfile in processed_array:
            print('{} is present, skipping...'.format(checkfile))
          else:
            commands.append({
              'results': {},
              'method' : 'append',
              'basefolder': base_folder,
              'location': location,
              'instance': i,
              'jsonfile': j,
              'prefix': options.prefix,
              'errorfile': error_file
            })
            files_checked.append(checkfile)
      else:
        print('folder {} does not exist, skipping...'.format(current_base_folder))

  try:
    pool_outputs = pool.map(do_work, commands)
  except:
    print('Error!')
    raise
  pool.close()
  pool.join()

  final_dict = reduce(merge_dicts,pool_outputs)
  final_dict = merge_dicts(final_dict,results)

  new_dict = {}

  for a in final_dict:
    if a not in new_dict:
      new_dict[a] = {}

    for b in final_dict[a]:
      if b not in new_dict[a]:
        new_dict[a][b] = {}

      for c in final_dict[a][b]:
        if c not in new_dict[a][b]:
          new_dict[a][b][c] = {}

        for d in final_dict[a][b][c]:
          if d not in new_dict[a][b][c]:
            new_dict[a][b][c][d] = {}

          for e in final_dict[a][b][c][d]:
            if e not in new_dict[a][b][c][d]:
              new_dict[a][b][c][d][e] = []

            for f in final_dict[a][b][c][d][e]:
              new_dict[a][b][c][d][e].append(int(f))


  file_tmp = open('{}/{}'.format(options.targetdir,options.outputfile),'w+')
  file_tmp.write(json.dumps(new_dict))
  file_tmp.close()

  with open(processed_file,'w+') as file_tmp:
    file_tmp.write('\n'.join(files_checked))
