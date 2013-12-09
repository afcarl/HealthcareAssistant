class Treatment():
    """ A class representing all known treatments """

    def __init__(self, data):
        """ Initialize a treatment from a dict object with the necessary attributes"""
        self.name = data["name"]
        self.interference = data["interference"]
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


    def __repr__(self):
        return "TRE(" + str(self.worse) + " " + str(self.better) + " " + str(self.same) + ")"

class Plan():
    """ A class for representing caretaker plans """

    def __init__(self, data, treatments):
        """ Initialize a plan from a dict object with the necessary attributes"""
        self.name = data["name"]
        self.treatments = []
        self.effects = {}
        self.doctor = data["doctor"]

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
    def __init__(self, treatments, score, plans):
        self.score = score
        self.conflicting_treatments = treatments
        self.plans = plans

    def __repr__(self):
        return "Inter(" + str(self.plans) + str(list(self.conflicting_treatments)[0]) + ", " + str(list(self.conflicting_treatments)[1]) + ", " + str(self.score) + ")"

class Conflict():

    def __init__(self, treatments):
        self.score = 0
        self.body_function = 0
        self.conflicting_treatments = treatments

    def __repr__(self):
        return "Conf(" + str(self.body_function) + ", " + str(self.conflicting_treatments) + ", " + str(self.score) + ")"
