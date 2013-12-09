import itertools as it
from random import random, shuffle
from time import clock


hr = "----------------------------------------"

def evaluate_unscaled(treatments, debug=False):
	n = len(treatments)
	total_score = 0
	for index in it.product(*(range(3) for x in range(n))): # O(n!)
		score = n-sum(index)
		if debug: print "Base score", score
		for i in range(n):
			if debug: print "Multiplying with", treatments[i][index[i]]
			score *= treatments[i][index[i]]
		if debug: print score, index
		total_score += score
	return total_score # Divide by n to normalize to range [-1, 1]


def evaluate(treatments, debug=False):
	n = len(treatments)
	total_score = 0
	for index in it.product(*(range(3) for x in range(n))): # O(n!)
		score = n-sum(index)
		if debug: print "Base score", score
		for i in range(n):
			if debug: print "Multiplying with", treatments[i][index[i]]
			score *= treatments[i][index[i]]
		if debug: print score, index
		total_score += score
	return total_score/float(n) # Divide by n to normalize to range [-1, 1]

def random_treatment():
	b = random()
	s = random()
	w = random()
	norm = sum([b,s,w])
	return (b/norm, s/norm, w/norm)

# better, same, worse
t1 = (0.3, 0.3, 0.4)
t2 = (0.1, 0.2, 0.7)
t3 = (0.6, 0.1, 0.3)

t1 = (1, 0, 0)
t2 = (0, 1, 0)
t3 = (0, 0.5, 0.5)

# Order seems to not matter
# t1,t3
# better 1*0.5
# worse = 0*0.5
# conf = 1*0.5

# t3, t1
# better = 0*1
# worse = 0.5*0
# conf = 0.5*1



def rec_conf(treatments, better, same, worse, conf, rec_call=False):

	# Find the probability of at least two treatments working against each other for a treatment


	# better, prob of all better or same
	# worse, prob of all worse or same
	# conf, prob of some conf
	if not rec_call:
		t = treatments[0]
		better = t[0]
		same = t[1]
		worse = t[2]
		conf = 0
		treatments = treatments[1:]

	# Base case
	if not treatments:
		return conf

	t = treatments[0]

	nbetter = better*(t[0]+t[1])+same*t[0] # all treatments before better or same, and this treatment better or same
	nworse = worse*(t[1]+t[2])+same*t[2] # all treatments before worse or same, and this treatment worse or same
	nsame = same*t[1]
	nconf = conf+better*t[2]+worse*t[0] # all ealier better or same, and this worse

	v =  rec_conf(treatments[1:], nbetter, nsame, nworse, nconf, True)
	return v

tself = (0.5, 0, 0.5)

confs = [random_treatment() for x in range(10)]
conf2 = [x for x in confs]
shuffle(conf2)
res = rec_conf(confs, "", "", "", "")
res2 = rec_conf(conf2, "", "", "", "")
print "RESULT", res, res2

# r = evaluate([t1, t2], True)
# print "Total score t1, t2:", r

# r = evaluate([t1, t2, t3])
# print "Total score t1-t3:", r

def fast_evaluate(treatments, chunk_size=3):
	n = len(treatments)
	runs = n/chunk_size
	rest = n%chunk_size

	result = 0
	for i in range(runs):
		start = i*chunk_size
		end = start + chunk_size
		prob = chunk_size/float(n)
		result += prob*evaluate(treatments[start:end])
	if rest:
		result += rest/float(n)*evaluate(treatments[-rest:])
	return result

# All better - not a conflict. Score=n
# ALl worse - potential conflict. Score =-n
# Some better, some worse, not conflict




k = 3
trtmnts = [random_treatment() for x in range(k)] # Takes crazy long for large number of treatments

t1 = (0.3, 0.3, 0.4)
t2 = (0.1, 0.2, 0.7)
t3 = (0.6, 0.1, 0.3)

t1 = (1,0,0)
t2 = (0,0,1)
t3 = (0,0,1)

treatments = [t1, t2, t3]
k = 12
treatments = [random_treatment() for x in range(k)]

# All give the same result

# print "Single scores"
# best_single = -1
# worst_single = 1
# for t in treatments:
# 	print t[0]-t[2]
# 	best_single = max(best_single, t[0]-t[2])
# 	worst_single = min(worst_single, t[0]-t[2])
# 	# Look at some delta score to determine conflicts?


# total = fast_evaluate(treatments)*len(treatments)
# score = (total)/best_single
# print "Best single", best_single
# print "Worst single", worst_single
# print "Delta", best_single - worst_single
# print "Total delta", total - best_single
# print "Total", total
# print "Score:", score

# print hr
# print "Unscaled:", evaluate_unscaled(treatments)
# print "Scaled:", evaluate(treatments)*len(treatments)
# print "Fast:", fast_evaluate(treatments,1)*len(treatments)
# print "ALT (LOL)", sum([x[0]-x[2] for x in treatments])

# print hr

# t1 = clock()-t

# print fast_evaluate(trtmnts, 1)
# print fast_evaluate(trtmnts)

# t = clock()
# fast_evaluate(trtmnts,2)
# t2 = clock()-t

# print "T1/T2"
# print t1/t2



#r1 = evaluate(trtmnts[:3])
#r2 = evaluate(trtmnts[3:6])
# r3 = evaluate(trtmnts[6:])
# print "AVG", (r1+r2+r3)/3.0
# print "T1", clock()-t
# t = clock()
# print evaluate(trtmnts)
# print "T", clock()-t

