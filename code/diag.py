def scores(n, k):
	s = [0 for _ in range(k)]
	s[0] = n
	t = True
	while t:
		v = [s[i-1] - s[i] for i in range(1, k)] 
		total = sum(v)
		v.append(n-total)
		yield v
		t = False
		for i in range(k-1, 0, -1):
			if s[i] < s[i-1]:
				s[i] += 1	
				t = True
				for j in range(i+1, k):
					s[j] = 0 
				break

def fixed_numbers(k):
	i = 0
	while True:
		for v in scores(i, k):
			yield v
		i += 1

def perm_generator(g, k):
	l = []
	i = 0
	for v in g:
		l.append(v)
		for v in scores(i, k):
			yield [l[j] for j in v]
		i += 1

def product(g, h):
	gs = []
	hs = []
	m = 0
	while True:
		gs.append(next(g))
		hs.append(next(h))
		for i in range(m+1):
			yield (gs[i], hs[m-i])
		m += 1
