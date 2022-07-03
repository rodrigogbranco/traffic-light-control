from os import system

if __name__ == "__main__":
  jsonfile = 'summary'
  locations = ['sp', 
    'ny'
    ]
  prefixes = [
              'staticdynamic',
              ]
  datafolder = 'latexfiles'
  #sp_evs = ['veh7058', 'veh5393', 'veh7377', 'veh5894', 'veh11651']
  #ny_evs = ['veh4216', 'veh4046', 'veh4028', 'veh2735', 'veh4856']

  sp_evs = ['veh11651']
  ny_evs = ['veh4856']

  commands_with_errors = []
  for location in locations:
    for prefix in prefixes:
      if location == 'sp':
        evs = sp_evs
      elif location == 'ny':
        evs = ny_evs

      for ev in evs:
        command = 'python3 tools/generate-latex-info.py --jsonfile {0}-{1}.json --prefix {1} --datafolder {2} --location {3} --ev {4}'\
                  .format(jsonfile,prefix,datafolder,location,ev)

        if(system(command) != 0):
            commands_with_errors.append(command)

  print('command with errors')
  print(commands_with_errors)            

