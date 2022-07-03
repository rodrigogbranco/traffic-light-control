import json
import os
import csv
import pandas as pd
from jsonpath_ng import jsonpath, parse

# this is the main entry point of this script
if __name__ == "__main__":
    #sce = ['od500k','od1500k']
    #sce = ['analysis']
    output_dir = '/home/rodrigo/docker-sumo-interscity-spres-ev/{}'.format('results-turin')
    #output_dir = '/home/rodrigo/docker-sumo-interscity-spres-ev/{}'.format('interscity-results')
    sce = ['turin']

    results = {}

    csvdata = {'scenario': [], 'ev' : [], 'alg': [], 'metric' : [], 'seed' : [], 'value' : []}

    for i in sce:
        #sce_dir = 'od{}k'.format(i)
        #sce_dir = 'od{}'.format(i)
        sce_dir = '{}'.format(i)

        results[sce_dir] = {}

        base_path = '/home/rodrigo/{0}/{0}-1/results/staticdynamic'.format(sce_dir)
        #print(os.listdir(base_path))

        for r in os.listdir(base_path):
            params = r.split('!')
            ev = params[1].split('_')[0]
            seed = params[2].split('_')[0]
            alg = params[3].split('.json')[0].split('_')[0]            

            if ev not in results[sce_dir]:
                results[sce_dir][ev] = {}

            if alg not in results[sce_dir][ev]:
                results[sce_dir][ev][alg] = {}

            if 'rt' not in results[sce_dir][ev][alg]:
                results[sce_dir][ev][alg]['rt'] = {}

            if 'tl' not in results[sce_dir][ev][alg]:
                results[sce_dir][ev][alg]['tl'] = {}

            if 'ttt' not in results[sce_dir][ev][alg]:
                results[sce_dir][ev][alg]['ttt'] = {}

            #if 'timeloss_affected' not in results[sce_dir][ev][alg]:
            #    results[sce_dir][ev][alg]['timeloss_affected'] = {}

            tmp = open('{}/{}'.format(base_path,r),'r')
            data = json.loads(tmp.read())
            tmp.close()                   

            vehs_data = parse('$.vehs').find(data)[0].value                      

            results[sce_dir][ev][alg]['tl'][seed] = vehs_data[ev][2]
            results[sce_dir][ev][alg]['rt'][seed] = parse('$.param[2]').find(data)[0].value
            results[sce_dir][ev][alg]['ttt'][seed] = vehs_data[ev][1]

            for metric in ['tl','rt','ttt']:
                csvdata['scenario'].append(i)
                csvdata['ev'].append(ev)
                csvdata['alg'].append(alg)
                csvdata['seed'].append(seed)
                csvdata['metric'].append(metric)
                csvdata['value'].append(results[sce_dir][ev][alg][metric][seed])
            
            #affected_vehs = parse('$.affected').find(data)[0].value

            #for veh in affected_vehs:
            #    if veh in vehs_data:
            #        results[sce_dir][ev][alg]['timeloss_affected'][veh] = vehs_data[veh][2]

            data = None
            print('{}/{}'.format(base_path,r))
            
    #print(results)

    df = pd.DataFrame(csvdata)

    df_other = df[(df['metric'] == 'tl') & (df['alg'] != 'no-preemption')]

    tl_imp = []

    for index, row in df_other.iterrows():
        df_nopreempt = df[(df['metric'] == 'tl') & (df['alg'] == 'no-preemption') & (df['scenario'] == row.scenario) & (df['ev'] == row.ev) & (df['seed'] == row.seed)]

        if not df_nopreempt.empty:
            improvement = (1-float(row.value)/float(df_nopreempt['value'].iloc[0]))*100
            tl_imp.append([row.scenario, row.ev, row.alg, 'imp', row.seed, improvement])

    df = df.append(pd.DataFrame(tl_imp, columns=['scenario', 'ev', 'alg', 'metric', 'seed', 'value']), ignore_index=True)

    df.to_csv('{}/summary.csv'.format(output_dir),index=False)

    tmp = open('{}/summary.json'.format(output_dir),'w+')
    tmp.write(json.dumps(results))
    tmp.close() 