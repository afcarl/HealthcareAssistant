from json_reader import PlanSystem

class Vis_plan:

    def __init__(self):
        self.p = PlanSystem()

    def evaluate_conflicts_with_probs(self, plans, conflicting_effects):
            # CAN CHECK MORE THAN TWO PLANS
            # USING THE WHOLE EFFECT TABLE IS (MAYBE) NOT EFFICIENT
            total_effects = {}
            for plan in plans:
                for e in conflicting_effects:
                    better, same, worse = 0, 0, 0

                    for t in self.p.effect_table[e]:
                        if t in plan.treatments:
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
    v = Vis_plan()
    B = v.p.plans[0]
    A = v.p.plans[1]
    #effects = B.effects + A.effects
    print A.effects.

    #v.evaluate_conflicts_with_probs([A, B],)