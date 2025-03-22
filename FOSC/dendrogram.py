class DendrogramStructure:

  # Initialization parameters:
  # Z: the original 
  def __init__(self, Z):
    self.dicNodes = {}
    self.dicAffectedClustersByLevel = {}
    self.numObjects = len(Z) + 1

    nodesIds = self.numObjects

    # Creating singleton Nodes
    for i in range(self.numObjects):
      self.dicNodes[i] = [i]
    
    # Creating intermediate nodes. In this scenario we keep track of the objects
    # contained in each node. It will be important to build the cluster tree
    # structure.
    for row in Z:
      leftNode = int(row[0])
      rightNode = int(row[1])
      level = row[2]

      self.dicNodes[nodesIds] = self.dicNodes[leftNode] + self.dicNodes[rightNode]
      
      if level not in self.dicAffectedClustersByLevel:
        self.dicAffectedClustersByLevel[level] = [leftNode, rightNode]
      else:
        # Check if there is in this level another cluster that is contained in
        # the new node. This node will not be added to the affected levels.
        leftNodeInLevel = False
        rightNodeInLevel = False

        for node in self.dicAffectedClustersByLevel[level]:
          if set(self.dicNodes[node]).issubset(self.dicNodes[leftNode]):
            leftNodeInLevel = True
          
          if set(self.dicNodes[node]).issubset(self.dicNodes[rightNode]):
            rightNodeInLevel = True

        if (not leftNodeInLevel) and rightNodeInLevel:
          self.dicAffectedClustersByLevel[level].append(leftNode)

        elif (not rightNodeInLevel) and leftNodeInLevel:
          self.dicAffectedClustersByLevel[level].append(rightNode)
        
        else:
          self.dicAffectedClustersByLevel[level].append(leftNode)
          self.dicAffectedClustersByLevel[level].append(rightNode)

      nodesIds += 1
    #print("Created dendrogram structure")

  def getAffectedNodesAtLevel(self, level):
    return self.dicAffectedClustersByLevel[level]

  def getFirstObjectAtNode(self, i):
    return self.dicNodes[i][0]
  
  def getSignificantLevels(self):
    result = list(self.dicAffectedClustersByLevel.keys())
    result.sort(reverse=True) 
    return result

  def getNumObjects(self):
    return self.numObjects

  def getNodeSize(self, id):
    return len(self.dicNodes[id])
  
  def getObjectsAtNode(self, i):
    return self.dicNodes[i]
  
  
  def __str__(self):
    return str(self.dicNodes) + "\n Affected clusters by level" + str(self.dicAffectedClustersByLevel)
