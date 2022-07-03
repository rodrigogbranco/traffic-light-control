from .logger import Logger

import math
import copy

class BaseOrchestrator:
    def __init__(self, mw):
        self.logger = Logger(self.__class__.__name__).get()
        self.commands = {}
        self.restore_tls = {}
        self.mw = mw
        self.tls_to_sync = {}
        self.tls_active_time = {}
        self.active_tls = set()

        self.active_evs_by_tl = {}         

    def open_tl_at_time_by_cycles(self,ev,cycle_quantity,edge_id,t,conf,infinity):
        self.logger.debug('when '+str(t))

        t_key = int(math.floor(t)+1)

        if t_key not in self.commands:
            self.commands[t_key] = {}

        self.commands[t_key][edge_id] = {}

        self.commands[t_key][edge_id]['ev'] = ev
        self.commands[t_key][edge_id]['conf'] = conf
        self.commands[t_key][edge_id]['infinity'] = infinity
        self.commands[t_key][edge_id]['cycles'] = cycle_quantity
        self.commands[t_key][edge_id]['start'] = int(self.mw.get_time())
        self.commands[t_key][edge_id]['color'] = 'y'
        self.commands[t_key][edge_id]['duration'] = -1

        if edge_id not in self.active_evs_by_tl:
            self.active_evs_by_tl[edge_id] = set()

        self.active_evs_by_tl[edge_id].add(ev)

    def open_tl_at_time_by_cycles_by_time(self,ev,cycle_quantity,edge_id,t,conf,duration):
        self.open_tl_at_time_by_cycles(ev,cycle_quantity,edge_id,t,conf,False)

        t_key = int(math.floor(t)+1)

        if t_key not in self.commands:
            self.commands[t_key] = {}

        self.commands[t_key][edge_id]['duration'] = duration

        if edge_id not in self.active_evs_by_tl:
            self.active_evs_by_tl[edge_id] = set()

        self.active_evs_by_tl[edge_id].add(ev)        

    def finish(self, ev):
        pass

    def execute_before_step_simulation(self,step):
        to_remove = []
        for tl in self.active_tls:
            if self.tls_active_time[tl][-1] == step:
                to_remove.append(tl)

        for tl in to_remove:
            self.active_tls.remove(tl)

        del_restore = []
        for tl in self.restore_tls:
            phase = int(self.mw.get_phase_of_tl(tl))
            self.logger.debug('to restore: tl '+str(tl)+' current phase: '+str(phase))
            self.logger.debug('lights now: '+str(self.mw.get_rgb_state(tl)))
            self.logger.debug('next switch: '+str(self.mw.get_next_switch_of_tl(tl)))

            if step >= self.restore_tls[tl]['after']:
                nswitch = int(self.mw.get_next_switch_of_tl(tl)) - step
                backup_program = self.restore_tls[tl]['program']
                self.mw.set_complete_definition_of_tl(tl,backup_program)
                self.mw.set_program_of_tl(tl,'0')
                self.mw.set_phase_of_tl(tl,phase)
                self.mw.set_phase_duration_of_tl(tl,nswitch)
                del_restore.append(tl)          

        for d in del_restore:
            del self.restore_tls[d]

        if len(self.commands) > 0 and step in self.commands:
            for edge in self.commands[step]:
                self.actuate(step, edge)
                tlname = self.commands[step][edge]['conf'].edges[edge]['tl']['name']
                self.active_tls.add(tlname)
                if tlname not in self.tls_active_time:
                    self.tls_active_time[tlname] = []
                    #time in future
                elif len(self.tls_active_time[tlname]) > 0 and self.tls_active_time[tlname][-1] > step:
                    self.tls_active_time[tlname][-1] = step

                cur_command = self.commands[step][edge]

                #print(tlname)                    
                #print(self.tls_active_time[tlname])
                
                if len(self.tls_active_time[tlname]) > 0 and self.tls_active_time[tlname][-1] == -1:
                    self.tls_active_time[tlname][-1] = step

                self.tls_active_time[tlname].append(step)

                if not cur_command['infinity']:
                    if cur_command['duration'] != -1:
                        self.tls_active_time[tlname].append(int(step + cur_command['duration']))
                    else:
                        until_now = int(self.mw.get_time()) - cur_command['start']
                        total_time = int(cur_command['cycles']*cur_command['conf'].edges[edge]['tl']['g']['duration'])
                        self.tls_active_time[tlname].append(int(step + total_time - until_now))
                elif cur_command['infinity'] and len(self.tls_active_time[tlname]) % 2 != 0:
                    self.tls_active_time[tlname].append(-1)

                #print(tlname)                    
                #print(self.tls_active_time[tlname])                    


            del self.commands[step]

        self.sync_tls(step)

    def actuate(self,step, edge):
        command = self.commands[step][edge]
        conf = command['conf']
        infinity = command['infinity']
        tl = conf.edges[edge]['tl']['name']
        if command['color'] == 'y':
            self.logger.info("current phase of "+str(tl)+": "+str(self.mw.get_phase_of_tl(tl)))

            lights = self.mw.get_rgb_state(tl)
            if lights.lower().count('r') == len(lights):
                self.mw.set_phase_of_tl(tl,conf.edges[edge]['tl']['g']['index'])
                if infinity:
                    self.mw.set_phase_duration_of_tl(tl,1000000)
                return

            my_green_phase = False

            if self.mw.get_phase_of_tl(tl) == conf.edges[edge]['tl']['g']['index']:
                my_green_phase = True
                if infinity:
                    self.mw.set_phase_of_tl(tl,conf.edges[edge]['tl']['g']['index'])
                    self.mw.set_phase_duration_of_tl(tl,1000000)
                return

            if not my_green_phase:
                self.change_y_phase(lights, tl, conf.edges[edge]['tl'], step)

            next_switch = int(self.mw.get_next_switch_of_tl(tl))

            cycles = command['cycles']
            red_phase_duration = int(conf.edges[edge]['tl']['r']['duration'])
            green_phase_duration = int(conf.edges[edge]['tl']['g']['duration'])

            if not my_green_phase:
                next_times = next_switch+red_phase_duration
            else:
                next_times = next_switch

            for c in range(1,int(cycles)+1):
                if next_times not in self.commands:
                    self.commands[next_times] = {}

                if edge not in self.commands[next_times]:
                    self.commands[next_times][edge] = {}

                self.commands[next_times][edge]['color'] = 'g'
                self.commands[next_times][edge]['ev'] = command['ev']
                self.commands[next_times][edge]['conf'] = command['conf']
                self.commands[next_times][edge]['infinity'] = command['infinity']
                self.commands[next_times][edge]['cycles'] = command['cycles']
                self.commands[next_times][edge]['start'] = command['start']
                self.commands[next_times][edge]['duration'] = command['duration']

                next_times = next_times + green_phase_duration
        else:
            self.logger.debug(tl+' '+ str(conf.edges[edge]['tl'][command['color']]['index']))
            self.logger.debug(self.mw.get_complete_definition_of_tl(tl))
            self.mw.set_phase_of_tl(tl,conf.edges[edge]['tl'][command['color']]['index'])
            if infinity:
                self.mw.set_phase_duration_of_tl(tl,1000000)
            elif command['duration'] != -1:
                self.mw.set_phase_duration_of_tl(tl,command['duration'])

    def sync_tls(self, step):

        remove_from_sm = []

        for edge_to_sync in self.tls_to_sync:
            data = self.tls_to_sync[edge_to_sync]
            tl_info_removed = data['conf'].edges[edge_to_sync]['tl']
            tl_name = tl_info_removed['name']

            time_in_program = step%float(tl_info_removed['ps_duration'][-1])
            total_phases = len(tl_info_removed['ps_duration'])
            self.logger.debug('time in program: '+str(time_in_program))

            real_index = 0
            while tl_info_removed['ps_duration'][real_index] < time_in_program:
                real_index = real_index + 1


            # check color state
            data['state'] = self.change_state(data['state'], tl_name, \
		                                                    real_index, edge_to_sync, remove_from_sm, total_phases, \
		                                                    tl_info_removed, time_in_program, step, data['infinity'])

        for edge in remove_from_sm:
            data = self.tls_to_sync[edge]
            del self.tls_to_sync[edge]
            tl = data['conf'].edges[edge]['tl']['name']
            if tl in self.active_tls:
                self.active_tls.remove(tl)

                if len(self.tls_active_time[tl]) > 0 and \
                    (self.tls_active_time[tl][-1] == -1 or \
                        (len(self.tls_active_time[tl]) % 2 == 0 and 
                        self.tls_active_time[tl][-1] > step)):
                    self.tls_active_time[tl][-1] = step
                else:
                    self.tls_active_time[tl].append(step)

            if data['infinity']:
                steps = [s for s in self.commands if edge in self.commands[s]]
                for s in steps:
                    del self.commands[s][edge]

    def change_state(self, state, tl_name, real_index, obj_to_sync, remove_from_sm, total_phases, tl_info_removed, time_in_program, step, infinity):
        current_light, real_light = self.get_colors(tl_name, tl_info_removed, real_index)
        current_index = self.mw.get_phase_of_tl(tl_name)
        current_time_left = int(self.mw.get_next_switch_of_tl(tl_name)) - step
        real_time_left = tl_info_removed['ps_duration'][real_index] - time_in_program

        if state == 1:
            if current_light == 'r':
                if real_light in ['r','g']:
                    # L1 = R and L2 in (R,G) noqa
                    self.mw.set_phase_of_tl(tl_name,real_index)
                    self.mw.set_phase_duration_of_tl(tl_name,real_time_left)
                    remove_from_sm.append(obj_to_sync)
                    return 0
                else:
                    # L1 = R and L2 = Y noqa
                    self.mw.set_phase_of_tl(tl_name,(real_index+1)%total_phases)
                    if infinity:
                        current_time_left = 0
                    self.mw.set_phase_duration_of_tl(tl_name,current_time_left+self.mw.get_phase_duration_of_tl(tl_name))
                    remove_from_sm.append(obj_to_sync)
                    return 0
            elif current_light == 'y':
                # L1 = Y noqa
                return 8
            elif current_light == 'g':
                next_green_light = (real_index+1)%total_phases
                time_to_check = real_time_left
                if real_light == 'y':
                    time_to_check = time_to_check + tl_info_removed['durations'][(real_index+1)%total_phases]              
                    next_green_light = (next_green_light+1)%total_phases

                if current_index == real_index:
                    # L1 = G and L1 = L2 noqa
                    self.mw.set_phase_duration_of_tl(tl_name,real_time_left)
                    remove_from_sm.append(obj_to_sync)
                    return 0
                elif real_light in ['r','y'] and next_green_light == current_index and current_time_left >= time_to_check:
                    # L1 = G and L2 in (R,Y) and next(G,L2) = L1 and (timeLeft(L1) >= timeLeft(L2) + duration(next(R,L2)) if L2 = Y or timeLeft(L2))
                    green_phase_duration = tl_info_removed['durations'][current_index]
                    self.mw.set_phase_of_tl(tl_name,current_index)
                    self.mw.set_phase_duration_of_tl(tl_name,green_phase_duration+time_to_check)
                    remove_from_sm.append(obj_to_sync)
                    return 0
                else:
                    # L1 = G and L2 doesn't matter now
                    lights = self.mw.get_rgb_state(tl_name)
                    self.change_y_phase(lights, tl_name, tl_info_removed, step)
                    return 8
        elif state == 8:
            if not infinity and int(self.mw.get_next_switch_of_tl(tl_name)) - step <= 1:
                return 1
            elif current_light == 'r':
                return 1
            else:
                return 8

    def change_y_phase(self, lights, tl, tl_info, step):
        had_green = False
        first_light = lights

        while 'g' in lights or 'G' in lights:
            had_green = True
            next_phase = (self.mw.get_phase_of_tl(tl) + 1) % len(tl_info['phases'])
            self.mw.set_phase_of_tl(tl,next_phase)
            lights = self.mw.get_rgb_state(tl)

        if had_green:
            new_lights = []
            for char in first_light:
                if 'g' == char or 'G' == char:
                    new_lights.append('y')
                else:
                    new_lights.append(char)

            new_lights = "".join(new_lights)

            if lights != new_lights:
                if not tl in self.restore_tls:
                    self.restore_tls[tl] = {}

                self.restore_tls[tl]['after'] = int(self.mw.get_next_switch_of_tl(tl))
                self.restore_tls[tl]['lights'] = lights
                self.restore_tls[tl]['phase'] = next_phase
                nswitch = int(self.mw.get_next_switch_of_tl(tl)) - step          
                program = self.mw.get_complete_definition_of_tl(tl)[0]
                self.restore_tls[tl]['program'] = program
                new_program = copy.deepcopy(program)
                self.restore_tls[tl]['total_phases'] = len(new_program.phases)

                self.logger.debug(new_program)

                new_program.phases[next_phase].state = new_lights
                self.mw.set_complete_definition_of_tl(tl,new_program)
                self.logger.debug('installed program: '+str(self.mw.get_complete_definition_of_tl(tl)))
                self.mw.set_program_of_tl(tl,'0')
                self.mw.set_phase_of_tl(tl,next_phase)
                self.mw.set_phase_duration_of_tl(tl,nswitch)
                self.logger.debug('was toggled')                                                                                                                            


    def get_colors(self,tl_current, tl_info, index):
        current_lights = self.mw.get_rgb_state(tl_current)
        if 'g' in current_lights.lower():
            current_light = 'g'
        elif 'y' in current_lights.lower():
            current_light = 'y'
        else:
            current_light = 'r'

        real_lights = tl_info['phases'][index]
        if 'g' in real_lights.lower():
            real_light = 'g'
        elif 'y' in real_lights.lower():
            real_light = 'y'
        else:
            real_light = 'r'

        return current_light, real_light

    def schedule_sync(self,ev,edge,conf,infinity):
        self.tls_to_sync[edge] = {}
        self.tls_to_sync[edge]['state'] = 1
        self.tls_to_sync[edge]['ev'] = ev
        self.tls_to_sync[edge]['conf'] = conf
        self.tls_to_sync[edge]['infinity'] = infinity

        if edge in self.active_evs_by_tl and ev in self.active_evs_by_tl[edge]:
            self.active_evs_by_tl[edge].remove(ev)

    def set_phase_duration_of_tl(self,step,tl,time):
        if tl not in self.active_tls:
            self.active_tls.add(tl)

        if tl not in self.tls_active_time:
            self.tls_active_time[tl] = []

        if len(self.tls_active_time[tl]) == 0 or self.tls_active_time[tl][-1] < step:
            self.tls_active_time[tl].append(step)
            self.tls_active_time[tl].append(int(step + time))

        if len(self.tls_active_time[tl]) > 0 and self.tls_active_time[tl][-1] > step:
            self.tls_active_time[tl][-1] = int(step + time)

        self.mw.set_phase_duration_of_tl(tl,time)
