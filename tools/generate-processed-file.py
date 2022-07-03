import json
import optparse
import sys

def get_options():
  opt_parser = optparse.OptionParser()
  opt_parser.add_option("--jsonfile", type="string", dest="jsonfile")
  opt_parser.add_option("--prefix", type="string", dest="prefix")
  (options, args) = opt_parser.parse_args()
  return options

# this is the main entry point of this script
if __name__ == "__main__":
  options = get_options()

  if not options.jsonfile:
    sys.exit("Error: You must specify the JSON file using the '--jsonfile' option")

  if not options.prefix:
    sys.exit("Error: You must specify the prefix using the '--prefix' option")  

  processed_file = options.jsonfile.split('.')
  processed_file = processed_file[0]+'-processed'+'.txt'
  print(processed_file)

  with open(options.jsonfile,'r') as file_tmp:
    results = json.loads(file_tmp.read())

  processed_array = []

  for location in results:
    for i in results[location]:
      for alg in results[location][i]:
        for args in results[location][i][alg]:
          for ev in results[location][i][alg][args]:
            for seed in results[location][i][alg][args][ev]:
              newarg = ''
              if alg == 'rfid':
                arg = args.split('nc')
                argdd = arg[0].split('!')[1]
                argnc = arg[1].split('!')[1]
                newarg = 'dd!'+argdd+'_nc!'+argnc
              elif alg == 'smartcity-centered':
                arg = args.split('sync')
                argsync = arg[1].split('!')[1]
                arg = arg[0].split('tf')
                argtf = arg[1].split('!')[1]
                arg = arg[0].split('df')
                argdf = arg[1].split('!')[1]
                arg = arg[0].split('sf')
                argsf = arg[1].split('!')[1]
                newarg = 'sf!'+argsf+'_df!'+argdf+'_tf!'+argtf+'_sync!'+argsync

              file_name = 'alg!'+alg+'_ev!'+ev+'_seed!'+seed
              if alg != 'no-preemption':
                file_name = file_name+'_'+newarg
              file_name = file_name +'.json'

              processed_array.append(location + '/' + location + '-' + str(i) + '/results/'+options.prefix+'/'+file_name)

  #print(processed_array)

  with open(processed_file,'w+') as file_tmp:
    file_tmp.write('\n'.join(processed_array))
  
  #results[location][i][alg_name][args_name][ev][seed]  

  #print(results)
