Quick Start Tutorial
====================

This is a tutorial that teaches how to quickly
start using the FOSC package.

Considering you have a dataset in a csv file,
start by loading its data.

.. code-block:: python

    import numpy as np

    mat = np.genfromtxt(file_path, dtype=float, delimiter=',', usecols=range(0, -1), missing_values=np.nan)

.. note::

   Replace `file_path` with your dataset's path.

   In this example, the last column represents the cluster
   to which an object is assigned, according to another
   algorithm. Since we are using our own method, we ignore
   the last column with the `usecols` parameter.

Choose the MClSize (minimum cluster size) parameter and the method of linkage:

.. code-block:: python

    mclsize = 30
    linkage_method = "single"

Calculate the distance matrix:

.. code-block:: python

    from scipy.spatial import distance_matrix

    dist_mat = distance_matrix(mat, mat, p=2)

Now, you can instantiate the FOSC object:

.. code-block:: python

    from FOSC import FOSC

    foscFramework = FOSC(dist_mat, linkage_method, mclsize)

And run the FOSC algorithm:

.. code-block:: python

    infiniteStability = foscFramework.propagateTree()
    partition, lastObjects = foscFramework.findProminentClusters(1, infiniteStability)

The partition returned from the
findProminentClusters method is the result of
running the FOSC algorithm i.e. the cluster
extraction.

Finally, you can visualize the results using the functions
available in the Plot module:

.. code-block:: python

    from FOSC import Plot

    Plot.plotDendrogram(foscFramework)
    Plot.plotSilhouette(foscFramework, partition)
    Plot.plotReachability(foscFramework, partition)






