import numpy, scipy.stats as st

from classes.base_latex_processor import BaseLatexProcessor

class TimelossNoPreemptionLatexProcessor(BaseLatexProcessor):
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
  axis y line*=left,
  y axis style=blue!75!black,
  xlabel=$Number~of~vehicles$,
  ylabel=$Timeloss(s)$,
  minor y tick num=3,minor x tick num=1,grid=minor,scaled x ticks=false,
]
\\addplot[solid,mark=square*,blue] 
plot [error bars/.cd, y dir=both, y explicit]
table [x=n_vehicles, y=no-preemption, y error plus=intconf, y error minus=intconf] {};
\\label{{Hplot}}
\\end{{axis}}

\\begin{{axis}}[
  axis y line*=right,
  axis x line=none,
  ymin=0, ymax=100,
  ylabel=$(\\frac{{Timeloss}}{{Total~Travel~Time}})\\times 100(\\percent)$,
  y axis style=red!75!black,
  minor y tick num=3,minor x tick num=1,scaled x ticks=false,
  legend style={{at={{(1.1,1)}},anchor=north west,draw=black,fill=white,align=left}}
]
\\addplot[solid,mark=*,red] 
table [x=n_vehicles, y=no-preemption] {};
\\addlegendimage{{/pgfplots/refstyle=Hplot}}
\\addlegendentry{{$\\frac{{Timeloss}}{{Total~Travel~Time}}(\\percent)$}}
\\addlegendentry{{$Timeloss(s)$}}
\\end{{axis}}

\\end{{tikzpicture}}
\\captionof{{figure}}{}
\\label{}
\\end{{center}} """

    def write_table(self, n_vehicles, result_output):
      n_vehicles = sorted(numpy.unique(n_vehicles))

      data_values = sorted(result_output.keys())

      file_prefix = self.metric+'-'+self.alg
      file_name_data = file_prefix+'-data.txt'
      table = 'n_vehicles'

      for k in data_values:
        table += ' '+str(k)
      table += ' intconf\n'

      for i in n_vehicles:
        table += str(i)
        for k in sorted(result_output.keys()):
          if i in result_output[k]:
            table += ' '+str(result_output[k][i][0])+' '+str(result_output[k][i][1])
        table += '\n'

      print('writing '+file_name_data+'...')
      file_results = open(self.data_folder+'/'+file_name_data,'w+')
      file_results.write(table)
      file_results.close()

      return file_name_data

    def print_summary(self):
      if self.location not in self.results:
        return

      result_output, n_vehicles = self.get_result_output()

      file_name_data1 = self.write_table(n_vehicles,result_output)

      self.metric = 'timeloss-ev'

      result_output, n_vehicles = self.get_result_output()

      file_name_data2 = self.write_table(n_vehicles,result_output)

      filedata1 = "{{./{}/{}}};".format(self.data_folder,file_name_data2)
      filedata2 = "{{./{}/{}}};".format(self.data_folder,file_name_data1)

      metadata = "{}-{}-{}-{}-{}".format(self.metric,self.location,self.prefix,self.ev,self.alg)
      description = "{{Timeloss \\textit{{versus}} $\\frac{{Timeloss}}{{Total~Travel~Time}}$ - {} - {} crossed Traffic Lights }}".format( \
                    self.location.upper(),self.get_tl_map()[self.location][self.ev])
      label = '{{graf-{}}}'.format(metadata)

      texfile = self.template.format(filedata1,filedata2,description,label)        

      file_name_latex = '{}-{}-0.tex'.format(self.metric,self.alg)
      print('writing '+file_name_latex+'...')
      file_results = open(self.data_folder+'/'+file_name_latex,'w+')
      file_results.write(texfile)
      file_results.close()      

      #print(texfile)

      #file_prefix = self.metric+'-'+self.alg  

     

    def process(self,args,alg_args_index,i,result_output,n_vehicles):
      if self.alg in self.results[self.location][i] and args in self.results[self.location][i][self.alg]:
        n_vec = 0
        metric_value = []
        if self.ev in self.results[self.location][i][self.alg][args] and self.ev:
          for seed in self.results[self.location][i][self.alg][args][self.ev]:
            if not self.results[self.location][i][self.alg][args][self.ev][seed]['ev_was_teleported'] and \
              not self.results[self.location][i]['no-preemption'][''][self.ev][seed]['ev_was_teleported']:
              n_vec = self.results[self.location][i][self.alg][args][self.ev][seed]['n_vehicles']

              if self.metric == 'timeloss-ev':
                metric_value.append(self.results[self.location][i][self.alg][args][self.ev][seed][self.metric])
              elif self.metric == 'timeloss-over-ttt':
                timeloss = float(self.results[self.location][i][self.alg][args][self.ev][seed]['timeloss-ev'])
                ttt = float(self.results[self.location][i][self.alg][args][self.ev][seed]['ttt-ev'])

                metric_value.append((timeloss/ttt)*100)                  
          if len(metric_value) > 0:
            shap = st.shapiro(metric_value)[1] >= 0.05
            print('loc:{}-{} alg:{} args:{} metric:{} ev:{} s_size:{} gaussian?={}'.format(self.location,i,self.alg,args,self.metric,
                  self.ev,len(metric_value),shap))

            n_vehicles.append(int(n_vec))
            #metric_value = metric_value[5:-5]

            np_metric_value = numpy.array(metric_value)
            mean = numpy.mean(np_metric_value)

            interval = st.t.interval(0.95, len(np_metric_value)-1, loc=mean, scale=st.sem(np_metric_value))

            result_output[alg_args_index][int(n_vec)] = mean,mean-interval[0]