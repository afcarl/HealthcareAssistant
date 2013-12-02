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
	
		self.load_treatments("data/real_treatments2.json")
		self.load_plans("data/real_plans.json")

	def load_plans(self, path):
		""" 
			Load a set of plans from the supplied path. Does not chbeck for conflicts
		"""
		plan_json = open(path)
		self.raw_plans = json.load(plan_json)
		plan_json.close()
		for p in self.raw_plans:
			self.plans.append(Plan(self.raw_plans[p], self.treatments))

	def load_treatments(self, path):
		treatment_json = open(path)
		self.raw_treatments = json.load(treatment_json)
		treatment_json.close()

		for t in self.raw_treatments:
			self.treatments[t] = Treatment(self.raw_treatments[t])
			for effect in self.treatments[t].effects:
				if effect.name in self.effect_table:
					self.effect_table[effect.name].add(self.treatments[t])
				else:
					self.effect_table[effect.name] = {self.treatments[t]}



	def find_conflicts(self, plan_a, plan_b):
		""" 
			Return all body functions that are affected by both plans 
			Does not check if the same treatment in both plan causes it
		"""
		conflicting_effects = set()
		for effa in plan_a.effects:
			if effa in plan_b.effects:
				conflicting_effects.add(effa)
		return conflicting_effects

	def treatment_intersection(self, plan_a, plan_b):
		""" 
			Check if two plans use any of the same treatmetns
		"""
		shared_treatments = set()
		for effa in plan_a.effects:
			if effa in plan_b.effects:
				in_both = plan_a.effects[effa].intersection(plan_b.effects[effa])

				shared_treatments |= in_both
		return shared_treatments

	def plan_report(plan):
		""" Return a summary of all effects of a plan """

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



if __name__ == '__main__':
	p = PlanSystem()

	B = p.plans[0]
	A = p.plans[1]

	conflicting_effects = p.find_conflicts(A,B)

	# THE FOLLOWING SHOULD BE EXTRACTED INTO A METHOD
	# CAN CHECK MORE THAN TWO PLANS
	# USING THE WHOLE EFFECT TABLE IS (MAYBE) NOT EFFICIENT

	total_effects = {}
	for e in conflicting_effects:
		print e, "is caused by"
		for t in p.effect_table[e]:
			if t in A.treatments: 
				print "A", t
			if t in B.treatments: print "B", t
			# AGGREGATE EFFECTS HERE
			# COMPARE IF THEY ARE POSITIVE OR NEGATIVE
			# AND IF THE GIVE THE CONFLICT A SCORE
			# WE CAN USE TO DECIDE IF WE SHOULD ALERT
			# ANYONE
			


	#print "PLANS:", p.plans
	#print "TREATMENTS:", p.treatments

	#print p.get_conflicts(p.treatments["tegretol"], p.treatments["prednisone"], p.treatments["lisinopril"])

	#print "PLANS WITH NAUSEA EFFECT", [plan for plan in p.plans if plan.has_effect("nausea")]
	# print "###############"
	#print p.effect_table["fight_seizures"]


	#print "INTERSECT", p.treatment_intersection(p.plans[0],p.plans[1])






