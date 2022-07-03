# deltaq.py

import math
import pandas as pd

import plotly.express as px

a = 2.6
k = 0.149129457  # in veh/m = 240 vehicles per mile
s = 0.444444444  # in veh/s = 1600 vehicles per hour
car_length = 4.3
t_flush = 5
Q_vector = [0, 50, 100, 150, 200, 250, 300, 500]
t_alpha = 3

algs = ['TPN', 'Queue Based']


def get_df(orig_v, cycle_length):
    data = {'Algorithm': [], 'Queue Length (m)': [], 'Metric' : [], 'Metric Value' : [], 'D': [], 'Instance' : []}
    v = orig_v/3.6
    for Q in Q_vector:
        t_ev = t_alpha*cycle_length
        d = t_ev*v

        t_last = (Q*k)/s
        t_queue = t_last
        Q_a = (v**2)/(2*a)

        t_queue += math.sqrt((2*Q)/a) if Q <= Q_a else v/a + (Q - Q_a)/v

        for alg in algs:
            if t_ev - t_queue >= 0:
                if alg == 'TPN':
                    t_offset = max(0.5*(t_ev - t_queue - t_flush), 0)
                elif alg == 'Queue Based':
                    t_offset = max(t_ev - t_queue, 0)

                sq_part = math.sqrt(2*a*k*s**3*(t_queue + t_offset) + s**4)/a
                remainder = (s**2)/a + k*s*(t_queue + t_offset)

                minus_part = (-sq_part + remainder)/(k**2)
                plus_part = (sq_part + remainder)/(k**2)

                delta_q = -Q + max(minus_part, plus_part)

                if Q + delta_q > Q_a:
                    delta_q = -Q + \
                        (s*v*((a**2 - 2)*v + 2*a*(t_queue + t_offset))) / \
                        (2*a*(k*v + s))

                if delta_q >= 0 and t_offset >= 0:
                    for metric in [u'ΔQ (m)', 'Activation (s)']:
                        data['Algorithm'].append(alg)
                        data['Queue Length (m)'].append(Q)
                        data['Metric'].append(metric)
                        data['Metric Value'].append(delta_q if metric == u'ΔQ (m)' else (0 if alg == 'Queue Based' else t_offset))
                        data['D'].append(d)
                        data['Instance'].append('Algorithm={} v={}km/h CycleLength={}s'.format(alg,orig_v,cycle_length))
                    

    return pd.DataFrame(data)

df = pd.concat([get_df(50, 15), get_df(70, 30), get_df(90, 45), get_df(110, 60)])

print(df)

fig = px.line(df, x='Queue Length (m)', y='Metric Value', color='Instance', markers=True, line_dash='Instance', symbol='Instance', facet_col='Metric')
fig.layout.yaxis2.update(matches=None,showticklabels=True)
fig.show()