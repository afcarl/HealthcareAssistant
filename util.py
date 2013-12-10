import time
def timer(func):
	""" Decorator to measure the performance of method calls """
	def wrapper(*arg):
		t1 = time.time()
		res = func(*arg)
		t2 = time.time()
		print '%s took %0.3f ms' % (func.func_name, (t2-t1)*1000.0)
		return res
	return wrapper

def printname(func):
	def wrapper(*arg):
		res = func(*arg)
		print "Method called:", func.func_name, "with arguments:", arg[1:]
		return res
	return wrapper
