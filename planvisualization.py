from json_reader import PlanSystem
import matplotlib.pyplot as plt
import numpy as np

class Vis_plan:

    def __init__(self):
        self.p = PlanSystem()

    def evaluate_conflicts_with_probs(self, plans):
            # CAN CHECK MORE THAN TWO PLANS
            # USING THE WHOLE EFFECT TABLE IS (MAYBE) NOT EFFICIENT
            total_effects = {}
            conflicting_effects = set()
            for plan in plans:
                conflicting_effects = conflicting_effects.union(plan.effectnames)
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

    def masterviz(self, plans):
        values = self.evaluate_conflicts_with_probs(plans)
        posValues = [a[0] for i, a in values.iteritems()]
        negValues = [a[2]*-1 for i, a in values.iteritems()]
        labels = [i for i, a in values.iteritems()]

        N = len(posValues)
        ind = np.arange(N)
        height = 0.5

        fig, ax = plt.subplots( )

        rects1 = ax.barh(ind, posValues, height, color='g')
        rects2 = ax.barh(ind, negValues, height, color='r')

        ax.set_ylabel('Affected Body function')
        ax.set_title('Results of the plans')
        ax.axis([min(negValues) -.1, max(posValues)+.1, min(ind), max(ind)])
        ax.set_yticks(ind+height)
        ax.set_yticklabels( labels )
        ax.yaxis.label.set_size(20)

        plt.grid(True)

        plt.show()


if __name__ == '__main__':
    v = Vis_plan()
    B = v.p.plans[0]
    A = v.p.plans[1]

    v.masterviz([A, B])