import optparse
import json
import sys
import numpy
import os
from distutils.util import strtobool
import scipy.stats as stats
import math
import collections

import copy

import numpy as np
import numpy as np, scipy.stats as st

from interval import interval

from statistics import mean

#from classes.base_latex_processor import BaseLatexProcessor
#from classes.improvement_latex_processor import ImprovementLatexProcessor
#from classes.timeloss_no_preemption_latex_processor import TimelossNoPreemptionLatexProcessor
#from classes.timeloss_over_ttt_no_preemption_latex_processor import TimelossOverTTTNoPreemptionLatexProcessor
#from classes.boxplot_latex_processor import BoxplotLatexProcessor
#from classes.errorbar_latex_processor import ErrorBarLatexProcessor
#from classes.bar_latex_processor import BarLatexProcessor
#from classes.bar2_latex_processor import Bar2LatexProcessor

def get_options():
  opt_parser = optparse.OptionParser()
  opt_parser.add_option("--jsonfile", dest="jsonfile", 
                        help="JSON File", metavar="FILE")
  opt_parser.add_option("--prefix", dest="prefix", 
                        help="Prefix to generate files", metavar="FILE")
  opt_parser.add_option("--datafolder", dest="datafolder", 
                        help="Folder where data will be generated", metavar="FILE")
  opt_parser.add_option("--sourcefolder", dest="sourcefolder", 
                        help="Folder where json files are", metavar="FILE")  
  opt_parser.add_option("--excludeoutliers", type="string", dest="excludeoutliers",
                        default="False", help="Indicates if outliers will be excluded")
  opt_parser.add_option("--locations", type="string", dest="locations",
                        help="Indicates locations (whitespace-serated like) so far")
  opt_parser.add_option("--evs", type="string", dest="evs",
                        help="Indicates EVs")

  (options, args) = opt_parser.parse_args()
  return options

def get_mean_interval(usedarray):
    if len(usedarray) == 0:
      return '0 0'

    if usedarray.count(usedarray[0]) == len(usedarray):
      interval =  0.0
      mean = usedarray[0]
    else:
      nparray = np.array(usedarray)
      interval = st.t.interval(0.95, len(nparray)-1, loc=np.mean(nparray), scale=st.sem(nparray))[0]
      mean = np.mean(nparray)

    return '{:.2f} {:.2f}'.format(mean,mean-interval)

# this is the main entry point of this script
if __name__ == "__main__":

  options = get_options()

  if not options.jsonfile:
    sys.exit("Error: You must specify the JSON file using the '--jsonfile' option")

  if not options.prefix:
    sys.exit("Error: You must specify the prefix using the '--prefix' option")  

  if not options.datafolder:
    sys.exit("Error: You must specify the data folder using the '--datafolder' option")

  if not options.sourcefolder:
    sys.exit("Error: You must specify the source folder using the '--sourcefolder' option")    

  if not options.locations:
    sys.exit("Error: You must specify the location using the '--location' option")
    
  if not options.evs:
    sys.exit("Error: You must specify the EVs using the '--evs' option")          

  try:
    excludeoutliers = strtobool(options.excludeoutliers)
  except:
    sys.exit("Error: --sync option invalid. It should be true or false")

  if not os.path.exists(options.sourcefolder):
    sys.exit("Error: source folder {} does not exist".format(options.sourcefolder))

  if not os.path.exists(options.datafolder):
    os.makedirs(options.datafolder, exist_ok=True)

  print(options)

  file_tmp = open('{}/{}'.format(options.datafolder,options.jsonfile),'r')
  files = json.loads(file_tmp.read())
  file_tmp.close()

  #data = copy.deepcopy(files)
  data = {}
  
  n_scenarios = {}

  locations = options.locations.split(',')

  for loc in locations:
    if loc in files:
      for i in files[loc]:
        for ev in options.evs.split(','):
          if options.evs in files[loc][i]:
            for alg in files[loc][i][options.evs]:
              for args in files[loc][i][options.evs][alg]:
                seeds = files[loc][i][options.evs][alg][args]

                if loc not in data:
                  data[loc] = {}
                if i not in data[loc]:
                  data[loc][i] = {}
                if ev not in data[loc][i]:
                  data[loc][i][ev] = {}
                if alg not in data[loc][i][ev]:
                  data[loc][i][ev][alg] = {}

                data[loc][i][ev][alg][args] = {}
                for seed in seeds:
                  data[loc][i][ev][alg][args][seed] = {}
                  args_not_empty = '_{}'.format(args) if len(args) > 0 else ''
                  filename = 'evs!{}_seed!{}_alg!{}{}.json'.format(options.evs,seed,alg,args_not_empty)
                  complete_path = '{0}/{1}/{1}-{2}/results/{3}/{4}'.format(options.sourcefolder,loc,i,options.prefix,filename)
                  print('reading {} for {}...'.format(complete_path,ev))
                  file_tmp = open(complete_path,'r')
                  content = json.loads(file_tmp.read())

                  #if alg == 'tpn':
                  #  for tl in content['tls']:
                  #    print(content['tls'][tl])

                  nv = len(content['vehs'])

                  if i not in n_scenarios:
                    n_scenarios[i] = []
                
                  n_scenarios[i].append(nv)

                  if ev not in content['teleported']:
                    if alg == 'no-preemption':
                      data[loc][i][ev][alg][args][seed]['duration'] = content['vehs'][ev][1]
                    else:
                      data[loc][i][ev][alg][args][seed]['affected'] = content['affected']

                    for tl in content['tls']:
                      if len(content['tls'][tl]) % 2 != 0:
                        print('erro {} {}'.format(complete_path,tl))
                        content['tls'][tl].append(content['tls'][tl][-1])


                  data[loc][i][ev][alg][args][seed]['teleported'] = content['teleported']
                  data[loc][i][ev][alg][args][seed]['runtime'] = content['param'][2] #runtime

                  data[loc][i][ev][alg][args][seed]['tls'] = content['tls']

                  data[loc][i][ev][alg][args][seed]['timeloss'] = {}

                  vehs_for_timeloss = [v for v in content['vehs'] if alg == 'no-preemption' or v in content['affected'] or v == ev]

                  for veh in vehs_for_timeloss:
                    data[loc][i][ev][alg][args][seed]['timeloss'][veh] = content['vehs'][veh][2]              

                  file_tmp.close()
          else:
            sys.exit("Error: {} not in {} ({}-{})".format(options.evs,options.jsonfile,loc,i))  
    else:
      sys.exit("Error: {} not in {}".format(loc,options.jsonfile))

  #sys.exit(0)

  #print(data)

  metrics = ['improvement','timeloss-no-preemption','timeloss-over-ttt-no-preemption','improvement-affected','runtime','tls-mean','tls-total','timeloss']

  results = {}
  results['scenarios'] = {}
  for i in n_scenarios:
    results['scenarios'][i] = math.trunc(mean(n_scenarios[i]))
    
  results['results'] = {}

  for m in metrics:
    results['results'][m] = {}

  #for m in metrics:
  #  results[m] = {}

  binomial_test = []  

  for loc in locations:
    for i in files[loc]:  
      for m in metrics:
        results['results'][m][i] = {}
        for ev in options.evs.split(','):
          results['results'][m][i][ev] = {}

          for alg in data[loc][i][ev]:
            for args in data[loc][i][ev][alg]:
              finalargs = '_{}'.format(args) if len(args) > 0 else ''
              alg_args = '{}{}'.format(alg,finalargs)

              for mx in metrics:
                addMx = False
                if alg == 'no-preemption' and mx in ['timeloss-no-preemption','timeloss-over-ttt-no-preemption']:
                  addMx = True
                elif alg != 'no-preemption' and mx in ['improvement', 'improvement-affected', 'tls-mean','tls-total', 'timeloss']:
                  addMx = True

                if mx == 'runtime':
                  addMx = True

                if addMx:
                  if i not in results['results'][mx]:
                    results['results'][mx][i] = {}
                  if ev not in results['results'][mx][i]:
                    results['results'][mx][i][ev] = {}
                  if alg_args not in results['results'][mx][i][ev]:
                    results['results'][mx][i][ev][alg_args] = {}

              impr = []
              timeloss_mean_nopreemption = []
              timeloss_over_ttt = []
              runtime = []
              impr_affected = []
              timeloss = []

              tls_mean = []
              tls_total = []

              test_binomial = 0
              size = len(data[loc][i][ev][alg][args])

              for seed in data[loc][i][ev][alg][args]:
                partial_data_no_preemption = data[loc][i][ev]['no-preemption'][''][seed]
                partial_data = data[loc][i][ev][alg][args][seed]

                ev_teleported_no_preemption = ev in partial_data_no_preemption['teleported']
                test_binomial += 0 if ev_teleported_no_preemption else 1
                ev_teleported = ev in partial_data['teleported']

                if not ev_teleported_no_preemption and not ev_teleported:
                  timeloss_alg = float(partial_data['timeloss'][ev])
                  timeloss_nopreemption = float(partial_data_no_preemption['timeloss'][ev])
                  ttt_nopreemption = float(partial_data_no_preemption['duration'])

                  if alg != 'no-preemption':
                    timeloss.append(timeloss_alg)
                    impr.append((1-(timeloss_alg/timeloss_nopreemption))*100)
                    aff_t_no = [ float(partial_data_no_preemption['timeloss'][t]) for t in partial_data_no_preemption['timeloss'] ]
                    aff_t = [ float(partial_data['timeloss'][t]) for t in partial_data['timeloss'] ]


                    impr_affected.append((np.mean(np.array(aff_t))/np.mean(np.array(aff_t_no)) - 1)*100)

                    times = []



                    for tl in partial_data['tls']:
                      times.append(sum([ partial_data['tls'][tl][t+1] - partial_data['tls'][tl][t] for t in range(0,len(partial_data['tls'][tl]),2) ]))

                    tls_mean.append(np.mean(np.array(times)))

                    total_intervals = interval()

                    for tl in partial_data['tls']:
                      for t in range(0,len(partial_data['tls'][tl]),2):
                        total_intervals |= interval([partial_data['tls'][tl][t],partial_data['tls'][tl][t+1]])

                    tls_total.append(sum([ iv[1] - iv[0] for iv in total_intervals ]))
                  else:
                    timeloss_mean_nopreemption.append(timeloss_nopreemption)
                    timeloss_over_ttt.append((timeloss_nopreemption/ttt_nopreemption)*100)

                  runtime.append(float(partial_data['runtime']))
                else:
                  print('loc={} i={} ev={} alg={} args={} seed={} teleported!'.format(loc,i,ev,alg,args,seed))

              if alg != 'no-preemption':
                results['results']['timeloss'][i][ev][alg_args] = get_mean_interval(timeloss)
                results['results']['improvement'][i][ev][alg_args] = get_mean_interval(impr)
                results['results']['improvement-affected'][i][ev][alg_args] = get_mean_interval(impr_affected) 
                results['results']['tls-mean'][i][ev][alg_args] = get_mean_interval(tls_mean)
                results['results']['tls-total'][i][ev][alg_args] = get_mean_interval(tls_total)
              else:
                results['results']['timeloss-no-preemption'][i][ev][alg_args] = get_mean_interval(timeloss_mean_nopreemption)
                results['results']['timeloss-over-ttt-no-preemption'][i][ev][alg_args] = get_mean_interval(timeloss_over_ttt)
              binomial_test.append('alg={} ev={} sce={} k={} of n={} => {:.2f}'.format(alg_args,ev,loc,test_binomial,size,stats.binom_test(test_binomial, n=size, p=0.9, alternative='less')))

              results['results']['runtime'][i][ev][alg_args] = get_mean_interval(runtime)

      file_tmp = open('{}/summary-{}-{}.json'.format(options.datafolder,options.prefix,loc),'w+')
      file_tmp.write(json.dumps(results))
      file_tmp.close()

  print('\n'.join(binomial_test))