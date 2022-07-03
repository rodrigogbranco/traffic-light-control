import numpy

from classes.base_latex_processor import BaseLatexProcessor

class TimelossOverTTTNoPreemptionLatexProcessor(BaseLatexProcessor):
    def process(self,args,alg_args_index,i,result_output,n_vehicles):
      if self.alg in self.results[self.location][i] and args in self.results[self.location][i][self.alg]:
        n_vec = 0
        metric_value = []
        if self.ev in self.results[self.location][i][self.alg][args] and self.ev:
          for seed in self.results[self.location][i][self.alg][args][self.ev]:
            if not self.results[self.location][i][self.alg][args][self.ev][seed]['ev_was_teleported'] and \
              not self.results[self.location][i]['no-preemption'][''][self.ev][seed]['ev_was_teleported']:
              n_vec = self.results[self.location][i][self.alg][args][self.ev][seed]['n_vehicles']

              timeloss = float(self.results[self.location][i][self.alg][args][self.ev][seed]['timeloss-ev'])
              ttt = float(self.results[self.location][i][self.alg][args][self.ev][seed]['ttt-ev'])

              metric_value.append((timeloss/ttt)*100)
          if len(metric_value) > 0:
            n_vehicles.append(int(n_vec))
            metric_value = numpy.array(metric_value)

            result_output[alg_args_index][int(n_vec)] = numpy.mean(metric_value)  