import collections
import itertools
import multiprocessing

from functools import partial
from multiprocessing.dummy import Pool
from subprocess import call
import os
import sys
import optparse
import json

from classes.telegram_bot_msg import TelegramBotMsg

def get_options():
  opt_parser = optparse.OptionParser()
  opt_parser.add_option("--configfile", dest="configfile", 
                        help="Instance and algorithms parameters", metavar="FILE")
  opt_parser.add_option("--machine", dest="machine", 
                        help="Machine option in file", type="string")
  opt_parser.add_option("--basefolder", dest="basefolder", 
                        help="Base folder of scenarios", metavar="FILE")
  opt_parser.add_option("--probe", dest="probe", action="store_true",
                        default=False, help="Probe EV (run only no-preemption instances)") 
  opt_parser.add_option("--taskset", dest="taskset", action="store_true",
                        default=False, help="Must use taskset to specify cpu core")
  opt_parser.add_option("--telegram", dest="telegram", action="store_true",
                        default=False, help="Specify if should send a message through telegram")
  opt_parser.add_option("--tmpdir", dest="tmpdir", 
                        help="Temp dir where log files will be stored", metavar="FILE")                        
  (options, args) = opt_parser.parse_args()
  return options

# this is the main entry point of this script
if __name__ == "__main__":
  options = get_options()

  if options.telegram:
    telegram_token = os.environ['TELEGRAM_BOT_TOKEN']

    if telegram_token == None or len(telegram_token) <= 0:
      sys.exit("Error: --telegram is set but TELEGRAM_BOT_TOKEN is not set")

    telegram_to = os.environ['TELEGRAM_BOT_TO']

    if telegram_to == None or len(telegram_to) <= 0:
      sys.exit("Error: --telegram is set but TELEGRAM_BOT_TO is not set")

  if not options.configfile:
    sys.exit("Error: You must specify the Config File using the '--configfile' option")

  if not options.basefolder:
    sys.exit("Error: You must specify the Base Folder of scenarios using the '--basefolder' option")

  if not options.machine:
    sys.exit("Error: You must specify the Machine using '--machine' option")

  if options.tmpdir != None and not os.path.isdir(options.tmpdir):
    sys.exit("Error: If provided, '--tmpdir' option must be a valid folder")


  configfile = open(options.configfile,'r')
  config_values = json.loads(configfile.read(), object_pairs_hook=collections.OrderedDict)
  configfile.close()

  print(configfile)

  if options.machine not in config_values['machines']:
    sys.exit("Error: {} is not specifiend in {} file".format(options.machine,options.configfile))

  algorithms = config_values['algorithms']

  base_folder = options.basefolder
  locations = config_values['locations']
  route_options = config_values['prefix']
  number_of_instances = config_values['scenarios']
  seeds = config_values['machines'][options.machine]['seeds']
  #tasks = config_values['machines'][options.machine]['tasks']
  cores = config_values['machines'][options.machine]['cores']
  maxtasks = config_values['machines'][options.machine]['maxtasks']


  #if 'threadnum' in config_values['machines'][options.machine]:
  #  threadnum = config_values['machines'][options.machine]['threadnum']
  #else:
  #  threadnum = multiprocessing.cpu_count()

  commands = []

  for route_option in route_options:
    for location in locations:
      evs = locations[location]['evs']
      for i in number_of_instances:
        current_base_folder = '{}/{}/{}-{}'.format(base_folder,location,location,i)

        for ev in evs:
          for j in seeds:
            command = ' python3 new_proposal.py --scenario {} --nogui --evs {} --sm {} --prefix {} --tmpdir {} '.format(current_base_folder,ev,j,route_option,options.tmpdir)
            #print(command)

            for alg, args in algorithms.items():
              if options.probe and alg != 'no-preemption':
                continue

              print('config: {} {} {}'.format(alg,args,command))

              algcommand = '{} --alg {} '.format(command,alg)
              if len(args) == 0:
                commands.append(algcommand)
              else:
                partial_commands = []
                for parameter, values in args.items():
                  partial_parameters = []
                  for p in values:
                    partial_parameters.append(' --{} {} '.format(parameter,p))
                  partial_commands.append(partial_parameters)
                
                if len(partial_commands) == 1:
                  for element in itertools.product(partial_commands[0]):
                    final_args = ''
                    for w in element:
                      final_args = '{} {} '.format(final_args,w)
                    commands.append('{} {}'.format(algcommand,final_args))
                elif len(partial_commands) == 2:
                  for element in itertools.product(partial_commands[0],partial_commands[1]):
                    final_args = ''
                    for w in element:
                      final_args = '{} {} '.format(final_args,w)
                    commands.append('{} {}'.format(algcommand,final_args))
                elif len(partial_commands) == 3:
                  for element in itertools.product(partial_commands[0],partial_commands[1],partial_commands[2]):
                    final_args = ''
                    for w in element:
                      final_args = '{} {} '.format(final_args,w)
                    commands.append('{} {}'.format(algcommand,final_args))
                elif len(partial_commands) == 4:
                  for element in itertools.product(partial_commands[0],partial_commands[1],partial_commands[2],partial_commands[3]):
                    final_args = ''
                    for w in element:
                      final_args = '{} {} '.format(final_args,w)
                    commands.append('{} {}'.format(algcommand,final_args))
                elif len(partial_commands) == 5:
                  for element in itertools.product(partial_commands[0],partial_commands[1],partial_commands[2],partial_commands[3],partial_commands[4]):
                    final_args = ''
                    for w in element:
                      final_args = '{} {} '.format(final_args,w)
                    commands.append('{} {}'.format(algcommand,final_args))

  taskset_commands = []
  core = 0  
  for c in commands:
    print(c)
    if options.taskset:
      taskset_commands.append(' taskset -c {} {} '.format(cores[core],c))
    else:
      taskset_commands.append(c)
      
    core = (core + 1) % len(cores)
  
  #print('\n'.join(taskset_commands))

  print('all commands: {}'.format(taskset_commands))

  #sys.exit(0)  

  failed_commands = {}
  #pool = Pool(threadnum*tasks) # using the number of cores to run concurrent commands at same time
  pool = Pool(maxtasks)
  for i, returncode in enumerate(pool.imap(partial(call, shell=True), taskset_commands)):
    if returncode != 0:
      failed_commands[i] = returncode

      tmp = open('./errorcommands.txt','a+')
      tmp.write('{} command failed with statuscode={} ({})\n'.format(i,failed_commands[i],commands[i]))
      tmp.close()
    else:
      print("{} command has successfuly finished".format(i))

  for i in failed_commands:
    print('{} command failed with statuscode={} ({})'.format(i,failed_commands[i],commands[i]) )

  if options.telegram:
    telegram = TelegramBotMsg(telegram_token)
    print("message return: {}".format(telegram.sendMsg(telegram_to,'Job finalizado! {}'.format(options.configfile))))

