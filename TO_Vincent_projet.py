# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 11:48:19 2020

@author: Vincent
"""

import copy # pour forker une chaîne
import datetime # pour obtenir le temps réel pour les timestamps
import hashlib # hash
    
# Premièrement on définit les classes
class MinimalChain():
    def __init__(self): # pour initialiser lors de la création d'une chaîne
        self.blocks = [self.get_genesis_block()]
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
    
    def get_genesis_block(self): 
        return MinimalBlock(0, 
                            datetime.datetime.utcnow(), 
                            'Genesis', 
                            'arbitrary')
    
    def add_block(self, data):
        self.blocks.append(MinimalBlock(len(self.blocks), 
                                        datetime.datetime.utcnow(), 
                                        data, 
                                        self.blocks[len(self.blocks)-1].hash))
    
    def get_chain_size(self): # exclure le genesis block
        return len(self.blocks)-1
    
    def verify(self, verbose=True): 
        flag = True
        for i in range(1,len(self.blocks)):
            if not self.blocks[i].verify():
                flag = False
                if verbose:
                    print(f'Wrong data type(s) at block {i}.')
            if self.blocks[i].index != i:
                flag = False
                if verbose:
                    print(f'Wrong block index at block {i}.')
            if self.blocks[i-1].hash != self.blocks[i].previous_hash:
                flag = False
                if verbose:
                    print(f'Wrong previous hash at block {i}.')
            if self.blocks[i].hash != self.blocks[i].hashing():
                flag = False
                if verbose:
                    print(f'Wrong hash at block {i}.')
            if self.blocks[i-1].timestamp >= self.blocks[i].timestamp:
                flag = False
                if verbose:
                    print(f'Backdating at block {i}.')
        return flag
    
    def fork(self, head='latest'):
        if head in ['latest', 'whole', 'all']:
            return copy.deepcopy(self)
        else:
            c = copy.deepcopy(self)
            c.blocks = c.blocks[0:head+1]
            return c
    
    def get_root(self, chain_2):
        min_chain_size = min(self.get_chain_size(), chain_2.get_chain_size())
        for i in range(1,min_chain_size+1):
            if self.blocks[i] != chain_2.blocks[i]:
                return self.fork(i-1)
        return self.fork(min_chain_size)
    
class MinimalBlock():
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hashing()
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
    
    def hashing(self):
        key = hashlib.sha256() # hashage de type sha256 comme le Bitcoin
        key.update(str(self.index).encode('utf-8'))
        key.update(str(self.timestamp).encode('utf-8'))
        key.update(str(self.data).encode('utf-8'))
        key.update(str(self.previous_hash).encode('utf-8'))
        return key.hexdigest()
    
    def verify(self): # vérifier les types de données de toutes les informations dans un bloc
        instances = [self.index, self.timestamp, self.previous_hash, self.hash]
        types = [int, datetime.datetime, str, str]
        if sum(map(lambda inst_, type_: isinstance(inst_, type_), instances, types)) == len(instances):
            return True
        else:
            return False

# Test de la chaîne
c = MinimalChain() # Démarrage de la chaîne
for i in range(1,20+1):
    c.add_block(f'Ceci est le bloc {i} de ma première chaîne.')

print(c.blocks[3].timestamp)
print(c.blocks[7].data)
print(c.blocks[9].hash)

print(c.get_chain_size())
print(c.verify())

# Test d'erreur
c_forked = c.fork('latest')
print(c == c_forked)

c_forked.add_block('Nouveau bloc pour la chaîne forké')
print(c.get_chain_size(), c_forked.get_chain_size())

c_forked = c.fork('latest')
c_forked.blocks[9].index = -9
c_forked.verify()

c_forked = c.fork('latest')
c_forked.blocks[16].timestamp = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)
c_forked.verify()


c_forked = c.fork('latest')
c_forked.blocks[5].previous_hash = c_forked.blocks[1].hash
c_forked.verify()