import json, os, time

class Treatment():
	""" A class representing all known treatments """
	def __init__(self, dictionary):
		""" Initialize a treatment from a dict object with the necessary attributes"""
		self.name = dictionary["name"]
		self.effects = []
		for e in dictionary["effects"]:
			worse, better, same = dictionary["effects"][e]["worse"], dictionary["effects"][e]["better"], dictionary["effects"][e]["same"]
			self.effects.append( (e, worse, better, same) )

	def has_effect(self, effect):
		""" Check if the treatment has a specific effect """
		for e in self.effects:
			if effect == e[0]: return True
		return False

	def __str__(self):
		return self.name

	def __repr__(self):
		return "TREATMENT(" + self.__str__() + ")"

class Plan():
	""" A class for representing caretaker plans """
	def __init__(self, dictionary, treatments):
		""" Initialize a plan from a dict object with the necessary attributes"""
		self.name = dictionary["name"]
		self.treatments = []
		for t in dictionary["treatments"]:
			self.treatments.append(treatments[t])
	def has_effect(self, effect):
		""" Check if any of the treatments in a plan has a specific side effect """
		for treatment in self.treatments:
			if treatment.has_effect(effect):
				return True
		return False

	def __str__(self):
		return "PLAN(" + self.name + ")=" + str(self.treatments)

	def __repr__(self):
		return self.__str__()

class PlanSystem():
	""" The system responsible for detecting conflicts and notifying people """
	def __init__(self):
		treatment_json = open("real_treatments.json")
		self.raw_treatments = json.load(treatment_json)
		treatment_json.close()

		plan_json = open("real_plans.json")
		self.raw_plans = json.load(plan_json)
		plan_json.close()

		self.treatments = {}
		for t in self.raw_treatments:
			self.treatments[t]=(Treatment(self.raw_treatments[t]))
		#print "TREATMENTS", self.treatments

		self.plans = []
		for p in self.raw_plans:
			self.plans.append(Plan(self.raw_plans[p], self.treatments))

	def add_plan(self, path):
		""" Read in a new plan in json format, check for conflicts and alert caretakers """
		pass


p = PlanSystem()
print "PLANS:", p.plans
print "TREATMENTS:", p.treatments

print "PLANS WITH NAUSEA EFFECT", [plan for plan in p.plans if plan.has_effect("nausea")]

