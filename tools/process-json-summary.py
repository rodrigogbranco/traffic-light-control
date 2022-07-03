import optparse
import json
import sys
import os

import numpy as np
import pandas as pd
import math

#from shutil import copyfile

def get_options():
  opt_parser = optparse.OptionParser()
  opt_parser.add_option("--jsonfile", dest="jsonfile", 
                        help="JSON File", metavar="FILE")
  opt_parser.add_option("--datafolder", dest="datafolder", 
                        help="Folder where data will be generated", metavar="FILE") 
  opt_parser.add_option("--locations", dest="locations", 
                        help="Location of scenarios", metavar="FILE")
  opt_parser.add_option("--evs", dest="evs", 
                        help="EVs", type="string")                         
  (options, args) = opt_parser.parse_args()
  return options                                                 

# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    if not options.locations:
        sys.exit("Error: You must specify the location using the '--location' option")

    if not options.jsonfile:
        sys.exit("Error: You must specify the JSON file using the '--jsonfile' option")

    if not options.datafolder:
        sys.exit("Error: You must specify the data folder using the '--datafolder' option")

    if not options.evs:
        sys.exit("Error: You must specify the EVs using the '--evs' option")        

    always = ['tpn','allgreen']

    labels = {
        'fuzzy_el!medium' : 'Fuzzy-M',
        'fuzzy_el!high' : 'Fuzzy-H',
        'fuzzy_el!low' : 'Fuzzy-L',
        'kapusta' : 'Kapusta',
        'tpn_prt!0.50_clear!False_always!True' : 'TPN-0.50-Always',
        'tpn_prt!0.50_clear!False_always!False' : 'TPN-0.50',
        'tpn_prt!0.50_clear!True_always!False' : 'TPN-0.50-Clear',
        'tpn_prt!0.50_clear!True_always!True' : 'TPN-0.50-Clear-Always',
        'rfid_dd!100.0_nc!5' : 'RFID-100-5',
        'rfid_dd!25.0_nc!2' : 'RFID-25-2',
        'rfid_dd!100.0_nc!2' : 'RFID-100-2',
        'rfid_dd!25.0_nc!5' : 'RFID-25-5',
        'allgreen' : 'AllGreen',
        'no-preemption' : 'NoPreemption'
    }

    #nvec = { 'sp' : ['7016','12842','17500','22154','25882'],
    #         'ny' : ['4265','7788','10798','13620','16454']}

    #nvec = { 'sp' : ['8344','11123','14829','19770','26358'],
    #         'spbi' : ['8355','11138','14847','19794','26389'],
    #         'oldsp' : ['8192','10921','14560','19412','25882'],
    #        'oldny' : ['5210','6944','9257','12342','16454']}    

    nvec = { 'od': ['27627', '36834', '49111', '65480', '87305']}

    factor = {'fuzzy' : 2.5,
              'kapusta' : 1.75,
              'rfid' : 2.75,
              'no-preemption' : 2}

    metrics = {'improvement' : 'Time-Loss Improvement (%)',
               'timeloss-no-preemption' : 'Time Loss (s)',
               'timeloss-over-ttt-no-preemption' : 'Time Loss / Actual Travel Time (%)',
               'improvement-affected' : 'Time-Loss gain (%)',
               'runtime' : 'Runtime (s)',
               'tls-mean' : 'Mean Active Preemption Time (s)',
               'tls-total' : 'Total Active Preemption Time (s)',
               'timeloss' : 'Time Loss (s)'}

    step = 3
    
    for ev in options.evs.split(','):
        for loc in options.locations.split(','):
            jsonpath = '{}/{}-{}.json'.format(options.datafolder,options.jsonfile,loc)       

            if not os.path.exists(jsonpath):
                sys.exit("Error: File {} does not exist".format(jsonpath))

            file_tmp = open(jsonpath,'r')
            results = json.loads(file_tmp.read())
            file_tmp.close()             

            for m in metrics:
                if m in ['improvement','improvement-affected','runtime','tls-mean','tls-total', 'timeloss']:
                    metric_dir = '{}/{}'.format(options.datafolder,m)
                    if not os.path.exists(metric_dir):
                        os.makedirs(metric_dir, exist_ok=True)            


                    file_metrics = '{}/{}-{}-{}.json'.format(options.datafolder,loc,m,ev)
                    file_tmp = open(file_metrics,'w')

                    unique_algs = {}

                    for i in results['results'][m]:
                        file_tmp.write('{}\n'.format(results['scenarios'][i]))

                        for alg in results['results'][m][i][ev]:
                            algname = alg.split('_')[0]

                            if algname not in unique_algs:
                                unique_algs[algname] = {}
                            if labels[alg] not in unique_algs[algname]:
                                unique_algs[algname][labels[alg]] = {}

                            unique_algs[algname][labels[alg]][(int(i)-1)*step] = results['results'][m][i][ev][alg]

                            file_tmp.write('\t{} {}\n'.format(alg,results['results'][m][i][ev][alg]))

                    file_tmp.close()                    

                    #print(unique_algs)

                    for algname in (a for a in unique_algs if a not in always):
                        metric_dir_alg = '{}/{}'.format(metric_dir,algname)
                        if not os.path.exists(metric_dir_alg):
                            os.makedirs(metric_dir_alg, exist_ok=True)

                        labels_file = []    

                        max_y = float('-inf')

                        for alglabel in unique_algs[algname]:
                            labels_file.append(alglabel)

                            alg_metrics = '{}/{}-{}-{}.dat'.format(metric_dir_alg,loc,alglabel,ev)
                            file_tmp = open(alg_metrics,'w')
                            for index in unique_algs[algname][alglabel]:
                                file_tmp.write('{} {}\n'.format(index,unique_algs[algname][alglabel][index]))
                                max_y = max(max_y,float(unique_algs[algname][alglabel][index].split(' ')[0]))

                            file_tmp.close()

                        for a in (a for a in unique_algs if a in always):
                            for alglabel in unique_algs[a]:
                                labels_file.append(alglabel)

                                alg_metrics = '{}/{}-{}-{}.dat'.format(metric_dir_alg,loc,alglabel,ev)
                                file_tmp = open(alg_metrics,'w')
                                for index in unique_algs[a][alglabel]:
                                    file_tmp.write('{} {}\n'.format(index,unique_algs[a][alglabel][index]))
                                    max_y = max(max_y,float(unique_algs[a][alglabel][index].split(' ')[0]))                            

                                file_tmp.close()

                        file_tmp = open('{}/{}-labels-{}.dat'.format(metric_dir_alg,loc,ev),'w')
                        file_tmp.write('\n'.join(labels_file))
                        file_tmp.close()

                        file_tmp = open('{}/{}-nvec-{}.dat'.format(metric_dir_alg,loc,ev),'w')
                        file_tmp.write('\n'.join(nvec[loc]))
                        file_tmp.close() 

                        file_tmp = open('{}/{}-indexes-{}.dat'.format(metric_dir_alg,loc,ev),'w')
                        file_tmp.write('\n'.join([ str((j-1)*step) for j in range(1,6)]))
                        file_tmp.close()

                        file_tmp = open('{}/{}-args-{}.dat'.format(metric_dir_alg,loc,ev),'w')
                        file_tmp.write('{}\n{}\n{}\n{}\n'.format(algname,metrics[m],int(math.ceil(max_y)*factor[algname]),m))
                        file_tmp.close() 

                        #copyfile('./plots/plot-{}.sh'.format(algname), '{}/plot-{}.sh'.format(metric_dir_alg,algname))                                
                #elif m in ['duration-no-preemption','timeloss-over-ttt-no-preemption']:
                #    metric_dir = '{}/{}'.format(options.datafolder,m)
                #    if not os.path.exists(metric_dir):
                #        os.makedirs(metric_dir, exist_ok=True)

                #    pass
            metric_dir = '{}/{}'.format(options.datafolder,'ttt')
            if not os.path.exists(metric_dir):
                os.makedirs(metric_dir, exist_ok=True)

            file_tmp = open('{}/{}-nvec.dat'.format(metric_dir,loc),'w')
            file_tmp.write('\n'.join(nvec[loc]))
            file_tmp.close()

            file_tmp = open('{}/file-{}-{}.dat'.format(metric_dir,loc,ev),'w')

            alg = 'no-preemption'
            for i in results['results'][m]:
                m1 = results['results']['timeloss-over-ttt-no-preemption'][i][ev][alg]
                m2 = results['results']['timeloss-no-preemption'][i][ev][alg]
                file_tmp.write('{} {} {}\n'.format(nvec[loc][int(i)-1],m1,m2))
            

            file_tmp.close()

    #copyfile('./plots/plot-ttt.sh', '{}/plot-ttt.sh'.format(metric_dir))                   

