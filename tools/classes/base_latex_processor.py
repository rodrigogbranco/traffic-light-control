import numpy
import math

class BaseLatexProcessor():
  def __init__(self, location, metric, alg, args_of_alg, results, data_folder, excludeoutliers, ev, prefix, label):
    self.location = location
    self.metric = metric
    self.alg = alg
    self.args_of_alg = args_of_alg
    self.results = results
    self.data_folder = data_folder
    self.excludeoutliers = excludeoutliers
    self.ev = ev
    self.prefix = prefix
    self.label = label

  def get_tl_map(self):
    tl_map = {
      'sp': {
        'veh7058': 5,
        'veh5393': 20,
        'veh7377': 35,
        'veh5894': 50,
        'veh11651': 65          
      },
      'ny': {
        'veh4216': 5,
        'veh4046': 20,
        'veh4028': 35,
        'veh2735': 50,
        'veh4856': 65          
      }
    }

    return tl_map    

  def set_aditional_data(self, **args):
    pass  

  def write_table(self, n_vehicles, result_output):
    n_vehicles = sorted(numpy.unique(n_vehicles))

    data_values = sorted(result_output.keys())

    file_prefix = self.metric+'-'+self.alg
    file_name_data = file_prefix+'-data.txt'
    table = 'n_vehicles'

    for k in data_values:
      table += ' '+str(k)
    table += '\n'

    for i in n_vehicles:
      table += str(i)
      for k in sorted(result_output.keys()):
        if i in result_output[k]:
          table += ' '+str(result_output[k][i])
      table += '\n'

    print('writing '+file_name_data+'...')
    file_results = open(self.data_folder+'/'+file_name_data,'w+')
    file_results.write(table)
    file_results.close()

    return file_name_data

  def get_result_output(self):     
    result_output = {}
    n_vehicles = []

    for args in numpy.unique(self.args_of_alg):
      if len(args) > 0:
        alg_args_index = '{}-{}'.format(self.alg,args)
      else:
        alg_args_index = self.alg
      result_output[alg_args_index] = {}

      for i in self.results[self.location]:
        self.process(args,alg_args_index,i,result_output,n_vehicles)

    return result_output, n_vehicles

  def print_summary(self):
    marks_and_colors = ['smooth,mark=x,black','dashed,mark=*,red','thick,mark=o,blue','solid,mark=*,green',
                        'dashdotted,mark=diamond,purple','dashdotdotted,mark=star,magenta','dashed,mark=triangle,orange',
                        'dashdotted,mark=star,pink','dotted,mark=square,black','densely dashed,mark=Mercedes star,cyan',
                        'smooth,mark=x,cyan','dashed,mark=*,black','thick,mark=o,pink','solid,mark=*,orange',
                        'dashdotted,mark=diamond,magenta','dashdotdotted,mark=star,purple','dashed,mark=triangle,green',
                        'dashdotted,mark=star,blue','dotted,mark=square,red','densely dashed,mark=Mercedes star,black']

    if self.location not in self.results:
      return

    result_output, n_vehicles = self.get_result_output()

    data_values = sorted(result_output.keys())

    file_name_data = self.write_table(n_vehicles,result_output)

    file_prefix = self.metric+'-'+self.alg
    p = 0
    addplot = []
    legend = []
    marks_and_colors_length = len(marks_and_colors)
    for k in data_values:
      if math.floor(p / marks_and_colors_length) == len(addplot):
        addplot.append('')
        legend.append('\\legend{')

      addplot[math.floor(p / marks_and_colors_length)] += '\\addplot['+marks_and_colors[p % len(marks_and_colors)]+'] table [x=n_vehicles, y='+k+']'+\
                ' {./'+self.data_folder+'/'+file_name_data+'};\n'
      legend[math.floor(p / marks_and_colors_length)] += k
      p +=1
      if math.floor(p / marks_and_colors_length) != len(addplot) and k != data_values[-1]:
        legend[math.floor(p / marks_and_colors_length)] += ', '

    for x in range(0,len(addplot)):
      legend[x] += '}\n'
      file_name_latex = file_prefix+'-'+str(x)+'.tex'
      print('writing '+file_name_latex+'...')
      file_results = open(self.data_folder+'/'+file_name_latex,'w+')
      self.print_header(file_results)
      file_results.write(addplot[x])
      file_results.write(legend[x].replace('_','\_'))
      self.print_footer(file_results,x)
      file_results.close()

  def print_header(self, file_results):
    header_latex = '\\begin{center}\n'
    header_latex += '\\pgfplotsset{legend style={at={(1.03,0.5)}, anchor=south}}\n'
    header_latex += '\\begin{tikzpicture}[scale=1]\n'
    header_latex += '\\begin{axis}[scaled x ticks=false,minor y tick num=3,minor x tick num=1,grid=minor,'
    header_latex += 'xlabel=$Number~of~vehicles$, ylabel={'+str(self.label)+'},legend style={at={(1.03,1)},'
    header_latex += 'anchor=north west,draw=black,fill=white,align=left}]\n'    
    file_results.write(header_latex)


  def print_footer(self, file_results, x):
    file_results.write('\\end{axis}\n')
    file_results.write('\\end{tikzpicture}\n')
    file_results.write('\\captionof{figure}{'+str(self.metric)+' - '+str(self.location)+' - '+str(self.prefix)+' - '+str(self.ev)+' - '+str(self.alg)+'('+str(x)+')}\n')
    file_results.write('\\label{graf-'+str(self.metric)+'-'+str(self.location)+'-'+str(self.prefix)+'-'+str(self.ev)+'-'+str(self.alg)+'-'+str(x)+'}\n')
    file_results.write('\\end{center}\n') 

  def process(self,args,alg_args_index,i,result_output,n_vehicles):
    pass   