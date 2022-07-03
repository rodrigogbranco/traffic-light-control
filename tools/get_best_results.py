import optparse
import json
import sys
import numpy as np


def get_options():
  opt_parser = optparse.OptionParser()
  opt_parser.add_option("--jsonfile", dest="jsonfile", 
                        help="JSON File", metavar="FILE")
  opt_parser.add_option("--prefix", dest="prefix", 
                        help="Prefix to generate filex", metavar="FILE")
  opt_parser.add_option("--location", type="string", dest="location",
                        help="Indicates location (SP or NY) so far")
  opt_parser.add_option("--ev", type="string", dest="ev",
                        help="Indicates EV")                                                 
  (options, args) = opt_parser.parse_args()
  return options                                                

if __name__ == "__main__":
  options = get_options()

  if not options.jsonfile:
    sys.exit("Error: You must specify the JSON file using the '--jsonfile' option")

  if not options.prefix:
    sys.exit("Error: You must specify the prefix using the '--prefix' option")  

  if not options.location:
    sys.exit("Error: You must specify the location using the '--location' option")
    
  if not options.ev:
    sys.exit("Error: You must specify the EV using the '--ev' option") 

  file_tmp = open(options.jsonfile,'r')
  results = json.loads(file_tmp.read())
  file_tmp.close()

  #print(results)

  algs = {}
  if options.location in results:
    #for i in results[options.location]:
    for alg in results[options.location]['5']:
      if alg != 'no-preemption':
        if alg not in algs:
          algs[alg] = []  
        for args in results[options.location]['5'][alg]:
          if options.ev in results[options.location]['5'][alg][args]:
            algs[alg].append(args)

  #print(algs)

  bests = {}

  for alg in algs:
    for args in algs[alg]:
    #if len(algs[alg]) > 0:
    #  args = algs[alg][0]

      if len(args) > 0:
        alg_args_index = '{}-{}'.format(alg,args)
      else:
        alg_args_index = alg

      if alg in results[options.location]['5'] and args in results[options.location]['5'][alg]:
        n_vec = 0
        metric_value = []
        if options.ev in results[options.location]['5'][alg][args] and options.ev:
          for seed in results[options.location]['5'][alg][args][options.ev]:
            if not results[options.location]['5'][alg][args][options.ev][seed]['ev_was_teleported'] and \
              not results[options.location]['5']['no-preemption'][''][options.ev][seed]['ev_was_teleported']:
              n_vec = results[options.location]['5'][alg][args][options.ev][seed]['n_vehicles']

              metric_alg = results[options.location]['5'][alg][args][options.ev][seed]['timeloss-ev']
              metric_nopreempt = results[options.location]['5']['no-preemption'][''][options.ev][seed]['timeloss-ev']

              metric_v = 1-metric_alg/metric_nopreempt            

              metric_value.append(metric_v*100)                  
          if len(metric_value) > 0:
            print('{} {} {}'.format(alg,alg_args_index,np.mean(metric_value)))       
