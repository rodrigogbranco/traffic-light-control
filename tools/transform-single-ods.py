from pyexcel_ods3 import get_data # noqa
from os import listdir, system
from os.path import isfile, join, exists
import os
import sys
import json

import optparse

def get_options():
  opt_parser = optparse.OptionParser()
  opt_parser.add_option("--folder", dest="folder", 
                        help="Folder of file", metavar="FILE")
  opt_parser.add_option("--odsfile", dest="odsfile", 
                        help="ODS File to process", metavar="FILE")                        
  (options, args) = opt_parser.parse_args()
  return options                        

# this is the main entry point of this script
if __name__ == "__main__":
  options = get_options()

  if not options.folder:
    sys.exit("Error: You must specify the Folder of file using the '--folder' option")

  if not options.odsfile:
    sys.exit("Error: You must specify the ODS File of scenarios using the '--odsfile' option")

  print('Processing '+options.odsfile+'...')

  partial_data = get_data(options.odsfile)

  sheet_summary = options.odsfile.split('/')[-1].split('.ods')[0]

  data = {
    'summary': {
      'instance': sheet_summary,
      'tls': partial_data[sheet_summary][1][1],
      'n_vehicles': partial_data[sheet_summary][1][2],
      'when_enter': partial_data[sheet_summary][1][3],
      'when_left': partial_data[sheet_summary][1][4],
      'n_when_enter': partial_data[sheet_summary][1][5],
      'n_when_left': partial_data[sheet_summary][1][6],
      'final_time': partial_data[sheet_summary][1][7],
      'n_teleported': partial_data[sheet_summary][1][8],
      'ev_was_teleported': partial_data[sheet_summary][1][9],
      'crossed_tls': partial_data[sheet_summary][1][10],
      'distance': partial_data[sheet_summary][1][11],
      'ev': partial_data[sheet_summary][4][0],
      'ttt-ev': partial_data[sheet_summary][4][1],
      'timeloss-ev': partial_data[sheet_summary][4][2],
      'timeloss-ev/ttt-ev': partial_data[sheet_summary][4][3],
      'ttt-other': partial_data[sheet_summary][5][1],
      'timeloss-other': partial_data[sheet_summary][5][2],
      'ttt-other-var': partial_data[sheet_summary][6][1],
      'timeloss-other-var': partial_data[sheet_summary][6][2],
      'ttt-other-std': partial_data[sheet_summary][7][1],
      'timeloss-other-std': partial_data[sheet_summary][7][2],
      'ttt-other-affected': partial_data[sheet_summary][8][1],
      'timeloss-other-affected': partial_data[sheet_summary][8][2],
      'ttt-other-affected-var': partial_data[sheet_summary][9][1],
      'timeloss-other-affected-var': partial_data[sheet_summary][9][2],
      'ttt-other-affected-std': partial_data[sheet_summary][10][1],
      'timeloss-other-affected-std': partial_data[sheet_summary][10][2],
      'ev-speed-avg': partial_data[sheet_summary][12][1],
      'other-speed-avg': partial_data[sheet_summary][14][1],
      'other-speed-var': partial_data[sheet_summary][15][1],
      'other-speed-std': partial_data[sheet_summary][16][1],
      'other-affected-speed-avg': partial_data[sheet_summary][18][1],
      'other-affected-speed-var': partial_data[sheet_summary][19][1],
      'other-affected-speed-std': partial_data[sheet_summary][20][1],               
    },
    'Car density': partial_data['Car density']
  }  

  file_tmp = open(options.folder+'/'+sheet_summary+'.json','w+')
  file_tmp.write(json.dumps(data))
  file_tmp.close()