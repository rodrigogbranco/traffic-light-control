from classes.preemption_strategy import PreemptionStrategy

class AllGreenStrategy(PreemptionStrategy):
    #constants: Marshall, P.S. and W.D. Berg, Design Guidelines for Railroad Preemption at Signalized Intersections. Institute of Transportation Engineers Journal, 1997.
    def configure(self):
        self.infinity = True
        self.started = False
        self.restored = False

    def execute_step(self,step,ev_entered_in_simulation,in_simulation):
        super().execute_step(step,ev_entered_in_simulation,in_simulation)
        #self.sync_tls(step)

        if self.ev_entered and not self.ev_exited:
            if not self.started:
                for tl in self.conf.tls:
                    self.open_tl_at_time_by_cycles(1,tl,step)

                self.started = True

        if self.ev_entered and self.ev_exited and not self.restored:
            for tl in self.conf.tls:
                self.orch.schedule_sync(self.ev,tl,self.conf,self.infinity)

            self.restored = True