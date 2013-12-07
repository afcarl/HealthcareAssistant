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
        # Optional, may start without plans
        if plans_path: self.load_plans(plans_path)

        # Should add a method for loading plans
        self.check_for_new_plans()

        # Do calculations, move to a new method that is called when a new plan is added?
        self.pc_list = self.generate_plan_conflicts()
        self.find_conflicting_effects()
        self.generate_interferences()

    @timer
    def load_plans(self, path):
        """
			Load a set of plans from the supplied path. Does not check for conflicts
		"""
        with  open(path, 'r') as data:
            raw_plans = json.load(data)

        for rp in raw_plans:
            p = Plan(raw_plans[rp], self.treatments)
            self.plans.append(p)

    @timer
    def load_treatments(self, path):

        with open(path, 'r') as data:
            raw_treatments = json.load(data)

        for rt in raw_treatments:
            t = Treatment(raw_treatments[rt])
            self.treatments[rt] = t
            for effect_name in t.effects:
                self.effect_table.setdefault(effect_name, set()).add(t)

        for name, treatment in self.treatments.iteritems():
            for possible_interference, value in treatment.interference.iteritems():
                if not value == 0:
                    self.interference_table[str(value)].add(Pair(self.treatments[possible_interference], treatment))
                    self.interference_table.setdefault(str(value),set()).add(Pair(self.treatments[possible_interference], object))

        if '-1' not in self.interference_table.keys():
            self.interference_table['-1'] = set()
        if '1' not in self.interference_table.keys():
            self.interference_table['-1'] = set()
        if '0.5' not in self.interference_table.keys():
            self.interference_table['-1'] = set()

    def check_for_new_plans(self):
        """
        finds whether there is a new plan
        """
        for plan in self.plans:
            if plan.status == "new":
                self.newplan = plan

    @timer
    def find_conflicting_effects(self):
        """
        creates plan_conflicts between two plans and generates the conflict tree for them
        """
        for pc in self.pc_list:
            zero_conflicts = set()
            for c in pc.conflicts:
                bl, wl, cl, nl = self.get_conflicts(c.body_function, c.conflicting_treatments)
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

    @timer
    def generate_plan_conflicts(self):
        """
        generates an empty plan_conflict for each pair of plans in a set of plans
        """
        if not self.newplan:
            plancombs = it.combinations(self.plans, 2)
        else:
            plancombs = [(plan, self.newplan) for plan in self.plans if not plan == self.newplan]
        pc_list = []
        for a in plancombs:
            pc_list.append(self.find_conflicts(a[0], a[1]))
        return pc_list

    @timer
    def find_conflicts(self, plan_a, plan_b):
        """
            Return all body functions that are affected by both plans
            Does not check if the same treatment in both plan causes it
        """
        pc = PlanConflict(plan_a, plan_b)
        conflicting_effects = set()
        for ea in plan_a.effects: # Effect A
            if ea in plan_b.effects:
                conflicting_effects.add(ea)

        for ce in conflicting_effects:
            confl_treatments = self.evaluate_conflicts([plan_a, plan_b], ce)
            dummy_conflict = Conflict(confl_treatments)
            dummy_conflict.body_function = ce
            pc.conflicts.add(dummy_conflict)

        return pc

    @timer
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

    @timer
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

    @timer
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

    @timer
    def generate_interferences(self):
        for pc in self.pc_list:
            for a in pc.plan_a.treatments:
                for b in pc.plan_b.treatments:
                    if Pair(a, b) in self.interference_table['1']:
                        pc.interferences.add(Interference(Pair(a, b), 1))
                    elif Pair(a, b) in self.interference_table['0.5']:
                        pc.interferences.add(Interference(Pair(a, b), 0.5))
                    elif Pair(a, b) in self.interference_table['-1']:
                        pc.interferences.add(Interference(Pair(a, b), -1))

    def generate_alerts(self, plan):
        print "Alerts for Doctor", plan.doctor, ":"
        for pc in self.pc_list:
            if plan == pc.plan_a or plan == pc.plan_b:
                for conf in pc.conflicts:
                    if conf.score >= .1:
                        print "   Treatments", ', '.join(str(a) for a in conf.conflicting_treatments), "cause", conf.body_function, "with a probability of", conf.score
                for conf in pc.interferences:
                    if conf.score == 1:
                        print "   Treatments", conf.conflicting_treatments.a, "and", conf.conflicting_treatments.b, "have a dangerous interaction"
        print "Warnings for Doctor", plan.doctor, ":"
        for pc in self.pc_list:
            if plan == pc.plan_a or plan == pc.plan_b:
                for conf in pc.conflicts:
                    if conf.score > .05 and conf.score < .1:
                        print "   Treatments", ', '.join(str(a) for a in conf.conflicting_treatments), "cause", conf.body_function, "with a probability of", conf.score
                for conf in pc.interferences:
                    if conf.score == 1:
                        print "   Treatments", conf.conflicting_treatments.a, "and", conf.conflicting_treatments.b, "have a slightly negative interaction"


if __name__ == '__main__':
    p = PlanSystem("data/real_treatments3.json", "data/real_plans.json")

    for plan in p.plans:
        p.generate_alerts(plan)

    #B = p.plans[0]
    #A = p.plans[1]

    #conflicting_effects = p.find_conflicts(A, B)

    # THE FOLLOWING SHOULD BE EXTRACTED INTO A METHOD

    # Simple aggregation of probabilities. It's here we must put or logic
    #print p.evaluate_conflicts_with_probs([A, B], conflicting_effects)


    #print "PLANS:", p.plans
    #print "TREATMENTS:", p.treatments

    #print p.get_conflicts(p.treatments["tegretol"], p.treatments["prednisone"], p.treatments["lisinopril"])

    #print "PLANS WITH NAUSEA EFFECT", [plan for plan in p.plans if "nausea" in plan.effects]
    # print "###############"
    #print p.effect_table["fight_seizures"]


    #print "INTERSECT", p.treatment_intersection(p.plans[0],p.plans[1])