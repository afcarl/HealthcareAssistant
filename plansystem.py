import json, os, time
import itertools as it
from models import *
from util import *

class PlanSystem():
    """
		The HealthcareAssistant system
	"""
    
    def __init__(self, treatments_path, plans_path=""):

        self.effect_table = {} # All treatments with a given effect
        self.treatments = {} # All known treatments
        self.plans = [] # All plans in the system
        self.interference_table = {'-1':set(), '0.5':set(), '1':set()} # MR: can only take these values?

        # Message queue to store messages before they are displayed. 
        self.messages = [] 

        # Load the treadments database. 
        self.load_treatments(treatments_path)
        # Build the interference table.
        self.build_interference_table()

        # To calculate conflicts, load them one by one
        # TODO: FIX PROBLEM CHECKING FOR INITIAL LOAD
        if plans_path: self.add_initial_plans(plans_path, conflict_checking=True) # SET FALSE TO SKIP CONLFICT CHECKING

    
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

    
    def add_initial_plans(self, path, conflict_checking=False):
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
            self.find_conflicting_effects(pc) # in-place
            self.generate_interferences(pc)
            
            # alert
            for plan in self.plans:
                self.generate_alerts(plan, pc)
            for message in self.messages:
                print message
    
    def all_plan_conflicts(self):
        """ 
            Checks all plans in the system pairwise for conflicts.
            Can be used for the systems inital load
        """
        plancombs = it.combinations(self.plans, 2)
        pc_list = []
        for a in plancombs:
            pc_list.append(self.find_conflicts(a[0], a[1]))
        return pc_list
    
    def add_plan(self, path):
        with open(path, 'r') as data:
            raw_new_plan = json.load(data)

        new_plan = Plan(raw_new_plan.values()[0], self.treatments)
        # new_plan.status = "unconfirmed" # Let the user confirm that he wants to add the plan after the conflicts are displayed?

        intersection = {}
        for plan in self.plans:
            i = self.treatment_intersection(plan, new_plan)
            if i:
                intersection[plan] = i
        if intersection:
            print "WE HAVE INTERSECION", intersection
            for i in intersection:
                self.messages.append("The treatment(s)" + str(intersection[i]) + " is already in plan " + str(i))

        # Check for conflicts here
        pc = self.generate_plan_conflicts(new_plan)
        self.find_conflicting_effects(pc) # in-place
        self.generate_interferences(pc)

        self.generate_alerts(new_plan, pc)


        # Do this only if the user choose to continue after the alerts?
        # So print all messages here, then let the user type (y/n) to add the plan to the system
        print "###################################"
        if self.messages:
            self.print_messages()
            print "----------------------------"
            confirm = raw_input("After looking at the messages, do you still want to add " + str(new_plan) + " to the system? (y/n)")
            if confirm.lower() == "y": 
               print "Plan added:", new_plan
            self.plans.append(new_plan)
        else:
            print "Plan added:", new_plan
            self.plans.append(new_plan)
        # in that case, the order must be changed :)
        return pc
    
    def generate_plan_conflicts(self, new_plan):
        """
        generates an empty plan_conflict for each frozenset [of plans in a set of plans
        """
        plancombs = [(plan, new_plan) for plan in self.plans if not plan == new_plan]
        pc_list = []
        for a in plancombs:
            pc_list.append(self.find_conflicts(a[0], a[1]))

        return pc_list  

    
    def find_conflicting_effects(self, pc_list):
        """
        creates plan_conflicts between two plans and generates the conflict tree for them. 
        Modifies pc_list in-place for now.
        """
        for pc in pc_list: # Just one plan conflict when we have one plan and add one plan
            zero_conflicts = set()
            for c in pc.conflicts: # Does not help to sort this
                conflict_probability = self.get_conflicts(c.body_function, c.conflicting_treatments)
                c.score = conflict_probability
    
    def find_conflicts(self, plan_a, plan_b):
        """
            Return all body functions that are affected by both plans
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
    
    def evaluate_conflicts(self, plans, conflicting_effect):
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
        shared = set()
        for t in plan_a.treatments: # Effect A
            if t in plan_b.treatments:
                shared.add(t)
        return shared
    
    def get_conflicts(self, E, treatments, better=None, same=None, worse=None, conf=None, recursive_call=False):
        """
            Find the probability of two or more plans counteracting each other on one specific body function. 
            Calls itself recursively. 
        """
        if not recursive_call:
            e = treatments[0].effects[E]
            better = e.better
            same = e.same
            worse = e.worse
            conf = 0
            treatments = treatments[1:]

        if not treatments:
            return conf

        t = treatments[0]
        e = t.effects[E]

        nbetter = better*(e.better+e.same)+same*e.better # all earlier treatments better or same, and this treatment better or same
        nworse = worse*(e.same+e.worse)+same*e.worse # all earlier treatments worse or same, and this treatment worse or same
        nsame = same*e.same # all treatments so far not effecting the BF
        nconf = conf+better*e.worse+worse*e.better # this treatment opposite of the earlier

        v =  self.get_conflicts(E, treatments[1:], nbetter, nsame, nworse, nconf, True) # Recursive
        return v
    
    def generate_interferences(self, pc_list):
        for pc in pc_list:
            plans = (pc.plan_a, pc.plan_b)
            for a in pc.plan_a.treatments:
                for b in pc.plan_b.treatments:
                    pair = frozenset([a, b])
                    if pair in self.interference_table['1']:
                        pc.interferences.add(Interference(pair, 1, plans))
                    elif pair in self.interference_table['0.5']:
                        pc.interferences.add(Interference(pair, 0.5, plans))
                    elif pair in self.interference_table['-1']:
                        pc.interferences.add(Interference(pair, -1, plans))
    
    def alternative_scoring_system(self, new_plan):
        """ 
            Alternative method for scoring plans
            Give a score before and after a new plan is added.
            Not sure how this scoring can be used to generate warnings.
        """
        score = {}
        counter = {}
        for plan in self.plans:
            for treatment in plan.treatments:
                for effect in treatment.effects:
                    values = treatment.effects[effect]
                    score[effect] = score.setdefault(effect, 0) + values.better - values.worse
                    counter[effect] = counter.setdefault(effect, 0) + 1

        nscore = {} # New score, just for the new plan
        ncounter = {}
        for treatment in new_plan.treatments:
            for effect in treatment.effects:
                    values = treatment.effects[effect]
                    nscore[effect] = nscore.setdefault(effect, 0) + values.better - values.worse
                    ncounter[effect] = ncounter.setdefault(effect, 0) + 1

        return nscore

        for k in score:
            print k
            print score[k], counter[k], nscore.setdefault(k,0), ncounter.setdefault(k,0)
            print "OLD SCORE", score[k]/float(counter[k])
            print "NEW SCORE", (score[k] + nscore.setdefault(k, 0))/float(counter[k] + ncounter.setdefault(k, 0))

    
    def generate_alerts(self, plan, pc_list):
        alerts = []
        warnings = []

        opposite_msg = "The treatments %(treatments)s will have opposite effects on %(body_function)s with probability of %(score)f"
        interaction_msg= "The treatments %(t1)s and %(t2)s have a %(level)s interaction"
        msg_args = {}

        for pc in pc_list:
            if plan == pc.plan_a or plan == pc.plan_b:
                for conf in pc.conflicts:
                    msg_args["body_function"] = conf.body_function
                    msg_args["score"] = conf.score
                    msg_args["treatments"] = ', '.join([str(a) for a in conf.conflicting_treatments])

                    message = opposite_msg % msg_args
                    if conf.score >= 0.1:
                        alerts.append(message)
                    elif 0.05 < conf.score < 0.1:
                        warnings.append(message)

                # To get the messages in the desired order
                for conf in pc.interferences:
                    interaction = list(conf.conflicting_treatments)

                    msg_args["t1"] = str(interaction[0])
                    msg_args["t2"] = str(interaction[1])
                    msg_args["level"] = "dangerous"


                    if conf.score == 1:
                        msg_args["level"] = "dangerous"
                        alerts.append(interaction_msg % msg_args)
                    elif conf.score == 0.5:
                        msg_args["level"] = "slightly negative"
                        warnings.append(interaction_msg % msg_args)

        if alerts:
            self.messages.append("--------------------")
            self.messages.append("Alerts for Doctor " + str(plan.doctor) +  ":")
            self.messages.append("--------------------")
            for alert in alerts:
                self.messages.append(alert)

        if warnings:
            self.messages.append("--------------------")
            self.messages.append("Warnings for Doctor " + str(plan.doctor) +  ":")
            self.messages.append("--------------------")
            for warning in warnings:
                self.messages.append(warning)

        # for message in self.messages: print messages
    
    def print_messages(self):
        for message in self.messages:
            print message
        self.messages = []

if __name__ == '__main__':

    #print "Add all plans at once, and send messages to everyone"
    #p = PlanSystem("data/treatments.json", "data/real_plans.json")

    ### EXAMPLE 1 IN THE PAPER ####
    p1 = PlanSystem("data/treatments.json")
    p1.add_plan("data/existing_plan.json")
    p1.add_plan("data/new_plan.json")
    ### END EXAMPLE 1 ###

    # p_b_first = PlanSystem("data/treatments.json")

    #p = PlanSystem("data/treatments.json", "data/real_plans.json")

    #print p.evaluate_conflicts([p.plans[0], p.plans[1]], "nausea")
    #print p.evaluate_conflicts([p.plans[1], p.plans[0]], "nausea")

    # t = time.clock()
    # for i in range(100):
    #     conflicts_a1 = p_a_first.add_plan("data/new_plan.json")
    # print "TIMER", time.clock()-t
    # print len(p_a_first.plans)

    # p_a_first.add_plan("data/existing_plan.json")
    # p_a_first.add_plan("data/new_plan.json")
    # p_a_first.alt_score(p_a_first.plans[1])


    #conflicts_a2 = p_a_first.add_plan("data/new_plan.json")

    # print "###########"
    # conflicts_b1 = p_b_first.add_plan("data/new_plan.json")
    # conflicts_b2 = p_b_first.add_plan("data/existing_plan.json")

    #print "A FIRST"
    #p_a_first.print_conflicts(conflicts_a2)
    #print "B FIRST"
    #p_b_first.print_conflicts(conflicts_b2)


    # print "Interference", conflicts_a2[0].interferences
    # print "Interference", conflicts_b2[0].interferences

    # # Use the treatment intersection to check if two plans are almost similar?
    # # Or say that names must be unique?
    # # conflicts_3 = p.add_plan("data/new_plan.json")
    # #print conflicts_2
    # #p.print_conflicts(conflicts_1)
    # #p.print_conflicts(conflicts_2)
    # #p.print_conflicts(conflicts_3)
    # print "--------------------------------------------------------------------"
    # print "A FIRST"
    #p_a_first.generate_alerts(p_a_first.plans[1], conflicts_a2)
    # print "B FIRST"
    # p_b_first.generate_alerts(p_b_first.plans[1], conflicts_b2)


    # # Should say which plan it is conflicting with


