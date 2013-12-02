class Treatment():
	""" A class representing all known treatments """

	def __init__(self, data):
		""" Initialize a treatment from a dict object with the necessary attributes"""
		self.name = data["name"]
		self.effects = {}
		for e in data["effects"]:
			p = data["effects"][e]
			self.effects[e] = TreatmentEffect(e, p["worse"], p["better"], p["same"])

	def __str__(self):
		return self.name

	def __repr__(self):
		return "Treatment(" + self.__str__() + ")"

class TreatmentEffect:
	def __init__(self, name, worse, better, same):
		self.name = name
		self.worse = worse
		self.better = better
		self.same = same

class Plan():
	""" A class for representing caretaker plans """
	def __init__(self, data, treatments):
		""" Initialize a plan from a dict object with the necessary attributes"""
		self.name = data["name"]
		self.treatments = []
		self.effects = {}

		for t in data["treatments"]:
			self.treatments.append(treatments[t])

		self.calculate_effects()

	def calculate_effects(self):
		""" Calculate all effects of a plan, and which treatments in the plan that causes them """
		# Reset effects
		for t in self.treatments:
			for effect_name in t.effects:
				self.effects.setdefault(effect_name, set()).add(t)

	def __str__(self):
		return self.name

	def __repr__(self):
		return "PLAN(" + self.__str__() + ")"


##################################################
######### NOT IMPLEMENTED/USED YET ###############
##################################################
class PlanConflict():
	def __init__(self, plan_a, plan_b):
		self.plan_a = plan_a
		self.plan_b = plan_b
		self.conflicts = []

	def check_for_conflicts():
		pass
		# A lot of looping

class Conflict():

	@classmethod
	def build_conflict(*treatments):
		return Conflict()

	def __init__(self):
		self.score = 0
		self.body_function = 0



