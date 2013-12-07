class Treatment():
    """ A class representing all known treatments """

    def __init__(self, data):
        """ Initialize a treatment from a dict object with the necessary attributes"""
        self.name = data["name"]
        self.interference= data["interference"]
        self.effects = {}
        for e in data["effects"]:
            p = data["effects"][e]
            self.effects[e] = TreatmentEffect(p["worse"], p["better"], p["same"])

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Treatment(" + self.__str__() + ")"


class TreatmentEffect:
    def __init__(self, worse, better, same):
        self.worse = float(worse)
        self.better = float(better)
        self.same = float(same)


class Plan():
    """ A class for representing caretaker plans """

    def __init__(self, data, treatments):
        """ Initialize a plan from a dict object with the necessary attributes"""
        self.name = data["name"]
        self.treatments = []
        self.effects = {}
        self.status = data["status"]

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


class PlanConflict():
    def __init__(self, plan_a, plan_b):
        self.plan_a = plan_a
        self.plan_b = plan_b
        self.conflicts = set()
        self.interferences = set()

    def __repr__(self):
        return "PC(" + str(self.plan_a) + ", " + str(self.plan_b) + ")"

class Interference():
    def __init__(self, treatments, score):
        self.score = score
        self.conflicting_treatments = treatments

    def __repr__(self):
        return "Inter(" + str(self.conflicting_treatments.a) + ", " + str(self.conflicting_treatments.b) + ", " + str(self.score) + ")"

class Conflict():
    '''
	@classmethod
	def build_conflict(cls, treatments):
		c = Conflict()
        c.conflicting_treatments = treatments
        return c
    '''

    def __init__(self, treatments):
        self.score = 0
        self.body_function = 0
        self.conflicting_treatments = treatments

    def __repr__(self):
        return "Conf(" + str(self.body_function) + ", " + str(self.conflicting_treatments) + ", " + str(self.score) + ")"

'''
Created on Oct 20, 2013

@author: Ofra
'''

class Pair(object):
    '''
    A utility class to represent pairs (ordering of the objects in the pair does not matter). It is used to represent mutexes (for both actions and propositions)
    '''


    def __init__(self, a, b):
        '''
        Constructor
        '''
        self.a = a
        self.b = b

    def __eq__(self, other):
        if (self.a == other.a) and (self.b == other.b):
            return True
        if (self.b == other.a) and (self.a == other.b):
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return str(self.a)+","+str(self.b)

    def __repr__(self):
        return "Pair("+ str(self) + ")"

    def __hash__(self):
        return hash((self.a,self.b))



