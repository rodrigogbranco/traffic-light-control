import numpy as np, scipy.stats as st
import collections

from pylab import plot, show, savefig, xlim, figure, hold, ylim, legend, boxplot, setp, axes, ylabel, xlabel, grid

from statsmodels.graphics.gofplots import qqplot

import pandas

from matplotlib import pyplot

from matplotlib.font_manager import FontProperties

from classes.base_latex_processor import BaseLatexProcessor

class BoxplotLatexProcessor(BaseLatexProcessor):

  def set_aditional_data(self, **args):
    self.algs = args.pop("algs", {})
    self.best_worst = args.pop("best_worst", "True")  

  def setBoxColors(self,bp):
      setp(bp['boxes'][0], color='blue')
      setp(bp['caps'][0], color='blue')
      setp(bp['caps'][1], color='blue')
      setp(bp['whiskers'][0], color='blue')
      setp(bp['whiskers'][1], color='blue')
      setp(bp['medians'][0], color='blue')

      setp(bp['boxes'][1], color='red')
      setp(bp['caps'][2], color='red')
      setp(bp['caps'][3], color='red')
      setp(bp['whiskers'][2], color='red')
      setp(bp['whiskers'][3], color='red')
      setp(bp['medians'][1], color='red')

      setp(bp['boxes'][2], color='black')
      setp(bp['caps'][4], color='black')
      setp(bp['caps'][5], color='black')
      setp(bp['whiskers'][4], color='black')
      setp(bp['whiskers'][5], color='black')
      setp(bp['medians'][2], color='black')

      setp(bp['boxes'][3], color='green')
      setp(bp['caps'][6], color='green')
      setp(bp['caps'][7], color='green')
      setp(bp['whiskers'][6], color='green')
      setp(bp['whiskers'][7], color='green')
      setp(bp['medians'][3], color='green')                   

  def get_result_output(self):     
    result_output = collections.OrderedDict()
    n_vehicles = []

    for alg in self.algs:
      args = self.algs[alg]

      for arg in args:
        if len(args) > 0:
          alg_args_index = '{}-{}'.format(alg,arg)
        else:
          alg_args_index = alg

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

    for alg_args in result_output:
      alg = alg_args.split('-')[0]

      should_stop = False

      for x in n_veh_unique:
        if x not in result_output[alg_args]:
          should_stop = True
          break

      if should_stop:
        continue

      if alg not in chosen_algs:
        chosen_algs[alg] = {}
        chosen_algs[alg]['instance'] = alg_args
        chosen_algs[alg]['median'] = result_output[alg_args][max_cars][0]
      elif self.best_worst == 'True' and result_output[alg_args][max_cars][0] > chosen_algs[alg]['median'] or \
        self.best_worst == 'False' and result_output[alg_args][max_cars][0] < chosen_algs[alg]['median']:
        chosen_algs[alg]['instance'] = alg_args
        chosen_algs[alg]['median'] = result_output[alg_args][max_cars][0]

    fig = figure()
    ax = axes()
    #hold(True)

    grid(color='gray', linestyle='-', linewidth=0.5)

    j = 0
    ranges = [[1,2,3,4],[6,7,8,9],[11,12,13,14],[16,17,18,19],[21,22,23,24]]

    for i in n_veh_unique:
      values = []
      for alg in algs_name:
        alg_name = chosen_algs[alg]['instance']
        values.append(result_output[alg_name][i][1])

        #datav = result_output[alg_name][i][1]  
        #qqplot(np.array(datav), line='s')
        #pyplot.show()

      bp = ax.boxplot(values, positions = ranges[j], widths = 0.6, notch = True, bootstrap = 10000)
      self.setBoxColors(bp)
      j += 1

    algs_with_args = []
    for alg in algs_name:
      algs_with_args.append(chosen_algs[alg]['instance'])         

    # set axes limits and labels
    xlim(0,25)
    ymin, ymax = ylim(ymax=100)

    if ymin < -100:
      ylim(ymin=-100,ymax=ymax)
    #ax.set_xticklabels(['A', 'B', 'C', 'D', 'E'])
    ax.set_xticklabels(n_veh_unique)
    ax.set_xticks([2.5, 7.5, 12.5, 17.5, 22.5])

    # draw temporary red and blue lines and use them to create a legend
    h_blue, = plot([1,1],'b-', label=algs_with_args[0])
    h_red, = plot([1,1],'r-', label=algs_with_args[1])
    h_black, = plot([1,1],color='black', label=algs_with_args[2])
    h_green, = plot([1,1],color='green', label=algs_with_args[3])
    h_blue.set_visible(True)
    h_red.set_visible(True)
    h_black.set_visible(True)
    h_green.set_visible(True)
    font_p = FontProperties()
    font_p.set_size('small')


    legend(handles=[h_blue,h_red,h_black,h_green],
    loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=2, fancybox=True, shadow=True, prop=font_p)

    ylabel(self.label)  
    xlabel('Number of vehicles')

    savefig('{}/boxcompare{}.png'.format(self.data_folder,self.best_worst))
    #show()

    file_name_latex = 'improvement.tex'
    print('writing {}...'.format(file_name_latex))

    bw = 'Best' if self.best_worst == 'True' else 'Worst'    

    metadata = "{}-{}-{}-{}-{}".format('improvement-comparision',self.location,self.prefix,self.ev,self.best_worst)
    description = "Improvement - {} - {} crossed Traffic Lights - {}".format( \
                    self.location.upper(),self.get_tl_map()[self.location][self.ev],bw)
    label = 'graf-{}'.format(metadata)    

    texfile = """\\begin{{figure}}[htbp]
  \\centering
  \\includegraphics[width=0.48\\textwidth]{{{}/boxcompare{}.png}}
  \\caption{{{}}}
  \\label{{{}}}
\\end{{figure}}""".format(self.data_folder,self.best_worst,description,label)

    file_results = open('{}/{}'.format(self.data_folder,file_name_latex),'w+')
    file_results.write(texfile)
    file_results.close()

  def process(self,arg,alg_args_index,i,result_output,n_vehicles):
    if self.alg in self.results[self.location][i] and arg in self.results[self.location][i][self.alg]:
      n_vec = 0
      metric_value = []
      metric_diff = []
      if self.ev in self.results[self.location][i][self.alg][arg] and self.ev:
        for seed in self.results[self.location][i][self.alg][arg][self.ev]:
          if not self.results[self.location][i][self.alg][arg][self.ev][seed]['ev_was_teleported'] and \
            not self.results[self.location][i]['no-preemption'][''][self.ev][seed]['ev_was_teleported']:
            n_vec = self.results[self.location][i][self.alg][arg][self.ev][seed]['n_vehicles']

            metric_alg = self.results[self.location][i][self.alg][arg][self.ev][seed][self.metric]
            metric_nopreempt = self.results[self.location][i]['no-preemption'][''][self.ev][seed][self.metric]

            metric_v = 1-metric_alg/metric_nopreempt            

            metric_value.append(metric_v*100)             

            metric_diff.append(metric_alg-metric_nopreempt)

            #if metric_v < 0 and self.alg == 'petri':
            #  print('loc:{}-{} alg:{} args:{} metric:{} ev:{} seed:{} {}/{} = {}'.format(self.location,i,self.alg,arg,self.metric,
            #        self.ev,seed,metric_alg,metric_nopreempt, float(metric_alg)/float(metric_nopreempt)))

        if len(metric_value) > 0:
          #if len(metric_value) < 3:
          #  print('SIZE:'+str(len(metric_value))+' WARNING: SAMPLE TOO SMALL')
          #elif stats.shapiro(metric_value)[1] < 0.05:
          #  print('SIZE:'+str(len(metric_value))+' WARNING: SAMPLE NOT NORMAL')
          #else:
          #  print('SIZE:'+str(len(metric_value))+' WARNING: SAMPLE IS NORMAL')
          # 
          metric_value = metric_value[5:-5]          

          if len(metric_value) >= 3:
            shap = st.shapiro(metric_value)[1] >= 0.05
            w, p = st.wilcoxon(metric_diff)
            if p >= 0.05 or not shap:
              print('loc:{}-{} alg:{} args:{} metric:{} ev:{} s_size:{} WilcoxonResult failure pvalue={} gaussian?={}'.format(self.location,i,self.alg,arg,self.metric,
                    self.ev,len(metric_value),p,shap))
            #else:
            #  print('SIZE:'+str(len(metric_value))+' WilcoxonResult successful: pvalue='+str(p))

          n_vehicles.append(int(n_vec))

          metric_value.sort()

          #result_output[alg_args_index][int(n_vec)] = np.median(metric_value[5:-5]),metric_value[5:-5]

          #if self.alg == 'petri':
          #  print('{}-{} - {}'.format(self.alg,arg,metric_value))          
          result_output[alg_args_index][int(n_vec)] = np.median(metric_value),metric_value