import re
import optparse
import sys

def get_options():
  opt_parser = optparse.OptionParser()
  opt_parser.add_option("--filename", dest="filename", 
                        help="File that should be modified", metavar="FILE")
  (options, args) = opt_parser.parse_args()
  return options

# this is the main entry point of this script
if __name__ == "__main__":
  options = get_options()

  if not options.filename:
    sys.exit("Error: You must specify the file name using the '--filename' option")

  pattern = re.compile('<<<<<<< HEAD\n(.+|\n)\n=======')

  file_tmp = open(options.filename,'r')
  content = file_tmp.read()
  file_tmp.close()

  m = pattern.search(content)

  if m:
    altered_content = m.group().replace('<<<<<<< HEAD\n','').replace('\n=======','')
    if altered_content:
      file_tmp = open(options.filename,'w+')
      content = file_tmp.write(altered_content)
      file_tmp.close()      