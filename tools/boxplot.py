import optparse
import sys
import json
import matplotlib.pyplot as plt
import os
import numpy

def get_options():
  opt_parser = optparse.OptionParser()
  opt_parser.add_option("--jsonfile", type="string", dest="jsonfile", metavar="FILE", help="Json with values")
  opt_parser.add_option("--prefix", type="string", dest="prefix", help="Prefix")
  opt_parser.add_option("--location", type="string", dest="location", help="Location")
  opt_parser.add_option("--ev", type="string", dest="ev", help="Emergency Vehicle")
  opt_parser.add_option("--alg", type="string", dest="alg", help="Desired Algorithm")
  opt_parser.add_option("--args", type="string", dest="args", help="Used arguments")
  opt_parser.add_option("--folder", type="string", dest="folder", help="Folder where images will be stored")
  (options, args) = opt_parser.parse_args()
  return options

# this is the main entry point of this script
if __name__ == "__main__":
  options = get_options()

  print(options)

  if not options.jsonfile:
    sys.exit("Error: You must specify the Json file using the '--jsonfile' option")

  if not options.prefix:
    sys.exit("Error: You must specify the prefix using the '--prefix' option")       

  if not options.location:
    sys.exit("Error: You must specify the Location using the '--location' option")  

  if not options.ev:
    sys.exit("Error: You must specify the EV using the '--options.ev' option")

  if not options.alg:
    sys.exit("Error: You must specify the desired algorithm using the '--alg' option")

  if not options.folder:
    sys.exit("Error: You must specify the folder where images will be store using the '--folder' option")

  if not os.path.isdir(options.folder):
    sys.exit("Error: {} directory does not exist".format(options.folder))

  if not options.args:
    options.args = ''

  options.args = options.args.replace("'","")

  file_tmp = open(options.jsonfile,'r')
  results = json.loads(file_tmp.read())
  file_tmp.close()
  
  metric = 'timeloss-ev'

#self.results[self.location][i][self.alg][args][self.ev][seed][self.metric]

  #smartcity-centered-sf!20.0 df!10.0 tf!2.0 sync!True
  #djahel-wc!start el!high
  #rfid-dd!100.0 nc!5
  #petri

  algs = {
    'petri' : {
      'args' : ''
    },
    'djahel' : {
      'args' : 'wc!start_el!high'
    },
    'rfid' : {
      'args' : 'dd!100.0_nc!5'
    },
    'smartcity-centered' : {
      'args' : 'sf!20.0_df!10.0_tf!2.0_sync!True'
    }
  }

  vehs = ['veh7058','veh5393','veh7377','veh5894','veh11651']

  scenarios = ['1','2','3','4','5']
  if options.location in results:
    for veh in vehs:
      for alg in algs:
        args = algs[alg]['args']

        data_to_plot = []
        xticks = []
        xticks.append(0)

        for i in scenarios:
          data_from_scenario = []
          xtick = None
          res_loc = results[options.location]
          if i in results[options.location]:
            res_loc_i = results[options.location][i]
            if alg in res_loc_i:
              res_loc_i_alg = res_loc_i[alg]
              if args in res_loc_i_alg:
                res_loc_i_alg_args = res_loc_i_alg[args]
                if veh in res_loc_i_alg_args:
                  res_loc_i_alg_args_veh = res_loc_i_alg_args[veh]
                  for seed in res_loc_i_alg_args_veh:
                    if 'no-preemption' in res_loc_i and '' in res_loc_i['no-preemption'] and \
                      veh in res_loc_i['no-preemption'][''] and seed in res_loc_i['no-preemption'][''][veh] and \
                        metric in res_loc_i['no-preemption'][''][veh][seed] and not res_loc_i_alg_args_veh[seed]['ev_was_teleported'] and \
                        not res_loc_i['no-preemption'][''][veh][seed]['ev_was_teleported']:
                      result_after = res_loc_i_alg_args_veh[seed][metric]
                      result_before = res_loc_i['no-preemption'][''][veh][seed][metric]
                      result = (1-(result_after/result_before))*100
                      print(i+' seed:'+str(seed)+' rb:'+str(result_before)+' ra:'+str(result_after)+' r:'+str(result))
                      data_from_scenario.append(result)
                      xtick = res_loc_i_alg_args_veh[seed]['n_vehicles']
          data_to_plot.append(data_from_scenario)
          xticks.append(xtick)


        #print(data_to_plot)

        plt.clf()
        plt.boxplot(data_to_plot, notch=True, bootstrap=10000, meanline=True, showmeans=True)
        plt.title('Boxplot - {}_{}-{}'.format(veh,alg,args))
        plt.xlabel('Nº of vehicles')
        plt.ylabel('(1-(timeloss-ev-before/timeloss-ev-before)*)100')
        plt.ylim(top=100,bottom=-100)
        plt.xticks(numpy.arange(len(xticks)+1), xticks)
        plt.savefig('{}/{}_{}-{}.png'.format(options.folder,veh,alg,args), dpi=300)
        #plt.show()
    
  print('Done!')
  sys.exit(0)