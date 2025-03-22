import bisect## Tree set Class

class TreeSet:
    
    def __init__(self):
        self._treeset = []
    
        
    def addAll(self, elements):
        for element in elements:
            if element in self: continue
            self.add(element)
    
            
    def add(self, element):
        if element not in self:
            bisect.insort(self._treeset, element)
    
    
    def __getitem__(self,num):
        return self._treeset[num]
    
    def __len__(self):
        return len(self._treeset)
    
    def clear(self):
        self._treeset =[]
        
    
    def remove(self,element):
        try:
            self._treeset.remove(element)
        except ValueError:
            return False
    
        return True
    
    
    def __iter__(self):
        for element in self._treeset:
            yield element
  
    def pop(self, index):
        return self._treeset.pop(index)

  
    def last(self):
        return self._treeset[-1]
  

    def __str__(self):
        return str(self._treeset)
  

    def __contains__(self,element):
        try:
            return element== self._treeset[bisect.bisect_left(self._treeset, element)]
        except:
            return False


    def isEmpty(self):
        return len(self._treeset) == 0