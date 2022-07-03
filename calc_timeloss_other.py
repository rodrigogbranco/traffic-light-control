import json

import numpy as np, scipy.stats as st

if __name__ == "__main__":
    instances = [1,5]
    algs = ['no-preemption', 'tpn_umt!False', 'tpn_umt!True']

    results = {}
    ev = 'veh11651'

    for i in instances:
        results[i] = {}
        for alg in algs:
            tmp = open('../interscity-spres-ev-scenarios/defined/sp/sp-{}/results/staticdynamic/evs!{}_seed!12811_alg!{}.json'.format(i,ev,alg))
            results[i][alg] = json.loads(tmp.read())
            #print(results[i][alg])
            tmp.close()

    for i in results:
        for alg in results[i]:
            if alg != 'no-preemption':
                r = results[i][alg]
                rno = results[i]['no-preemption']

                rset = {}
                for t in r['timeloss_all_ev']:
                    rset[t[0]] = t[1]

                rnoset = {}
                for t in rno['timeloss_all_ev']:
                    rnoset[t[0]] = t[1]                    

                vehs = r['evs'][ev]['affected_vehs']


                results[i][alg]['times'] = []
                for veh in vehs:
                    results[i][alg]['times'].append(1 - (float(rset[veh])/float(rnoset[veh])))

                interval = 0
                mean = 0

                if len(results[i][alg]['times']) > 0:
                    interval = st.t.interval(0.95, len(results[i][alg]['times'])-1, loc=np.mean(results[i][alg]['times']), scale=st.sem(results[i][alg]['times']))[0]
                    mean = np.mean(results[i][alg]['times'])                    

                print('scenario:SP-{} alg:{} n:{} timeloss affected:{:.2f}% +/- {:.2f}%'.format(i,alg,len(results[i][alg]['times']),mean*100,interval*100))