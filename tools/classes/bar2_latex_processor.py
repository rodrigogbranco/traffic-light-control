import numpy as np, scipy.stats as st
import collections

import pandas as pd

from classes.base_latex_processor import BaseLatexProcessor

class Bar2LatexProcessor(BaseLatexProcessor):
  def __init__(self, location, metric, alg, args_of_alg, results, data_folder, excludeoutliers, ev, prefix, label):
    super().__init__(location, metric, alg, args_of_alg, results, data_folder, excludeoutliers, ev, prefix, label)
    self.template = """\\begin{{center}}
\\pgfplotsset{{compat=newest}}

\\begin{{tikzpicture}}[scale=1]

\\pgfplotsset{{
    scale only axis,
    y axis style/.style={{
        yticklabel style=#1,
        ylabel style=#1,
        y axis line style=#1,
        ytick style=#1
  }}
}}

\\begin{{axis}}[
ybar,
enlargelimits=0.135,
legend style={{at={{(1.01,1)}},anchor=north west,draw=black,fill=white,align=left,font=\\tiny}},
ylabel =${{Timeloss gain=(\\frac{{Timeloss~After}}{{Timeloss~Before}})\\times 100(\\percent)}}$,
xlabel=$Number~of~vehicles$,
symbolic x coords ={},
minor y tick num=3,minor x tick num=1,grid=minor,scaled x ticks=false,
/pgf/bar width=3.5pt
]
{}
\\legend {}
\\end{{axis}}
\\end{{tikzpicture}}

\\captionof{{figure}}{}
\\label{}
\\end{{center}} """ 

    self.table_template = """
\\begin{{table}}[!t]
\\centering
\\caption{{$\\rho$-values from Mann–Whitney U test for N={}. We cannot see statistical differences between evaluated algorithms 
if the $\\rho$-value were bigger than 0.05. Legend: {}}}
\\begin{{small}}
\\begin{{tabular}}{{ccccccccc}} \\hline
\\textbf{{Algorithm}} & {} \\\\ \\hline 
{} \\\\
\\hline
\\end{{tabular}}
\\end{{small}}
\\label{}    
\\end{{table}}  
  """

  def set_aditional_data(self, **args):
    self.algs = args.pop('algs')

  def get_result_output(self):     
    result_output = collections.OrderedDict()
    n_vehicles = []

    for alg in self.algs:
      args = self.algs[alg]

      for arg in args:
        alg_args_index = '{}-{}'.format(alg,arg) if len(args) > 0 else alg

        if alg_args_index not in result_output:
          result_output[alg_args_index] = {}

          for i in self.results[self.location]:
            self.alg = alg
            self.process(arg,alg_args_index,i,result_output,n_vehicles)

    return result_output, n_vehicles

  def print_summary(self):
    if self.location not in self.results:
      return

    result_output, n_vehicles = self.get_result_output()
    n_veh_unique = np.unique(n_vehicles)
    max_cars = max(n_veh_unique)    

    algs_name = []
    for alg_args in result_output:
      alg = alg_args.split('-')[0]

      if alg not in algs_name:
        algs_name.append(alg)

    algs_name.sort()

    chosen_algs = {}

    chosen_algs['best'] = {}
    chosen_algs['worst'] = {}    

    for alg_args in result_output:
      alg = alg_args.split('-')[0]

      should_stop = False

      for x in n_veh_unique:
        if x not in result_output[alg_args]:
          should_stop = True
          break

      if should_stop:
        continue

      if alg not in chosen_algs['best']:
        chosen_algs['best'][alg] = {}
        chosen_algs['best'][alg]['instance'] = alg_args
        chosen_algs['best'][alg]['mean'] = result_output[alg_args][max_cars][0]
        chosen_algs['best'][alg]['values'] = result_output[alg_args][max_cars][2]
      if alg not in chosen_algs['worst']:
        chosen_algs['worst'][alg] = {}
        chosen_algs['worst'][alg]['instance'] = alg_args
        chosen_algs['worst'][alg]['mean'] = result_output[alg_args][max_cars][0]
        chosen_algs['worst'][alg]['values'] = result_output[alg_args][max_cars][2]


      if result_output[alg_args][max_cars][0] > chosen_algs['best'][alg]['mean']:
        chosen_algs['best'][alg]['instance'] = alg_args
        chosen_algs['best'][alg]['mean'] = result_output[alg_args][max_cars][0]
        chosen_algs['best'][alg]['values'] = result_output[alg_args][max_cars][2]

      elif result_output[alg_args][max_cars][0] < chosen_algs['worst'][alg]['mean']: 
        chosen_algs['worst'][alg]['instance'] = alg_args
        chosen_algs['worst'][alg]['mean'] = result_output[alg_args][max_cars][0]
        chosen_algs['worst'][alg]['values'] = result_output[alg_args][max_cars][2]


    n_veh_values_str = '{{{}}}'.format(','.join(n_veh_unique.astype(str)))

    addplot_entries = []
    legends = []

    patterns = ['blue!100!blue,pattern=horizontal lines,pattern color=blue!100!white',
                'blue!50!blue,pattern=north west lines,pattern color=blue!50!white',
                'red!100!red,pattern=grid,pattern color=red!100!white',
                'red!50!red,pattern=dots,pattern color=red!50!white',
                'black!100!black,pattern=north east lines',
                'black!100!black,fill=black!0!white',
                'brown!100!brown,pattern=crosshatch dots,pattern color=brown!100!white',
                'brown!50!brown,pattern=crosshatch,pattern color=brown!50!white']

    pattern_index = 0

    filei = 0

    for alg in algs_name:
      for br in ['best','worst']:
        tuple_values = []

        filei_h = open('{}/{}-{}.dat'.format(self.data_folder,filei,self.location),'w+')

        i = 0
        for n in n_veh_unique:
          alg_name = chosen_algs[br][alg]['instance']
          if n in result_output[alg_name]:
            tuple_template = '({},{}) +- (0.0, {})'
            tuple_values.append(tuple_template.format(n,result_output[alg_name][n][0],result_output[alg_name][n][1]))
            filei_h.write('{} {} {}\n'.format(i,result_output[alg_name][n][0],result_output[alg_name][n][1]))
            i = i + 2
        addplot_entry = '\\addplot+[{},error bars/.cd,y dir=both,y explicit] coordinates {{{}}};'.format(patterns[pattern_index],' '.join(tuple_values))
        addplot_entries.append(addplot_entry)
        legends.append(alg_name.replace('_','\_'))
        pattern_index += 1

        filei_h.close()

        filei = filei+1

    addplot_final = '\n'.join(addplot_entries)
    legends_final = '{{{}}}'.format(','.join(legends))

    file_labels = open('{}/{}-labels.dat'.format(self.data_folder,self.location),'w')
    file_labels.write('\n'.join(legends))
    file_labels.close()

    file_nvec = open('{}/{}-nvec.dat'.format(self.data_folder,self.location),'w')
    file_nvec.write('\n'.join(n_veh_unique.astype(str)))
    file_nvec.close()


    curr_letter = 'A'
    start_at = 0

    letters = {}
    for alg in algs_name:
      for br in ['best','worst']:
        letters[curr_letter] = {}
        letters[curr_letter]['name'] = chosen_algs[br][alg]['instance']
        letters[curr_letter]['values'] = []

        starting_from = 0
        for alg2 in algs_name:
          for br2 in ['best','worst']:
            if starting_from >= start_at:
              alg_name = chosen_algs[br][alg]['instance']
              alg_name2 = chosen_algs[br2][alg2]['instance']
              if not (alg_name == alg_name2 and br == br2):
                v1 = chosen_algs[br][alg]['values']
                v2 = chosen_algs[br2][alg2]['values']
                pval = st.mannwhitneyu(v1, v2, alternative = 'two-sided')[1]
                pval_string = '${:.2f}$'.format(pval) if pval >= 0.01 else '$< 0.01$'
                letters[curr_letter]['values'].append(pval_string)
              else:
                letters[curr_letter]['values'].append('$X$')
            else:
              letters[curr_letter]['values'].append(' ')
            
            starting_from += 1

        curr_letter = chr(ord(curr_letter)+1)
        start_at += 1

    table_header = [ '\\textbf{{[{}]}}'.format(l) for l in  letters]
    table_header = ' & '.join(table_header)

    table_lines = []
    table_legend = []

    for l in letters:
      table_lines.append('\\textbf{{[{}]}} & {}'.format(l,' & '.join(letters[l]['values'])))
      table_legend.append('\\textbf{{[{}]}} {}'.format(l,letters[l]['name'].replace('_','\_')))
    table_lines = ' \\\\ \n'.join(table_lines)  
    table_legend = ',\n '.join(table_legend)
      
    metadata = "{}-{}-{}-{}".format('improvement-comparision',self.location,self.prefix,self.ev)
    description = "{{Improvement - {} - {} crossed Traffic Lights }}".format( \
                    self.location.upper(),self.get_tl_map()[self.location][self.ev])
    label = '{{graf-{}}}'.format(metadata)
    table_label = '{{table:pvalues-{}}}'.format(metadata)

    texfile = self.template.format(n_veh_values_str,addplot_final,legends_final,description,label) 
    table_texfile = self.table_template.format(max_cars,table_legend,table_header,table_lines,table_label)       

    file_name_latex = 'improvement.tex'
    print('writing {}...'.format(file_name_latex))
    file_results = open('{}/{}'.format(self.data_folder,file_name_latex),'w+')
    file_results.write(texfile)
    file_results.close()

    table_latex = 'table.tex'
    print('writing {}...'.format(table_latex))
    file_results = open('{}/{}'.format(self.data_folder,table_latex),'w+')
    file_results.write(table_texfile)
    file_results.close()        

  def process(self,args,alg_args_index,i,result_output,n_vehicles):
    if self.alg in self.results[self.location][i] and args in self.results[self.location][i][self.alg]:
      n_vec = 0
      metric_value = []
      metric_alg_v = []
      metric_nopreempt_v = []
      if self.ev in self.results[self.location][i][self.alg][args] and self.ev:
        for seed in self.results[self.location][i][self.alg][args][self.ev]:
          if not self.results[self.location][i][self.alg][args][self.ev][seed]['ev_was_teleported'] and \
            not self.results[self.location][i]['no-preemption'][''][self.ev][seed]['ev_was_teleported']:
            n_vec = self.results[self.location][i][self.alg][args][self.ev][seed]['n_vehicles']

            metric_alg = self.results[self.location][i][self.alg][args][self.ev][seed][self.metric]
            metric_nopreempt = self.results[self.location][i]['no-preemption'][''][self.ev][seed][self.metric]

            metric_nopreempt_v.append(metric_nopreempt)
            metric_alg_v.append(metric_alg)

            #metric_v = 1-metric_alg/metric_nopreempt            
            metric_v = (metric_alg/metric_nopreempt)-1

            #print('{}/{}'.format(metric_alg,metric_nopreempt))

            metric_value.append(metric_v*100)                  
        if len(metric_value) > 0:
          n_vehicles.append(int(n_vec))

          #trim = int(len(metric_value)*0.125)

          keys = sorted(range(len(metric_value)), key=lambda k: metric_value[k])
          #keys = keys[trim:-trim]

          metric_value = [ metric_value[k] for k in keys ]
          metric_nopreempt_v = [ metric_nopreempt_v[k] for k in keys ]
          metric_alg_v = [ metric_alg_v[k] for k in keys ]

          u_statistic, pval = st.mannwhitneyu(metric_nopreempt_v, metric_alg_v, alternative = 'two-sided')

          np_metric_value = np.array(metric_value)

          interval = st.t.interval(0.95, len(np_metric_value)-1, loc=np.mean(np_metric_value), scale=st.sem(np_metric_value))
          mean = np.mean(metric_value)

          metric_value = np.array(metric_value)

          #same population -> p >= 0.05
          result_output[alg_args_index][int(n_vec)] = mean,mean-interval[0],metric_value,pval
