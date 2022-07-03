import numpy
import pandas
import scipy.stats as stats

from classes.base_latex_processor import BaseLatexProcessor

class ImprovementLatexProcessor(BaseLatexProcessor):
    def process(self,args,alg_args_index,i,result_output,n_vehicles):
      loc = self.results[self.location][i]
      if self.alg in loc and args in loc[self.alg] and 'no-preemption' in loc:
        n_vec = 0
        metric_value = []
        metric_diff = []
        if self.ev in loc[self.alg][args] and self.ev in loc['no-preemption']['']:
          loc_alg_args = loc[self.alg][args]
          loc_noprempt = loc['no-preemption']['']
          for seed in loc_alg_args[self.ev]:
            if seed in loc_noprempt[self.ev] and \
              not loc_noprempt[self.ev][seed]['ev_was_teleported'] and \
              not loc_alg_args[self.ev][seed]['ev_was_teleported']:
              n_vec = loc_alg_args[self.ev][seed]['n_vehicles']

              metric_alg = loc_alg_args[self.ev][seed][self.metric]
              metric_nopreempt = loc_noprempt[self.ev][seed][self.metric]

              metric_v = metric_alg/metric_nopreempt

              if metric_v >= 1 and self.metric == 'timeloss-ev' and self.alg == 'petri':
                print('loc:{}-{} alg:{} args:{} metric:{} ev:{} seed:{} {}/{} = {}'.format(self.location,i,self.alg,args,self.metric,
                      self.ev,seed,metric_alg,metric_nopreempt, float(metric_alg)/float(metric_nopreempt)))

              if self.metric != 'ev-speed-avg':
                metric_v = 1 - metric_v

              metric_value.append(metric_v*100)

              metric_diff.append(loc_alg_args[self.ev][seed][self.metric]-loc_noprempt[self.ev][seed][self.metric])

          if len(metric_value) > 0:
            #if len(metric_value) < 3:
            #  print('SIZE:'+str(len(metric_value))+' WARNING: SAMPLE TOO SMALL')
            #elif stats.shapiro(metric_value)[1] < 0.05:
            #  print('SIZE:'+str(len(metric_value))+' WARNING: SAMPLE NOT NORMAL')
            #else:
            #  print('SIZE:'+str(len(metric_value))+' WARNING: SAMPLE IS NORMAL')

            #if len(metric_value) >= 3:
              #w, p = stats.wilcoxon(metric_diff)
              #if (p >= 0.05):
              #  print('SIZE:'+str(len(metric_value))+' WilcoxonResult unsuccessful: pvalue='+str(p))
              #else:
              #  print('SIZE:'+str(len(metric_value))+' WilcoxonResult successful: pvalue='+str(p))


            n_vehicles.append(int(n_vec))
            metric_value = numpy.array(metric_value)

            if not self.excludeoutliers:
              result_output[alg_args_index][int(n_vec)] = numpy.mean(metric_value)
            else:
              df = pandas.DataFrame(data=metric_value)
              Q1 = df.quantile(0.25)
              Q3 = df.quantile(0.75)
              IQR = Q3 - Q1
              metric_value = df[~((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).any(axis=1)]
              result_output[alg_args_index][int(n_vec)] = numpy.mean(metric_value.values)      