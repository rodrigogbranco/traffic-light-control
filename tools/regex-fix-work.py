import sys
from os import listdir, system
from os.path import isfile, join, exists
import optparse

def get_options():
  opt_parser = optparse.OptionParser()
  opt_parser.add_option("--basefolder", dest="basefolder", 
                        help="Base folder of scenarios", metavar="FILE")
  opt_parser.add_option("--prefix", type="string", dest="prefix")                        
  (options, args) = opt_parser.parse_args()
  return options

# this is the main entry point of this script
if __name__ == "__main__":
  options = get_options()

  if not options.basefolder:
    sys.exit("Error: You must specify the Base Folder of scenarios using the '--basefolder' option") 

  if not options.prefix:
    sys.exit("Error: You must specify the prefix using '--prefix' option")     

  base_folder = options.basefolder
  locations = ['sp','ny']
  number_of_instances = 5

  commands_with_errors = []

  for location in locations:
    for i in range(1,number_of_instances+1):
      current_base_folder = base_folder + '/' + location + '/' + location + '-' + str(i) + '/results/'+options.prefix

      if exists(current_base_folder):
        only_json_files = [f for f in listdir(current_base_folder) if isfile(join(current_base_folder, f)) and '.json' in f]

        for j in only_json_files:
          command = 'python3 regex-fix.py --filename '+current_base_folder+'/'+j

          print('processing '+current_base_folder+'/'+j)
          if(system(command) != 0):
            commands_with_errors.append(command)
      else:
        print('folder '+current_base_folder+' does not exist, skipping...')
      
  print('command with errors')
  print(commands_with_errors)    