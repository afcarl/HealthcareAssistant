import json, os, time
import itertools as it
from models import *
from util import timer

class PlanSystem():
    """
		The HealthcareAssistant system
	"""

    def __init__(self, treatments_path, plans_path=""):

        self.effect_table = {} # All treatments with a given effect
        self.treatments = {} # All known treatments
        self.plans = [] # All plans in the system
        self.interference_table = {'-1':set(), '0.5':set(), '1':set()} # MR: can only take these values?

        # Required
        self.load_treatments(treatments_path)
        # Build athe interference table. Should be  moved to its own method
        self.build_interference_table()
        # Optional, may start without plans
        # Initially loaded plans are assumed not to conflict
        # To calculate conflicts, load them one by one
        if plans_path: self.load_plans(plans_path, conflict_checking=True) # SET FALSE TO SKIP CONLFICT CHECKING

    def load_plans(self, path, conflict_checking=False):
        """
			Load a set of plans from the supplied path. Does not check for conflicts
		"""
        with  open(path, 'r') as data:
            raw_plans = json.load(data)

        for rp in raw_plans:
            p = Plan(raw_plans[rp], self.treatments)
            self.plans.append(p)

        if conflict_checking:
            pc = self.all_plan_conflicts() # potential conflicts
            self.generate_interferences(pc) # in-place
            
            # alert
            for plan in self.plans:
                self.generate_alerts(plan, pc)

    def load_treatments(self, path):
        """
            Builds a knowledge base of treatments and effects. 
            The system needs to know about all treatments in all plans that are
            submitted
        """
        with open(path, 'r') as data:
            raw_treatments = json.load(data)

        for rt in raw_treatments:
            t = Treatment(raw_treatments[rt])
            self.treatments[rt] = t
            for effect_name in t.effects:
                self.effect_table.setdefault(effect_name, set()).add(t)


        
    def build_interference_table(self):
        """
            Build an interference table from all known treatments. 
            Can only be done after all treatments are loaded.
        """
        for treatment in self.treatments.values():
            for possible_interference, value in treatment.interference.iteritems():
                if value: # not zero
                    self.interference_table[str(value)].add(frozenset([self.treatments[possible_interference], treatment]))


    def add_plan(self, path):
        with open(path, 'r') as data:
            raw_new_plan = json.load(data)

        plan = Plan(raw_new_plan.values()[0], self.treatments)
        plan.status = "unconfirmed" # Let the user confirm that he wants to add the plan after the conflicts are displayed?

        # Check for conflicts here
        pc = self.generate_plan_conflicts(plan)
        self.find_conflicting_effects(pc) # in-place
        self.generate_interferences(pc)

        # Do this only if some test passes?
        self.plans.append(plan)

        return pc

    def print_conflicts(self, pc):
        for plc in pc:
            print "***************"
            print plc
            print plc.conflicts
            print plc.interferences
            print "***************"

    def find_conflicting_effects(self, pc_list):
        """
        creates plan_conflicts between two plans and generates the conflict tree for them. 
        Modifies pc_list in-place for now.
        """
        for pc in pc_list:
            zero_conflicts = set()
            for c in pc.conflicts:
                bl, wl, cl, nl = self.get_conflicts(c.body_function, c.conflicting_treatments)

                print bl
                print wl
                print cl
                print nl

                if cl == []:
                    zero_conflicts.add(c)
                else:
                    treatments = []
                    total_prob = 0
                    for score, combo, prob in cl:
                        if len(combo) > len(treatments):
                            treatments = combo
                        total_prob+= prob
                    c.score = total_prob
                    c.conflicting_treatments = treatments
                #print c
            pc.conflicts = pc.conflicts - zero_conflicts

    def generate_plan_conflicts(self, new_plan=None):
        """
        generates an empty plan_conflict for each frozenset [of plans in a set of plans
        """
        plancombs = [(plan, new_plan) for plan in self.plans if not plan == new_plan]
        pc_list = []
        for a in plancombs:
            pc_list.append(self.find_conflicts(a[0], a[1]))
        return pc_list

    def all_plan_conflicts(self):
        """ 
            Checks all plans in the system pairwise for conflicts.
            Can be used for the systems inital load
        """
        plancombs = it.combinations(self.plans, 2)
        print list(plancombs)
        pc_list = []
        for a in plancombs:
            pc_list.append(self.find_conflicts(a[0], a[1]))
        return pc_list

    
    def find_conflicts(self, plan_a, plan_b):
        """
            Return all body functions that are affected by both plans
            Does not check if the same treatment in both plan causes it
        """

        pc = PlanConflict(plan_a, plan_b)
        conflicting_effects = set()
        for ea in plan_a.effects: # Effect A
            if ea in plan_b.effects:
                conflicting_effects.add (ea)

        for ce in conflicting_effects:
            confl_treatments = self.evaluate_conflicts([plan_a, plan_b], ce)
            dummy_conflict = Conflict(confl_treatments)
            dummy_conflict.body_function = ce
            pc.conflicts.add(dummy_conflict)

        return pc

    
    def evaluate_conflicts(self, plans, conflicting_effect):
    # CAN CHECK MORE THAN TWO PLANS
    # USING THE WHOLE EFFECT TABLE IS (MAYBE) NOT EFFICIENT
        treatments = []
        for plan in plans:
            for t in plan.treatments:
                if t in self.effect_table[conflicting_effect]:
                    treatments.append(t)
        return treatments

    def treatment_intersection(self, plan_a, plan_b):
        """
            Check if two plans use any of the same treatments
        """
        shared_treatments = set()
        for ea in plan_a.effects: # Effect A
            if ea in plan_b.effects:
                in_both = plan_a.effects[ea].intersection(plan_b.effects[ea])
        return shared_treatments

    
    def get_conflicts(self, E, treatments):
        """
        expands the whole probability tree and creates list with all conflicts, positive/negative effects and the
        probability that nothing happens
        """
        bl = [(1, [treatments[0].name], treatments[0].effects[E].better)] # better_list
        wl = [(1, [treatments[0].name], treatments[0].effects[E].worse)] # worse_list

        cl = [] #conflicts_list
        nl = treatments[0].effects[E].same #neutral_list

        for t in treatments[1:]:
            bl, wl, cl, nl = self.expand(bl, wl, cl, nl, t, E)

        bl = [a for a in bl if a[2] != 0]
        wl = [a for a in wl if a[2] != 0]
        cl = [a for a in cl if a[2] != 0]
        return bl, wl, cl, nl

    
    def expand(self, better_list, worse_list, conf_list, neutral, T, E):
        # T treatment,  E effect
        """
        expands one level of the tree
        """
        nbl = [] # new_better_list
        nwl = [] # new_worse_list
        ncl = [] # new_conflict_list

        for a in better_list:
            ncl.append((a[0] - 1, a[1] + [T.name], a[2] * T.effects[E].worse))
            nbl.append((a[0], a[1], a[2] * T.effects[E].same))
            nbl.append((a[0] + 1, a[1] + [T.name], a[2] * T.effects[E].better))

        for a in worse_list:
            nwl.append((a[0] - 1, a[1] + [T.name], a[2] * T.effects[E].worse))
            nwl.append((a[0], a[1], a[2] * T.effects[E].same))
            ncl.append((a[0] + 1, a[1] + [T.name], a[2] * T.effects[E].better))

        for a in conf_list:
            ncl.append((a[0] - 1, a[1] + [T.name], a[2] * T.effects[E].worse))
            ncl.append((a[0], a[1], a[2] * T.effects[E].same))
            ncl.append((a[0] + 1, a[1] + [T.name], a[2] * T.effects[E].better))

        new_neutral = neutral * T.effects[E].same

        return nbl, nwl, ncl, new_neutral

    def generate_interferences(self, pc_list):
        for pc in pc_list:
            for a in pc.plan_a.treatments:
                for b in pc.plan_b.treatments:
                    if frozenset([a, b]) in self.interference_table['1']:
                        pc.interferences.add(Interference(frozenset([a, b]), 1))
                    elif frozenset([a, b]) in self.interference_table['0.5']:
                        pc.interferences.add(Interference(frozenset([a, b]), 0.5))
                    elif frozenset([a, b]) in self.interference_table['-1']:
                        pc.interferences.add(Interference(frozenset([a, b]), -1))

    def generate_alerts(self, plan, pc_list):
        alerts = []
        warnings = []

        for pc in pc_list:
            if plan == pc.plan_a or plan == pc.plan_b:
                for conf in pc.conflicts:
                    if conf.score >= 0.1:
                        message = "Treatments " + ', '.join(str(a) for a in conf.conflicting_treatments) + " cause " + conf.body_function + " with a probability of " + str(conf.score)
                        alerts.append(message)
                    elif 0.05 < conf.score < 0.1:
                        message = "Treatments " + ', '.join(str(a) for a in conf.conflicting_treatments) + " cause " + conf.body_function + " with a probability of " + str(conf.score)
                        warnings.append(message)

                for conf in pc.interferences:
                    interaction = list(conf.conflicting_treatments)
                    if conf.score == 1:
                        message = " Treatments " + str(interaction[0]) + " and " + str(interaction[1]) + "have a dangerous interaction"
                        alerts.append(message)
                    elif conf.score == 0.5:
                        message = " Treatments " + str(interaction[0]) + " and " + str(interaction[1]) + "have a slightly negative interaction"
                        warnings.append(message)

        print "Alerts for Doctor", plan.doctor, ":"
        for alert in alerts:
            print alert

        print "Warnings for Doctor", plan.doctor, ":"
        for warning in warnings:
            print warning

if __name__ == '__main__':

    p_a_first = PlanSystem("data/real_treatments3.json")
    p_b_first = PlanSystem("data/real_treatments3.json")

    p = PlanSystem("data/real_treatments3.json")

    conflicts_a1 = p_a_first.add_plan("data/existing_plan.json")
    conflicts_a2 = p_a_first.add_plan("data/new_plan.json")

    conflicts_b1 = p_b_first.add_plan("data/new_plan.json")
    conflicts_b2 = p_b_first.add_plan("data/existing_plan.json")

    # Use the treatment intersection to check if two plans are almost similar?
    # Or say that names must be unique?
    # conflicts_3 = p.add_plan("data/new_plan.json")

    #print conflicts_2
    #p.print_conflicts(conflicts_1)
    #p.print_conflicts(conflicts_2)
    #p.print_conflicts(conflicts_3)

    print "--------------------------------------------------------------------"

    print "A FIRST"
    p_a_first.generate_alerts(p_a_first.plans[0], conflicts_a2)
    print "B FIRST"
    p_b_first.generate_alerts(p_b_first.plans[0], conflicts_b2)


