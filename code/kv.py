import re

class Tree:
    def __init__(self, tail):
        self.neg = None
        self.pos = None 
        self.tail = tail 

    def test_word(self, word):
        return word + self.tail

    def is_leaf(self):
        return self.neg == None and self.pos == None

    def __str__(self):
        return str("({}, {}, {})".format(str(self.neg), self.tail, str(self.pos)))

class Learner:
    def __init__(self, oracle, alphabet):
        self.oracle = oracle
        self.alphabet = alphabet
        self.root = Tree("")
        self.access_string = {}
        self.access_string[self.root] = ""

    def leaves(self, tree=None):
        if tree == None:
            tree = self.root
        if tree.is_leaf():
            return [tree]
        else:
            poss = [leaf for leaf in self.leaves(tree.pos)]
            negs = [leaf for leaf in self.leaves(tree.neg)]
            return poss+negs

    def sift(self, word, tree=None):
        if tree == None:
            tree = self.root
        if tree.is_leaf():
            return tree
        if self.oracle(tree.test_word(word)):
            return self.sift(word, tree.pos)
        else:
            return self.sift(word, tree.neg)

    def automata(self):
        leaves = [leaf for leaf in self.leaves()]
        to_nat = {leaf : n for n, leaf in enumerate(leaves)}
        print([to_nat[leaf] for leaf in self.leaves() if self.oracle(self.access_string[leaf])])
        print ("-->", to_nat[self.sift("")])
        for q in self.leaves():
            word = self.access_string[q]
            for a in self.alphabet:
                print(word+a)
                p = self.sift(word+a)
                print (to_nat[q], a, to_nat[p])

    def add_conter_example(self, example):
        for i in range(len(example)):
            state = self.sift(example[:i])
            access = self.access_string[state]
            print(">>", access+example[i:])
            print("o>", self.oracle(access+example[i:]))
            if self.oracle(example) != self.oracle(access + example[i:]):
                print(">>>", access+example[i:])
                # okay, we have found the state that is actually two 
                # we need to turn this into a state
                del self.access_string[state]
                ex = Tree(example[i])
                st = Tree(state.tail)
                self.access_string[ex] = example
                self.access_string[st] = access
                pt = state.tail
                state.tail = example[i:]
                if self.oracle(example):
                    state.pos = ex 
                    state.neg = st 
                else: # otw 
                    state.neg = ex 
                    state.pos = st
                break

def oracle(string):
    return re.fullmatch("ab*$", string) != None

learner = Learner(oracle, ['a', 'b'])
while True:
    learner.automata()
    cex = input()
    learner.add_conter_example(cex)