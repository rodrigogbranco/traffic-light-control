import math
import numpy as np
import matplotlib.pyplot as plt

cycle_time = [60,90,120]

tflush = 5
veh_length = 1/4.3
k = 0.149129457
s = 0.444444444
vvec = [50,75,100]
a = 2.6

Q_length = [0,50,100,150,200,250,300]

def plot_graph(qlength,v,gl,xlabel,selector):
    fig, ax = plt.subplots()

    dashes = [[2, 2, 10, 2],[6, 2],[1, 1, 10, 1],[2, 4, 15, 4],[3,3,6,3],[8,10]]

    step = 0
    for j in v:
        for i in v[j]:
            line = ax.plot(qlength, v[j][i][selector], label=v[j][i]['label'], dashes=dashes[step])
            step += 1

    if selector == 'flow':
        sf = []
        for q in qlength:
            sf.append(s)
        line = ax.plot(qlength, sf, label='Saturation Flow')
        
    ax.legend()
    ax.set_ylabel('{} ({})'.format(gl[selector]['ylabel'],gl[selector]['yunit']))
    ax.set_xlabel(xlabel)
    ax.set_title(gl[selector]['ylabel'])
    ax.yaxis.grid(True)

    plt.tight_layout()
    plt.savefig('/home/rodrigo/docker-sumo-interscity-spres-ev/{}.png'.format(gl[selector]['pngname']))
    #plt.show()
    plt.close()

alg = ['kapusta','tpn']
xlabel = 'Queue Length (m)'

graphlabels = {
    'spare' : {
        'ylabel' : 'Spare Time',
        'yunit' : 's',
        'pngname' : 'spare'
    },
    'flow' : {
        'ylabel' : 'Flow',
        'yunit' : 'veh/s',
        'pngname' : 'flow'
    }
}

values = {}

#header=[]
for j in alg:
    values[j] = {}
    for i in range(0,len(vvec)):
        values[j][i] = {}
        if j == 'kapusta':
            #header.append('{}:v={}km/h,ct={}s '.format(j,vvec[i],cycle_time[i]))
            values[j][i]['label'] = '{}:v={}km/h,ct={}s '.format(j,vvec[i],cycle_time[i])
        else:
            #header.append('{}:v{}km/h'.format(j,vvec[i]))
            values[j][i]['label'] = '{}:v{}km/h'.format(j,vvec[i])
        values[j][i]['spare'] = []
        values[j][i]['flow'] = []


#print('  {} {} {} {} {} {}'
#            .format(header[0],header[1],header[2],header[3],header[4],header[5]))

#spare = open('/home/rodrigo/spare.dat','w')
#flow = open('/home/rodrigo/flow.dat','w')

for Q in Q_length:
    #values = []
    #values2 = []
    for j in alg:
        for i in range(0,len(vvec)):
            v = vvec[i]/3.6
            Q_a = v*v/(2*a)
            t_queue = (Q*k)/s
            activation = cycle_time[i]/2
            if Q < Q_a:
                t_last = math.sqrt((2*Q)/a)
            else:
                t_last = v/a + (Q - (v*v)/(2*a))/v

            if j == 'kapusta':
                wasted_time = activation - tflush - t_queue - t_last
                t_effective = activation - tflush
            elif j == 'tpn':
                wasted_time = (tflush + t_queue + t_last)/2
                t_effective = (tflush + t_queue + t_last)*1.5

            deltaq2 = (2*a*s*v*t_effective - s*v*v)/(2*a*(k*v+s)) - Q
            deltaq1 = 0        

            insideroot = 2*a*k*t_effective*math.pow(s,3) + math.pow(s,4)
            if insideroot >= 0:
                rootpart = math.sqrt(insideroot)
                lastpart = (s*s)/a -Q*k*k + k*s*t_effective

                deltaq1 = max((-rootpart+lastpart)/(k*k),(+rootpart+lastpart)/(k*k))

            if deltaq1 > 0 and Q + deltaq1 <= (v*v)/(2*a):
                deltaq = deltaq1
            else:
                deltaq = deltaq2

            values[j][i]['spare'].append(wasted_time)
            values[j][i]['flow'].append((deltaq*veh_length)/t_effective)

            #values.append(wasted_time)
            #values2.append((deltaq*k)/t_effective)

    #spare.write('{} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f}\n'
    #        .format(Q,values[0],values[1],values[2],values[3],values[4],values[5]))

    #flow.write('{} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f}\n'
    #        .format(Q,values2[0],values2[1],values2[2],values2[3],values2[4],values2[5]))

#spare.close()
#flow.close()                        

    #print(Q)
    #print('{} {:.2f} {:.2f} {:.2f}'.format(Q,wasted_time,deltaq,(deltaq*k)/t_effective))




plot_graph(Q_length,values,graphlabels,xlabel,'spare')
plot_graph(Q_length,values,graphlabels,xlabel,'flow')
