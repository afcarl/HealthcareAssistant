class Treatment():
	""" A class representing all known treatments """
	def __init__(self, dictionary):
		""" Initialize a treatment from a dict object with the necessary attributes"""
		self.name = dictionary["name"]
		self.effects = []
		for e in dictionary["effects"]:
			worse, better, same = dictionary["effects"][e]["worse"], dictionary["effects"][e]["better"], dictionary["effects"][e]["same"]
			self.effects.append( TreatmentEffect(e, worse, better, same) )



	def has_effect(self, effect):
		""" Check if the treatment has a specific effect """
		for e in self.effects:
			if effect == e[0]: return True
		return False

	def __str__(self):
		return self.name

	def __repr__(self):
		return "treatment(" + self.__str__() + ")"

class TreatmentEffect:
	def __init__(self, name, worse, better, same):
		self.name = name
		self.worse = worse
		self.better = better
		self.same = same

class Plan():
	""" A class for representing caretaker plans """
	def __init__(self, dictionary, treatments):
		""" Initialize a plan from a dict object with the necessary attributes"""
		self.name = dictionary["name"]
		self.treatments = []
		for t in dictionary["treatments"]:
			self.treatments.append(treatments[t])
		self.calculate_effects()

	def calculate_effects(self):
		""" Calculate all effects of a plan, and which treatments in the plan that causes them """
		# Reset effects
		self.effects = {}
		for treatment in self.treatments:
			for effect in treatment.effects:
				if effect.name not in self.effects: self.effects[effect.name] = set()
				self.effects[effect.name].add(treatment)

	def has_effect(self, effect):
		""" Check if any of the treatments in a plan has a specific side effect """
		return effect in self.effects

	def __str__(self):
		return "PLAN(" + self.name + ")"

	def __repr__(self):
		return self.__str__()

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



