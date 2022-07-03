import json
import os
from matplotlib.legend import Legend
import numpy as np
import matplotlib
from pandas.core.algorithms import isin
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import statsmodels.stats.api as sms
import pandas as pd
import sys
import scipy.stats as sp
import seaborn as sns

hatches = ['/', '\\', 'o', '*', '-', '+']

sns.set_theme(style="ticks", palette="pastel")

labels = {
    'scenarios' : {
        'od500k' : 'Origin/Destination Survey - 500K vehicles',
        'od1500k' : 'Origin/Destination Survey - 1.5M vehicles',
        'odanalysis' : 'EV2 with splitted route',
        'turin' : 'Turin - TuSTScenario',
        'cologne' : 'TAPAS Cologne'
    },
    'algs' : {
        'kapusta2': 'Kapusta et al (2017)',
        'allgreen': 'Hyphotetical all-green',
        'tpn2' : 'TPN',
        'no-preemption' : 'No Preemption',
        'tpn' : 'TPN (Old)',
        'kapusta': 'Kapusta et al (2017) [1st version]'
    },
    'graphs' : {
        'tl' : {
            'ylabel' : 'Timeloss (s)',
            'title' : 'Timeloss  - {}',
            'barpath' : '{}/timeloss-bar-{}.png',
            'boxplotpath' : '{}/timeloss-boxplot-{}.png',
            'xlabel' : 'Emergency Vehicles'
        },
        'rt' : {
            'ylabel' : 'Runtime (s)',
            'title' : 'Runtime  - {}',
            'barpath' : '{}/runtime-bar-{}.png',
            'boxplotpath' : '{}/runtime-boxplot-{}.png',
            'xlabel' : 'Emergency Vehicles'
        },
        'imp' : {
            'ylabel' : 'Time-Loss Improvement (x)',
            'title' : '{}',
            'barpath' : '{}/improvement-bar-{}.png',
            'boxplotpath' : '{}/improvement-boxplot-{}.png',
            'xlabel' : 'Emergency Vehicles'
        },
        'ttt' : {
            'ylabel' : 'Total Time (s)',
            'title' : 'No Preemption - {}',
            'barpath' : '{}/totaltime-{}.png',
            'boxplotpath' : '{}/totaltime-boxplot-{}.png',
            'xlabel' : 'Emergency Vehicles'
        }
    },
    'evs' : {
        'vehev1' : 'EV1',
        'vehev2' : 'EV2',
        'vehev3' : 'EV3'
    }       
}

algs_order_global = ['kapusta2', 'tpn2', 'allgreen']
ev_order_global = ['vehev1', 'vehev2', 'vehev3']
exclude_algs = ['tpn','kapusta']

def finish_fig(ax, figpath, metric, scenario, base_path, add_legend=True):
    ax.set_title(labels['graphs'][metric]['title'].format(labels['scenarios'][scenario]))

    plt.grid()

    if add_legend:
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.3), borderaxespad=0., fancybox=True, shadow=True)

    plt.subplots_adjust(bottom=0.25)

    plt.tight_layout()

    fig_path = labels['graphs'][metric][figpath].format(base_path,scenario)
    plt.savefig(fig_path)

    plt.close()

    print('{} generated'.format(fig_path))

def plot_stacked(df, ev_order, metric, scenario, base_path):
    plt.figure()

    sns.barplot(x = 'ev', y = 'ttt', data = df, color='g', order=ev_order, ci=None, label='Total Travel Time')
    ax = sns.barplot(x = 'ev', y = 'tl', data = df, color='r', capsize=0.1, order=ev_order, label='Timeloss')

    count = 0
    ev_count = len(ev_order)
    for k,thisbar in enumerate(ax.patches):
        count += 1 if k % ev_count == 0 else 0
        thisbar.set_hatch(hatches[count - 1])      

    ax.set_ylabel(labels['graphs'][metric]['ylabel'])
    ax.set_xlabel(labels['graphs'][metric]['xlabel'])

    finish_fig(ax, 'barpath', metric, scenario, base_path) 

def plot_bar(df, ev_order, algs_order, metric, scenario, base_path):
    plt.figure()
    g = sns.catplot(x="ev", y=metric, hue="alg", kind="bar", data=df[(df[metric].notnull())], capsize=0.1, hue_order=algs_order, order=ev_order, legend=False)

    count = 0
    ev_count = len(ev_order)
    for k,thisbar in enumerate(g.ax.patches):
        count += 1 if k % ev_count == 0 else 0
        thisbar.set_hatch(hatches[count - 1])  

    g.set_axis_labels(labels['graphs'][metric]['xlabel'], labels['graphs'][metric]['ylabel'])
    finish_fig(g.ax, 'barpath', metric, scenario, base_path)


def plot_boxplot(df,ev_order, algs_order, metric, scenario, base_path):
    plt.figure()
    ax = sns.boxplot(x="ev", y=metric, hue="alg", data=df[(df[metric].notnull())], hue_order=algs_order, order=ev_order,
            showmeans=True,
            meanprops={"marker":"+", "markeredgecolor":"red", "markersize": "15", 'linewidth': 1.5},
            whis=[15, 85]
    )

    count = 0
    algs_count = len(algs_order)
    for patch in ax.artists:
        patch.set_hatch(hatches[count % algs_count])
        count += 1

    ax.set_ylabel(labels['graphs'][metric]['ylabel'])
    ax.set_xlabel(labels['graphs'][metric]['xlabel'])          

    finish_fig(ax, 'boxplotpath', metric, scenario, base_path)

def plot_boxplot_nopreemption(df,ev_order, algs_order, metric, scenario, base_path):
    plt.figure()
    ax = sns.boxplot(x="ev", y=metric, data=df[(df[metric].notnull())], order=ev_order,
            showmeans=True,
            meanprops={"marker":"+", "markeredgecolor":"red", "markersize": "15", 'linewidth': 1.5},
            whis=[15, 85]
    )

    count = 0
    ev_count = len(ev_order)
    for patch in ax.artists:
        patch.set_hatch(hatches[count % ev_count])
        count += 1

    ax.set_ylabel(labels['graphs'][metric]['ylabel'])
    ax.set_xlabel(labels['graphs'][metric]['xlabel'])          

    finish_fig(ax, 'boxplotpath', metric, scenario, base_path, add_legend=False)         


if __name__ == "__main__":
    base_path = sys.argv[1]
    scenario = sys.argv[2]

    df = pd.read_csv('{}/summary.csv'.format(base_path))
    df = df[(df['scenario'] == scenario) & (~df['alg'].isin(exclude_algs))]

    for metric in labels['graphs']:
        mod_df = df.copy()

        evs = mod_df['ev'].unique().tolist()
        algs = mod_df['alg'].unique().tolist()

        ev_order = []
        for ev in ev_order_global:
            if ev in evs:
                ev_order.append(labels['evs'][ev])
                
        algs_order = []
        for alg in algs_order_global:
            if alg in algs:
                algs_order.append(labels['algs'][alg]) 

        mod_df["ev"].replace(labels['evs'], inplace=True) 

        mod_df = mod_df[mod_df['teleported'] != True]

        if metric in ['tl','rt','imp']:
            mod_df["alg"].replace(labels['algs'], inplace=True)

            mod_df = mod_df[mod_df['alg'] != 'no-preemption'] 
   
            plot_bar(mod_df,ev_order,algs_order,metric,scenario,base_path)
            plot_boxplot(mod_df,ev_order,algs_order,metric,scenario,base_path)
        elif metric == 'ttt':
            plot_stacked(mod_df[mod_df['alg'] == 'no-preemption'],ev_order,metric,scenario,base_path)
            mod_df["alg"].replace(labels['algs'], inplace=True)
            metric = 'tl'
            plot_boxplot_nopreemption(mod_df[mod_df['alg'] == labels['algs']['no-preemption']],ev_order,[ labels['algs']['no-preemption'] ],metric,scenario,base_path)
