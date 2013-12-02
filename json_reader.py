import json, os, time
from models import Treatment, Plan

class PlanSystem():
	""" 
		The HealthcareAssistant system
	"""
	def __init__(self):

		self.effect_table = {} # All treatments with a given effect
		self.treatments = {} # All known treatments
		self.plans = [] # All plans in the system
	
		self.load_treatments("data/real_treatments3.json")
		self.load_plans("data/real_plans.json")

	def load_plans(self, path):
		""" 
			Load a set of plans from the supplied path. Does not chbeck for conflicts
		"""
		with  open(path, 'r') as data:
			raw_plans = json.load(data)

		for rp in raw_plans:
			p = Plan(raw_plans[rp], self.treatments)
			self.plans.append(p)

	def load_treatments(self, path):

		with open(path, 'r') as data:
			raw_treatments = json.load(data)

		for rt in raw_treatments:
			t = Treatment(raw_treatments[rt])
			self.treatments[rt] = t
			for effect_name in t.effects:
				self.effect_table.setdefault(effect_name, set()).add(t)


	def find_conflicts(self, plan_a, plan_b):
		""" 
			Return all body functions that are affected by both plans 
			Does not check if the same treatment in both plan causes it
		"""
		conflicting_effects = set()
		for ea in plan_a.effects: # Effect A
			if ea in plan_b.effects:
				conflicting_effects.add(ea)
		return conflicting_effects

	def treatment_intersection(self, plan_a, plan_b):
		""" 
			Check if two plans use any of the same treatmetns
		"""
		shared_treatments = set()
		for ea in plan_a.effects: # Effect A
			if ea in plan_b.effects:
				in_both = plan_a.effects[ea].intersection(plan_b.effects[ea])
				shared_treatments |= in_both
		return shared_treatments

	def get_conflicts(self, E, *treatments):
		print treatments
		bl = [(1, [treatments[0].name], treatments[0].effects[E].better)] # better_list
		wl = [(1, [treatments[0].name], treatments[0].effects[E].worse)] # worse_list
		cl = [] #conflicts_list
		nl = treatments[0].effects[E].same #neutral_list

		for t in treatments[1:]:
		    bl, wl, cl, nl = expand(bl, wl, cl, nl, t)

		#figure out what to do with the lists and what to return
		#IDEA: return conflicts as conflicts and worse as notices
		return bl
	#can also do viz based on output

	def expand(better_list, worse_list, conf_list, neutral, T, E):
		# T treatment
		# E effect
		nbl = [] # new_better_list
		nwl = [] # new_worse_list
		ncl = [] # new_conflict_list

		for a in better_list:
			ncl.append((a[0]-1, a[1]+T.name, a[2]*T.effects[E].worse))
			nbl.append((a[0], a[1], a[2]*T.effects[E].same))
			nbl.append((a[0]+1, a[1]+T.effects[E].name, a[2]*T.effects[E].better))

		for a in worse_list:
			nwl.append((a[0]-1, a[1]+T.effects[E].name, a[2]*T.effects[E].worse))
			nwl.append((a[0], a[1], a[2]*T.effects[E].same))
			ncl.append((a[0]+1, a[1]+T.effects[E].name, a[2]*T.effects[E].better))

		for a in conf_list:
			ncl.append((a[0]-1, a[1]+T.effects[E].name, a[2]*T.effects[E].worse))
			ncl.append((a[0], a[1], a[2]*T.effects[E].same))
			ncl.append((a[0]+1, a[1]+T.effects[E].name, a[2]*T.effects[E].better))

		new_neutral = neutral * T.effects[E].same

		return new_better_list, new_worse_list, new_conf_list, new_neutral

	def evaluate_conflicts(self, conflicting_effects):
		# CAN CHECK MORE THAN TWO PLANS
		# USING THE WHOLE EFFECT TABLE IS (MAYBE) NOT EFFICIENT
		total_effects = {}
		for e in conflicting_effects:
			print e, "is caused by"
			better, same, worse = 0, 0, 0

			for t in p.effect_table[e]:
				if t in A.treatments: print "A", t
				if t in B.treatments: print "B", t


				better += float(t.effects[e].better)
				same += float(t.effects[e].same)
				worse += float(t.effects[e].worse)
			total_effects[e] = (better, same, worse)
				# AGGREGATE EFFECTS HERE
				# COMPARE IF THEY ARE POSITIVE OR NEGATIVE
				# AND IF THE GIVE THE CONFLICT A SCORE
				# WE CAN USE TO DECIDE IF WE SHOULD ALERT
				# ANYONE
		return total_effects


if __name__ == '__main__':
	p = PlanSystem()

	B = p.plans[0]
	A = p.plans[1]

	conflicting_effects = p.find_conflicts(A,B)

	# THE FOLLOWING SHOULD BE EXTRACTED INTO A METHOD
	
	# Simple aggregation of probabilities. It's here we must put or logic
	print p.evaluate_conflicts(conflicting_effects)


	#print "PLANS:", p.plans
	#print "TREATMENTS:", p.treatments

	#print p.get_conflicts(p.treatments["tegretol"], p.treatments["prednisone"], p.treatments["lisinopril"])

	print "PLANS WITH NAUSEA EFFECT", [plan for plan in p.plans if "nausea" in plan.effects]
	# print "###############"
	#print p.effect_table["fight_seizures"]


	#print "INTERSECT", p.treatment_intersection(p.plans[0],p.plans[1])






