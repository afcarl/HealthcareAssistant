import matplotlib.pyplot as plt
import numpy as np
from util import timer

class ConflictVisualizer:

    def __init__(self, plan_system):
        self.plan_system = plan_system

    def evaluate_conflicts_with_probs(self, plans): #FIXED - one bug was here
        # CAN CHECK MORE THAN TWO PLANS
        total_effects = {}
        all_effects = set()

        for plan in plans:
            all_effects = all_effects.union(plan.effects)

        for e in all_effects:
            better, same, worse = 0, 0, 0
            for plan in plans:
                for t in plan.treatments:
                    if t in self.plan_system.effect_table[e]:
                        better += float(t.effects[e].better)
                        same += float(t.effects[e].same)
                        worse += float(t.effects[e].worse)

            total_effects[e] = (better, same, worse)
        return total_effects

    def visualize(self, plans):
        """
            Calculate total probabilities of a set of plan in the plansystem,
            and plot them using the plot function.
        """
        total_effects = self.evaluate_conflicts_with_probs(plans)

        posValues, negValues, labels = [], [], []
        for key, value in total_effects.iteritems():
            posValues.append(value[0])
            negValues.append(-value[2])
            labels.append(key) 

        self.plot(posValues,negValues,labels)

    def plot(self, posValues, negValues, labels):
        """
            Create the actual plot with the supplied values
        """
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
    from plansystem import PlanSystem
    p = PlanSystem("data/treatments.json", "data/real_plans.json")
    v = ConflictVisualizer(p)
    B = v.plan_system.plans[0]
    A = v.plan_system.plans[1]
    v.visualize(p.plans)