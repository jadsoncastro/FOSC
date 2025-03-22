from FOSC import Plot, FOSC
import numpy as np
from scipy.spatial import distance_matrix

file_path = "./datasets/Handl_datasets/10d-10c-no0.csv"
mClSize = 30
linkage_method = "single"

mat = np.genfromtxt(file_path, dtype=float, delimiter=',', usecols=range(0, -1), missing_values=np.nan)
dist_mat = distance_matrix(mat, mat, p=2)
                    
foscFramework = FOSC(dist_mat, linkage_method, mClSize=mClSize)
infiniteStability = foscFramework.propagateTree()
partition, lastObjects = foscFramework.findProminentClusters(1, infiniteStability)

Plot.plotSilhouette(foscFramework, partition)
Plot.plotReachability(foscFramework, partition)