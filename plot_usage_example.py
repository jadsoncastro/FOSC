from FOSC import FOSC
from FOSC import Plot
# from sklearn.metrics.pairwise import cosine_distances
import numpy as np
import os
from scipy.spatial import distance_matrix
# from scipy.spatial.distance import cdist



#### ############################################  Main script #########################################################
pathFiles = "./datasets/Handl_datasets/"
listOfFiles    = os.listdir(pathFiles)


listOfMClSize = [30]#, 5, 8,, 16, 20, 30]
methodsLinkage = ["single"]#, "average", "ward", "complete", "weighted"]


for fn in listOfFiles:
    if not fn.endswith(".csv"):continue 
    
    varFileName = str(fn).rsplit(".", 1)[0]
    print ("\n\n\nPerforming experiments in dataset " + varFileName)
    
    mat = np.genfromtxt(pathFiles+fn, dtype=float, delimiter=',', usecols=range(0, -1),missing_values=np.nan)
    partition = np.genfromtxt(pathFiles+fn, delimiter=',', usecols=-1, dtype=int)

    # print("Matrix===================\n", mat)

    dist_mat = distance_matrix(mat, mat, p=2)
    # dist_mat = cosine_distances(mat)
    # distance_matrix = cdist(mat, mat, metric='euclidean')
    # print("DISTANCE MATRIX====\n", dist_mat, "\n")
    
    # Running tests
    for m in listOfMClSize:
        print("--------------------------------------- MCLSIZE = %d ---------------------------------------" % m)
        
        for lm in methodsLinkage:
            
            titlePlot = varFileName + "\n(" + lm + " and mClSize=" + str(m) + ")"
            savePath = pathFiles + varFileName + "-" + lm + " mClSize-" + str(m)+ ".png"
            saveDendrogram = pathFiles + varFileName + "-dendrogram-" + lm + " mClSize-" + str(m)+ ".png"

            print("Using linkage method %s" % lm)
                        
            foscFramework = FOSC(dist_mat, lm, mClSize=m)
            # foscFramework.computeQualityMeasure()
            infiniteStability = foscFramework.propagateTree()
            partition, lastObjects = foscFramework.findProminentClusters(1, infiniteStability)

            # print(foscFramework.getHierarchy())
            # print("===============\n", foscFramework.ds.dicAffectedClustersByLevel)
            # print("==============\n", foscFramework.ds.dicNodes)
            # print("===============\n", foscFramework.clusters)
            # print("LEN PARTITION ======\n", len(partition), "============\n")
            # 9: 11, 12, 13, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29

            # partition = np.array([])
            # print(partition)
            # Plot.plotDendrogram(foscFramework, titlePlot)
            fig_name = varFileName + "-" + lm + " mClSize-" + str(m)+ ".png"
            silhouette_fig_name = "silh_" + fig_name
            save_dir = "./tests/results/"
            save_silhouette_dir = save_dir + silhouette_fig_name
            Plot.plotSilhouette(foscFramework)#, saveDescription=save_silhouette_dir)

            reachability_fig_name = "reac_" + fig_name
            save_reachability_dir = save_dir + reachability_fig_name
            Plot.plotReachability(foscFramework)#, saveDescription=save_reachability_dir)
            # hierarchy_matrix = foscFramework.getHierarchy()
            # print(hierarchy_matrix)
            # print(partition)
            silhouette_with_partition_fig_name = "silh_p_" + fig_name
            save_silhouette_with_partition_dir = save_dir + silhouette_with_partition_fig_name
            # Plot.plotSilhouette(foscFramework, partition)#, saveDescription=save_silhouette_with_partition_dir)

            reachability_with_partition_fig_name = "reac_p_" + fig_name
            save_reachability_with_partition_dir = save_dir + reachability_with_partition_fig_name
            # Plot.plotReachability(foscFramework, partition)#, saveDescription=save_reachability_with_partition_dir)