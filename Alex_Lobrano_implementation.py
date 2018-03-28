import math
import random
import fractions
import hashlib
import string

randnum = random.SystemRandom()
############## Problem 1 a ##############

# Generate prime number of size n bits
def generate_prime(n):
	# sample uniform number of n bits
	# use isPrimeMR() to test that the generated number is prime
	
	for i in xrange(3*pow(n,2)):
		p = randnum.getrandbits(n-1)			# generate N-1 random bits
		p = format(p, 'b')					# convert to binary string
		for i in range(n - len(p) - 1):
			p = "0" + p						# add missing zeroes
		p = "1" + p							# add 1 to front to ensure N bits
		p = int(p, 2)						# convert back to int
		if(isPrimeMR(p)): return p

#get number p, test if it's prime using Miller-Rabin
def isPrimeMR(p):
	
	if(p % 2 == 0): return False
	#if(isPerfectPower(p)): return False
	u = p - 1
	u = u/2
	r = 1
	while(u % 2 == 0):
		u = u/2
		r += 1
	for j in range(10):
		a = randnum.randint(2, p-1)
		if(foundWitness(a,u,r,p)):
			return False
	return True

#get number p, test if it's a perfect power
def isPerfectPower(p):
	for e in range(2, len(format(p, 'b'))):
		a = 1
		b = p
		while(a <= b):
			m = (a+b)/2
			if(pow(m,e) == p): return True
			if(pow(m,e) > p):
				b = m - 1
			if(pow(m,e) < p):
				a = m + 1
	return False
	
def foundWitness(a, u, r, p):
	if((pow(a,u,p) != 1) and (pow(a,u,p) != p-1)):
		for i in range(1, r):
			if(pow(a,2**i*u,p) == p-1):
				return False
		return True
	return False

# primality test using the naive approach
def isPrimeNaive(p):
	for i in range(2, int(math.sqrt(p))+2):
		if p % i == 0:
			return False
	return True

# returns x such that a*x + b*y = g
def modinv(a, b):
    x0, x1, y0, y1 = 1, 0, 0, 1
    while a != 0:
        q, b, a = b // a, a, b % a
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return y0
	#return b, y0, x0 #(g,x,y)
	
def generate_string(size):
	temp = ''
	for i in range(size):
		temp += random.choice(string.ascii_letters + string.digits)
	return temp
	
############## Problem 1 b ##############
class RSA:
	# initialize RSA, generate e, d
	def __init__(self):
		pass

	# Use generate_prime	
	def gen(self):
		# security parameter
		self.n = 1024
		
		# Primes p and q
		self.p = generate_prime(self.n)
		self.q = generate_prime(self.n)
		
		# RSA modulus N = pq
		self.rsamodulus = self.p * self.q
		
		# Phi(N)
		self.phi = (self.p - 1)*(self.q - 1)
		
		# Public key e
		self.e = randnum.randint(1, self.phi - 1)			# generate integer e between 1 and phi(N)-1
		while(fractions.gcd(self.e, self.phi) != 1):		# check if e is relatively prime to phi(N)
			self.e = randnum.randint(1, self.phi - 1)			# if not, generate new e and try again
		
		# Secret key d
		self.d = modinv(self.e, self.phi) + self.phi
	
	def trapdoor(self, x):
		y = pow(x, self.e, self.rsamodulus)
		return y
	
	def inverse(self, y):
		x = pow(y, self.d, self.rsamodulus)
		return x

############## Problem 2 ##############
class MerkleTree:
	def __init__(self):
		pass

	# Number of files
		self.n = 32
	
	def create_tree(self, file_list):
		self.file_list = file_list												# save files
		self.height = int(math.log(len(file_list))/math.log(2))					# number of levels in tree
		treesize = int(pow(2,self.height+1)-1)									# number of nodes in tree, including leaves and root
		self.tree = [None] * treesize
		
		leaf_start = int(pow(2,self.height)-1)
		for i in range(leaf_start, leaf_start+len(file_list)):					# create leaves as nodes for all files
			hash = hashlib.sha256(self.file_list[i-leaf_start])
			self.tree[i] = hash.hexdigest()
		
		for level in range(self.height, 0, -1):
			for level_offset in range(pow(2,level)-1, pow(2,level+1)-1, 2):
				temp1 = pow(2, level) - 1
				temp2 = pow(2, level+1) - 1
				parent_index = temp1 + (level_offset - temp2)/2
				data = self.tree[level_offset] + self.tree[level_offset+1]
				hash = hashlib.sha256(data)
				self.tree[parent_index] = hash.hexdigest()
		
		hash = hashlib.sha256(self.tree[1] + self.tree[2])
		self.tree[0] = hash.hexdigest()
		self.root = self.tree[0]

	def read_file(self, i):
		pass
		
		file = self.file_list[i]						# file i
		
		leaf_start = int(pow(2,self.height)-1)			# index where leaves start
		leaf_offset = leaf_start+i						# index of leaf containing hash of file i
		
		if(leaf_offset % 2 == 0): 						# get index of sibling for leaf
			sibling_index = leaf_offset - 1
		else:
			sibling_index = leaf_offset + 1
		#print "Adding index to sibling list", sibling_index
		siblings_list = [ [sibling_index,self.tree[sibling_index]] ]			# add sibling to sibling list
		
		for level in range(self.height, 1, -1):
			temp1 = pow(2, level) - 1
			temp2 = pow(2, level+1) - 1
			parent_index = temp1 + (leaf_offset - temp2)/2
			if(parent_index % 2 == 0):
				uncle_index = parent_index - 1
			else:
				uncle_index = parent_index + 1
			#print "Adding index to sibling list", uncle_index
			siblings_list.append([uncle_index,self.tree[uncle_index]])
			leaf_offset = parent_index
		
		# return file from Merkle Tree
		# Print siblings_list
		return (file, siblings_list)
		
	def write_file(self, i, file):
		pass
		
		self.file_list[i] = file
		hash = hashlib.sha256(file)
		
		leaf_start = int(pow(2,self.height)-1)			# index where leaves start
		leaf_offset = leaf_start+i						# index of leaf containing hash of file i
		#print "Setting new value for index", leaf_offset
		self.tree[leaf_offset] = hash.hexdigest()
		
		for level in range(self.height, 1, -1):
			if(leaf_offset % 2 == 0): 						# get index of sibling for leaf
				sibling_index = leaf_offset - 1
				hash = hashlib.sha256(self.tree[sibling_index] + self.tree[leaf_offset])
			else:
				sibling_index = leaf_offset + 1
				hash = hashlib.sha256(self.tree[leaf_offset] + self.tree[sibling_index])
			temp1 = pow(2, level) - 1
			temp2 = pow(2, level+1) - 1
			parent_index = temp1 + (leaf_offset - temp2)/2
			#print "Setting new value for index", parent_index
			self.tree[parent_index] = hash.hexdigest()
			leaf_offset = parent_index
		
		hash = hashlib.sha256(self.tree[1] + self.tree[2])
		#print "Setting new value for root"
		self.tree[0] = hash.hexdigest()
		self.root = self.tree[0]
		
	def check_integrity(self, i, file, siblings_list):
		# Check that self.root matches root computed from the returned path
		# valid = True if integrity is verified
		
		if(file != self.file_list[i]): return False
		
		hash = hashlib.sha256(file)
		for i in range(0, len(siblings_list)):
			if(siblings_list[i][0] % 2 == 0):									# sibling is even, then it is right term
				hash = hashlib.sha256(hash.hexdigest()+siblings_list[i][1])
			else:																# sibling is odd, so it is left term
				hash = hashlib.sha256(siblings_list[i][1]+hash.hexdigest())
		
		if(hash.hexdigest() == self.root): return True
		else: return False