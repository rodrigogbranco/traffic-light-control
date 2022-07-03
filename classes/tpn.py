import snakes.plugins

from snakes import ConstraintError

@snakes.plugins.plugin("snakes.nets")
def extend (module) :
    class Transition (module.Transition) :
        def __init__ (self, name, guard=None, **args) :
            self.time = None
            self.min_time = args.pop("min_time", None)
            module.Transition.__init__(self, name, guard, **args)
        def enabled (self, binding, **args) :
            if self.min_time is None:
                return module.Transition.enabled(self, binding)
            elif self.time is None:
                return False
            else:
                return (self.min_time <= self.time) and module.Transition.enabled(self, binding)
        def update_min_time(self,new_min_time):
            self.min_time = new_min_time

    class PetriNet (module.PetriNet) :
        def time (self, step=None) :
          transactions = [trans for trans in self.transition() if trans.min_time is not None]
          for trans in transactions:
            trans.time = step
    return Transition, PetriNet