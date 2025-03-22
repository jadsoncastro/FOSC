from FOSC.dendrogram import DendrogramStructure
from FOSC.cluster import Cluster
from FOSC.utilClasses import TreeSet

from scipy.cluster.hierarchy import linkage
import numpy as np

class FOSC:
    WARNING_MESSAGE = "----------------------------------------------- WARNING -----------------------------------------------\n" \
                    "With your current settings, the cluster stability is not well-defined. It could receive\n" '''
                    infinite values for some data objects, either due to replicates in the data (not a set) or due to numerical\n
                    roundings (this does not affect the construction of the clustering hierarchy). For this reason,\n
                    the post-processing routine to extract a flat partition containing the most stable clusters may\n
                    produce unexpected results. It may be advisable to increase the value of mClSize.\n
                    -------------------------------------------------------------------------------------------------------"""
      '''


    def __init__(self, dist_mat, linkage_method, mClSize=4):
        
        self.Z = linkage(dist_mat, linkage_method, metric="euclidean")
        self.ds = DendrogramStructure(self.Z)
        self.numObjects = self.ds.getNumObjects()
        
        nextClusterLabel = 2
        currentClusterLabels = np.ones(self.numObjects, dtype=np.int64)
        
        self.clusters = []
        self.clusters.append(None)
        
        # Creating the first cluster of the cluster tree
        self.clusters.append(Cluster(1, None, np.NaN, self.numObjects))

        
        affectedClusterLabels = TreeSet()

        significantLevels = self.ds.getSignificantLevels()
        dic_nodes = self.ds.dicNodes
        list_of_clusters = list(dic_nodes.keys())
        num_rows = len(dic_nodes[list_of_clusters[-1]])
        num_columns = len(significantLevels) + 1
        self.hierarchy_matrix = np.zeros((num_rows, num_columns))
        label = 2

        self.hierarchy_matrix[:, 0] = 1
        # print(self.hierarchy_matrix)
        # print("significant levels: ", significantLevels, "\n")

        # print(significantLevels())
        for j, currentLevelWeight in enumerate(significantLevels):

            # calculate hierachy matrix
            for i in range(num_rows):
                self.hierarchy_matrix[i, j + 1] = self.hierarchy_matrix[i, j]
            
            clusters = self.ds.getAffectedNodesAtLevel(currentLevelWeight)
            # print("clusters", clusters, j, "\n")
            if len(dic_nodes[clusters[0]]) >= mClSize and len(dic_nodes[clusters[1]]) >= mClSize: # INTEGRATE
                for cluster in clusters:
                    objects = dic_nodes[cluster]
                    # print("objects mine:\n", "cluster", label, "=", objects)
                    for i in objects:
                        self.hierarchy_matrix[i, j + 1] = label
                    label += 1 ############### INTEGRATE
            else:
                for cluster in clusters:
                    objects = dic_nodes[cluster]
                    if len(objects) < mClSize:
                        for i in objects:
                            self.hierarchy_matrix[i, j + 1] = 0
            
            #print("Labels at level %.5f: %s" %(currentLevelWeight, currentClusterLabels))
            affectedNodes = TreeSet()
            affectedNodes.addAll(self.ds.getAffectedNodesAtLevel(currentLevelWeight))
            
            for nodeId in affectedNodes:
                if currentClusterLabels[self.ds.getFirstObjectAtNode(nodeId)] != 0:
                    affectedClusterLabels.add(currentClusterLabels[self.ds.getFirstObjectAtNode(nodeId)])
            
            
            if affectedClusterLabels.isEmpty(): continue
            
            #print("Level %.5f. Affected labels %s" %(currentLevelWeight, affectedClusterLabels))
            
            while not affectedClusterLabels.isEmpty():
                examinedClusterLabel = affectedClusterLabels.last()
                affectedClusterLabels.remove(examinedClusterLabel)
                examinedNodes = TreeSet()
                
                # Get all the affected nodes that are members of the cluster currently being examined
                for nodeId in affectedNodes:
                    if currentClusterLabels[self.ds.getFirstObjectAtNode(nodeId)] == examinedClusterLabel:
                        examinedNodes.add(nodeId)
                
                #print("Level %.5f. Affected nodes in dendrogram for cluster %d: %s" %(currentLevelWeight, examinedClusterLabel, affectedNodes))
                ########## Check if the examinedNodes represent a cluster division or a cluster shrunk ###########
                validChildren = TreeSet()
                virtualChildNodes = TreeSet()
                
                for nodeId in examinedNodes:
                    if self.ds.getNodeSize(nodeId) >= mClSize:
                        validChildren.add(nodeId)
                    else:
                        virtualChildNodes.add(nodeId)
                
                # If we have more than two valid child, we create new clusters, setup the
                # parent and ajust the parent's death level.
                # print("Level %.5f. Valid nodes for cluster %d: %s" %(currentLevelWeight, examinedClusterLabel, validChildren))
                
                if len(validChildren) >= 2: ############# INTEGRATE
                    for nodeId in validChildren:
                        # print("validChildren:\n", validChildren)
                        # print("objects Jadson:\n", "cluster", nextClusterLabel, "=", self.ds.getObjectsAtNode(nodeId))
                        # print("currentClusterLabels:\n", currentClusterLabels)
                        newCluster = self._createNewCluster(self.ds.getObjectsAtNode(nodeId), currentClusterLabels, self.clusters[examinedClusterLabel], nextClusterLabel, currentLevelWeight)
                        self.clusters.append(newCluster)
                        nextClusterLabel += 1 ########### INTEGRATE
                
                # We have to assign the noise label for all the objects in virtual child nodes list. We also have to update the respective cluster parent.
                for nodeId in virtualChildNodes:
                    if currentClusterLabels[self.ds.getFirstObjectAtNode(nodeId)] != 0:
                        self._createNewCluster(self.ds.getObjectsAtNode(nodeId), currentClusterLabels, self.clusters[examinedClusterLabel], 0, currentLevelWeight)
    
    
    def _createNewCluster(self, points, clusterLabels, parentCluster, clusterLabel, levelWeight):
        """
        Function to create a new cluster structure, or update the cluster when there is a shrunk of it
        (the children do not satisfy the mClSize parameter)
        """
        for point in points:
            clusterLabels[point] = clusterLabel
        
        parentCluster.detachPoints(len(points), levelWeight)
        
        if clusterLabel != 0:
            cluster = Cluster(clusterLabel, parentCluster, levelWeight, len(points))
            cluster.setObjects(points)
            return cluster
        else:
            parentCluster.addPointsToVirtualChildCluster(points)
            return None


    def propagateTree(self, **kwargs):
        """
        Propagates constraint satisfaction, stability, bcubed index, and lowest child death level from each child
        cluster to each parent cluster in the tree.  This method must be called before calling
        findProminentClusters()

        Returns
        -------
        bool: `True` if there are any clusters with infinite stability, `False` otherwise
        """
        clustersToExamine = TreeSet()
        addedToExaminationList = []
        infiniteStability = False
        updateQualityMeasure = False
        
        addedToExaminationList = len(self.clusters)*[False]
        dicQualityMeasure = {}

        print(kwargs, bool(dicQualityMeasure))

        if "dict" in kwargs:
            dicQualityMeasure = kwargs["dict"]

            if ("quality_measure" in kwargs) and (kwargs["quality_measure"] in dicQualityMeasure):
                updateQualityMeasure= True
            else:
                messageError = "There is no quality measure named " + kwargs["quality_measure"] + " in the dictionary!"
                raise NameError(messageError)
        


        # Find all leaf clusters in the cluster tree
        for cluster in self.clusters:
            if cluster == None: continue

            #if we present a quality measure to evaluate, we need to update the quality measure in each cluster
            if updateQualityMeasure:
                cluster.setQualityMeasure(dicQualityMeasure["quality_measure"][cluster.getLabel,:])

            
            if not cluster._hasChildren():
                clustersToExamine.add(cluster.getLabel())
                addedToExaminationList[cluster.getLabel()] = True
            
        while len(clustersToExamine) > 0:
            currentLabel = clustersToExamine.pop(-1)
            currentCluster = self.clusters[currentLabel]            
            currentCluster.propagate()
            
            if currentCluster.getStability() == np.Inf or currentCluster.getStability() == np.NaN:
                infiniteStability = True
            
            if currentCluster.getParent() != None:
                parent = currentCluster.getParent()
                
                if not addedToExaminationList[parent.getLabel()]:
                    clustersToExamine.add(parent.getLabel())
                    addedToExaminationList[parent.getLabel()] = True
            
        if infiniteStability:
            print(FOSC.WARNING_MESSAGE)
        
        return infiniteStability
    
    
    
    def findProminentClusters(self, rootTree, infiniteStability):
        partition = np.zeros(self.numObjects, dtype=np.int64)
        solution = self.clusters[rootTree].getPropagatedDescendants()
        significantObjects={}


        for cluster in solution:
            affectedNodes = self.ds.getAffectedNodesAtLevel(cluster.getDeathLevel())
            lastPoints=[]
            for idNode in affectedNodes:
                lastPoints+= self.ds.getObjectsAtNode(idNode)


            for point in cluster.getObjects():
                if point in lastPoints:
                    significantObjects[cluster.getLabel()]=point

                partition[point] = cluster.getLabel()
        
        return partition, significantObjects


    def getZ(self):
        return self.Z
    
    def getHierarchy(self):
        return self.clusters
    
    def getHierarchyMatrix(self):
        return self.hierarchy_matrix