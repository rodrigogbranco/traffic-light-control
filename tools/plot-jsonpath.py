import json
import os
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

sns.set_theme(style="ticks", color_codes=True)

scenarios = {
    'od500k' : 'Origin/Destination Survey - 500K vehicles',
    'od1500k' : 'Origin/Destination Survey - 1.5M vehicles',
    'odanalysis' : 'EV2 with splitted route',
    'turin' : 'Turin - TuSTScenario',
} 

def plot_graph(labels,means,errors,g,i):
    x_pos = np.arange(len(labels))
    width = 0.17
    #widths = [-(2*width),-width,0,width,+(2*width)]
    widths = [-width,0,+width]

    #hatches = ['/','\\', 'o', 'x', '-']
    hatches = ['/','\\', 'o']

    fig, ax = plt.subplots()

    rects = []

    step = 0
    for alg in algs_order:
        if alg not in ['tl','eff']:
            rects.append(ax.bar(x_pos + widths[step], means[alg], yerr=errors[alg], alpha=0.5, width=width, label=algs[alg], align='center', ecolor='black', capsize=10, hatch=hatches[step]))
            step += 1

    ax.set_ylabel(g['ylabel'])
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels)
    ax.set_xlabel(g['xlabel'])
    ax.set_title(g['title'].format(scenarios[i]))
    ax.yaxis.grid(True)
    ax.legend()

    plt.tight_layout()
    plt.savefig(g['figpath'].format(base_path,i))
    plt.close()
    #plt.show()
    print('{} generated'.format(g['figpath'].format(base_path,i)))

def plot_boxplot(labels,raw,g,i):

    algdata = []
    labeldata = []

    length = 0

    for ev in raw:
        evdata = []
        for alg in algs:
            evdata += raw[ev][alg]
            length = len(raw[ev][alg])
        algdata.append(evdata)

    for alg in algs:
        labeldata += [algs[alg] for i in range(0,length)]

    df = pd.DataFrame(np.array(algdata).transpose(), columns=labels)

    df["X"] = pd.Series(labeldata)

    plt.figure()

    bps = df.boxplot(by="X",patch_artist = True, medianprops = dict(linestyle='-.', linewidth=1.5), color={'medians': 'red'}, sym="r+")

    if isinstance(bps, list):
        for bp in bps:
            bp[0].set_ylabel(g['ylabel'])
            bp[0].set_xlabel('')
    else:
        bps.set_ylabel(g['ylabel'])
        bps.set_xlabel('')        
    #bp.set_title() 

    colors = ['tab:blue','tab:orange','tab:green']
    hatches = ['/','\\', 'o']

    if isinstance(bps, list):
        for bp in bps:
            for c in range(0,len(colors)):
                bp[0].findobj(matplotlib.patches.Patch)[c].set_facecolor(colors[c])
                bp[0].findobj(matplotlib.patches.Patch)[c].set_hatch(hatches[c])
                bp[0].findobj(matplotlib.patches.Patch)[c].set_edgecolor('black')
                bp[0].findobj(matplotlib.patches.Patch)[c].set_alpha(0.5)
    else:
        for c in range(0,len(colors)):
            bps.findobj(matplotlib.patches.Patch)[c].set_facecolor(colors[c])
            bps.findobj(matplotlib.patches.Patch)[c].set_hatch(hatches[c])
            bps.findobj(matplotlib.patches.Patch)[c].set_edgecolor('black')
            bps.findobj(matplotlib.patches.Patch)[c].set_alpha(0.5)

    #bps.set_ylim(-70,120)

    #plt.tight_layout()
    plt.suptitle(g['title'].format(scenarios[i]))
    plt.savefig(g['boxplotpath'].format(base_path,i))
    #plt.show()
    plt.close()
    print('{} generated'.format(g['boxplotpath'].format(base_path,i)))             

def plot_ttt(labels,means,errors,g,i):
    x_pos = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar(labels, means['tl'], width, yerr=errors['tl'], label='Timeloss', alpha=0.5, align='center', ecolor='black', capsize=10, hatch='/', color='purple')
    ax.bar(labels, means['eff'], width, label='Effective Time', alpha=0.5, bottom=means['tl'], align='center', ecolor='black', capsize=10, hatch='\\', color='yellow')    

    ax.set_ylabel(g['ylabel'])
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels)
    ax.set_xlabel(g['xlabel'])
    ax.set_title(g['title'].format(scenarios[i]))
    ax.yaxis.grid(True)
    ax.legend()

    plt.tight_layout()
    plt.savefig(g['figpath'].format(base_path,i))
    #plt.show()
    plt.close()
    print('{} generated'.format(g['figpath'].format(base_path,i)))    

if __name__ == "__main__":
    #base_path = '/home/rodrigo/docker-sumo-interscity-spres-ev/interscity-results'
    base_path = '/home/rodrigo/docker-sumo-interscity-spres-ev/results-turin'

    #algs = {
    #    'kapusta': 'Kapusta',
    #    'kapusta2': 'Kapusta Original',
    #    'allgreen': 'All Green',
    #    'tpn' : 'TPN',
    #    'tpn2' : 'TPN2'
    #}

    algs = {
        'kapusta2': 'Kapusta et al (2017)',
        'allgreen': 'Hyphotetical all-green',
        'tpn2' : 'TPN'
    }

    algs_order_new = ['Kapusta et al (2017)', 'TPN', 'Hyphotetical all-green']
    #ev_order = ['EV1','EV2','EV3']
    ev_order = ['EV1']

    algs_order = ['kapusta2', 'tpn2', 'allgreen'] 
    column_order = []
    for al in algs_order:
        column_order.append(algs[al])

    skip = ['kapusta', 'tpn']

    graphs = {}
    graphs['tl'] = {
        'ylabel' : 'Timeloss (s)',
        'title' : 'Timeloss  - {}',
        'figpath' : '{}/timeloss-{}.png',
        'boxplotpath' : '{}/timeloss-boxplot-{}.png',
        'xlabel' : 'Emergency Vehicles'
    }

    graphs['rt'] = {
        'ylabel' : 'Runtime (s)',
        'title' : 'Runtime  - {}',
        'figpath' : '{}/runtime-{}.png',
        'boxplotpath' : '{}/runtime-boxplot-{}.png',
        'xlabel' : 'Emergency Vehicles'
    }  

    graphs['imp'] = {
        'ylabel' : 'Time-Loss Improvement (%)',
        'title' : '{}',
        'figpath' : '{}/improvement-{}.png',
        'boxplotpath' : '{}/improvement-boxplot-{}.png',
        'xlabel' : 'Emergency Vehicles'
    }

    graphs['ttt'] = {
        'ylabel' : 'Total Time (s)',
        'title' : 'No Preemption - {}',
        'figpath' : '{}/totaltime-{}.png',
        'boxplotpath' : '{}/totaltime-boxplot-{}.png',
        'xlabel' : 'Emergency Vehicles'
    }

    #graphs['timeloss_affected'] = {
    #    'ylabel' : 'Improvement (%)',
    #    'title' : 'Improvement  - Scenario {}',
    #    'figpath' : '{}/improvement-{}.png',
    #    'xlabel' : 'Emergency Vehicle'        
    #}     

    #tmp = open('{}/summary.json'.format(base_path),'r')
    #results = json.loads(tmp.read())
    #tmp.close()

    df = pd.read_csv('{}/summary.csv'.format(base_path))
    #df["ev"].replace({"vehev1": "EV1", "vehev2": "EV2", "vehev3": "EV3"}, inplace=True)
    df["ev"].replace({"vehev1": "EV1"}, inplace=True)
    df["alg"].replace({"kapusta2": algs['kapusta2'], 'tpn2': algs['tpn2'], 'allgreen': algs['allgreen']}, inplace=True)

    df_tli = df[(df['metric'] == 'imp') & (df['scenario'] == 'turin') & (~df['alg'].isin(['tpn','kapusta']))]
    #g = sns.catplot(x="ev", y="value", hue="alg", kind="bar", data=df_tli, capsize=0.1, hue_order=algs_order_new, order=ev_order)
    #hatches = ['\\', '*', 'o']

    #count = 0
    #for k,thisbar in enumerate(g.ax.patches):
    #    count += 1 if k % 3 == 0 else 0
    #    thisbar.set_hatch(hatches[count - 1])  

    #g.set_axis_labels("Emergency Vehicles", "Time-Loss Improvement (%)")

    #g.ax.set_title('Origin/Destination Survey - 1.5M vehicles')


    ax = sns.boxplot(x="ev", y="value", hue="alg", data=df_tli, hue_order=algs_order_new, order=ev_order)

    hatches = ['\\', '*', 'o']

    count = 0
    for patch in ax.artists:
        patch.set_hatch(hatches[count % len(hatches)])
        count += 1  

    #ax.set_title('Origin/Destination Survey - 500K vehicles')
    ax.set_title('Turin - TuSTScenario')

    ax.set_ylabel('Time-Loss Improvement (%)')
    ax.set_xlabel('Emergency Vehicles')

    plt.grid()
    plt.savefig('/home/rodrigo/tmp.png')
    plt.close()    

    sys.exit(0)

    for g in graphs:
        for i in results:
            #if i == 'od1500k':
            #    continue

            #labels = ['vehev1', 'vehev2', 'vehev3']
            #vehs_labels = ['EV1', 'EV2', 'EV3']

            #labels = ['vehev4', 'vehev5', 'vehev6', 'vehev7']
            #vehs_labels = ['O -> BB', 'O -> AB', 'BB -> D', 'AB -> D']

            labels = ['vehev1']
            vehs_labels = ['EV']


            #labels = ['vehev4', 'vehev5', 'vehev6', 'vehev7','vehev8','vehev9', 'vehev10', 'vehev11']
            means = {}
            errors = {}
            raw = {}

            means['tl'] = []
            means['eff'] = []
            errors['tl'] = []
            errors['eff'] = []  

            for ev in labels:
                result_alg = {}
                raw[ev] = {}    

                for alg in results[i][ev]:
                    if alg != 'no-preemption' and g != 'ttt':

                        if alg in skip:
                            continue

                        if alg not in means:
                            means[alg] = []
                        if alg not in errors:
                            errors[alg] = []
                        if alg not in raw[ev]:
                            raw[ev][alg] = []

                        result_alg[alg] = []

                        if g == 'tl' or g == 'rt':
                            for seed in results[i][ev][alg][g]:
                                result_alg[alg].append(float(results[i][ev][alg][g][seed]))
                        elif g == 'imp':
                            for seed in results[i][ev][alg]['tl']:
                                if seed in results[i][ev]['no-preemption']['tl'] and seed in results[i][ev][alg]['tl']:
                                    before = float(results[i][ev]['no-preemption']['tl'][seed])
                                    after = float(results[i][ev][alg]['tl'][seed])
                                    result_alg[alg].append((1-after/before)*100)
                        #PAREI AQUI

                        means[alg].append(np.mean(np.array(result_alg[alg])))
                        errors[alg].append(means[alg][-1] - sms.DescrStatsW(result_alg[alg]).tconfint_mean()[0])
                        raw[ev][alg] = result_alg[alg]                       
                    elif alg == 'no-preemption' and g == 'ttt':
                        result_alg['tl'] = []
                        result_alg['eff'] = [] 

                        for seed in results[i][ev][alg]['tl']:
                            tl = float(results[i][ev]['no-preemption']['tl'][seed])
                            ttt = float(results[i][ev]['no-preemption']['ttt'][seed])

                            result_alg['tl'].append(tl)
                            result_alg['eff'].append(ttt-tl)

                        means['tl'].append(np.mean(np.array(result_alg['tl'])))
                        errors['tl'].append(means['tl'][-1] - sms.DescrStatsW(result_alg['tl']).tconfint_mean()[0])                                 

                        means['eff'].append(np.mean(np.array(result_alg['eff'])))                                                  

            if g != 'ttt':
                plot_graph(vehs_labels,means,errors,graphs[g],i)
                plot_boxplot(vehs_labels,raw,graphs[g],i)
            else:
                plot_ttt(vehs_labels,means,errors,graphs[g],i)
