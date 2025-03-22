from scipy.cluster.hierarchy import dendrogram
from FOSC.fosc import FOSC

import random
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from mplcursors import cursor
from typing import Optional


class Plot:
    
    def plotDendrogram(fosc: FOSC, title: str, saveDescription: Optional[str]=None):
        """
        Plots the colored dendrogram of the FOSC hierarchy.

        Parameters
        ----------
        fosc: FOSC
            The FOSC instance.
        title: str
            The title of the dendrogram.
        saveDescription: Optional[str]
            The path to save the dendrogram. If `None`, the dendrogram will be shown interactively.
        """      
        
        Z = fosc.getZ()
        no_of_colors=200
        palleteColors=["#"+''.join([random.choice('0123456789ABCDEF') for i in range(6)]) for j in range(no_of_colors)]

        infiniteStability = fosc.propagateTree() 
        result, _ = fosc.findProminentClusters(1, infiniteStability)

        uniqueValues = np.unique(result)
                
        dicColors = {}
        dicColors[0] = "#000000"

        for i in range(len(uniqueValues)):
            if uniqueValues[i] != 0:
                dicColors[uniqueValues[i]]= palleteColors[i]    
        
        
        colorsLeaf={}
        for i in range(len(result)):
            colorsLeaf[i] = dicColors[result[i]]
        
        
        # notes:
        # * rows in Z correspond to "inverted U" links that connect clusters
        # * rows are ordered by increasing distance
        # * if the colors of the connected clusters match, use that color for link
        linkCols = {}
        for i, i12 in enumerate(Z[:,:2].astype(int)):
            c1, c2 = (linkCols[x] if x > len(Z) else colorsLeaf[x]
                    for x in i12)
                    
            linkCols[i+1+len(Z)] = c1 if c1 == c2 else dicColors[0]
        
        fig = plt.figure(figsize=(15, 10))
        
        dn = dendrogram(Z=Z, color_threshold=None, leaf_font_size=10,
                        leaf_rotation=45, link_color_func=lambda x: linkCols[x])
        plt.title(title, fontsize=12)
        
        if saveDescription != None:
            plt.savefig(saveDescription)
            plt.close(fig)
            return
        
        plt.show() #\
    

    def plotReachability(fosc: FOSC, partition: Optional[np.ndarray]=np.array([]), saveDescription: Optional[str]=None):
        """
        Plots a reachability plot.

        Parameters
        ----------
        fosc: FOSC
            The FOSC instance.
        partition: Optional[np.ndarray]
            The partition of the objects. If provided, the plot will be colored and the groups will stand out.
        """

        has_partition = partition.size

        def dict_to_tuple_list(input_dict):
            # print("input_dict", input_dict)
            for key, value in input_dict.items():
                if value == 0.0:
                    input_dict[key] = 'red'
                elif value == 1.0:
                    input_dict[key] = 'blue'
                elif value == 2.0:
                    input_dict[key] = 'yellow'
                elif value == 3.0:
                    input_dict[key] = 'green'
                elif value == 4.0:
                    input_dict[key] = 'pink'
                else:
                    input_dict[key] = 'error'
            
            input_dict[0] = 'white'

            return input_dict

        Z = fosc.getZ()
        fig = 0

        def create_bar_plot(x_labels, y_values, partition):
            global fig

            def create_graph(objects, cluster_labels):
                g = nx.Graph()
                for i in range(len(objects) - 1):
                    g.add_node(cluster_labels[objects[i]])
                    if(cluster_labels[objects[i]] != cluster_labels[objects[i + 1]]
                       and cluster_labels[objects[i]] != 0 and cluster_labels[objects[i + 1]] != 0):
                        g.add_edge(cluster_labels[objects[i]], cluster_labels[objects[i + 1]])
                return g

            if has_partition:
                cluster_labels = dict(enumerate(partition))
                g = create_graph(leaves, cluster_labels)
                coloring = nx.coloring.equitable_color(g, 4)
                coloring_list = dict_to_tuple_list(coloring)

                color_map = [coloring_list[cluster_labels[i]] for i in leaves]

            fig, ax = plt.subplots()
            bar_width = 1.0 / (len(x_labels) - 1)
            x_coordinates = [i for i in range(len(x_labels))]
            if has_partition:
                ax.bar(x=x_coordinates, height=y_values, align='edge', alpha=1.0, width=1.0, color=color_map)
            else:
                ax.bar(x=x_coordinates, height=y_values, align='edge', alpha=1.0, width=1.0)
            ax.set_ylabel('Distances')
            # ax.set_title('Reachability plot')
            ax.set_facecolor('lightgray')
            ax.get_xaxis().set_visible(False)
            plt.ylim(0, np.floor(max(y_values[1:])) + 5)
            plt.tight_layout()

            if has_partition:
                return cluster_labels

        dn = dendrogram(Z=Z, color_threshold=None, leaf_font_size=10, no_plot=True)
        leaves = dn['leaves']

        affected_clusters_by_level = fosc.ds.dicAffectedClustersByLevel # # accessing objects directly // change later?
        dic_nodes = fosc.ds.dicNodes # accessing objects directly // change later?

        def height_of_smallest_common_ancestor(leaf, leaf_ancestor):

            leaf_found = False
            leaf_ancestor_found = False        
            for dist, clusters in affected_clusters_by_level.items():
                for cluster in clusters:
                    if leaf in dic_nodes[cluster]:
                        leaf_found = True
                    if leaf_ancestor in dic_nodes[cluster]:
                        leaf_ancestor_found = True
                
                if leaf_found and leaf_ancestor_found:
                    return dist
                else:
                    leaf_found = False
                    leaf_ancestor_found = False
        
        distances = []
        for i in range(1, len(leaves)):
            distances.append(height_of_smallest_common_ancestor(leaves[i], leaves[i - 1]))
        distances.insert(0, np.floor(max(distances)) + 5) # convention for plotting
        
        x_labels = [f"x{i}" for i in leaves]

        if has_partition:
            cluster_labels = create_bar_plot(x_labels, distances, partition)
        else:
            create_bar_plot(x_labels, distances, partition)

        # Configure hover information using mplcursors
        cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(get_pixel_info(sel)))

        # Function to get pixel information
        def get_pixel_info(sel):
            x, y = int(sel.target[0]), int(sel.target[1])
            object = x_labels[x]
            distance = f"{distances[x]:.2f}" if x > 0 else 'inf'
            if has_partition:
                cluster = cluster_labels[leaves[x]]
                return f"Object: {object}\nDistance: {distance}\nCluster: {cluster}"
            else:
                return f"Object: {object}\nDistance: {distance}\n"

        if(saveDescription):
            plt.savefig(saveDescription, bbox_inches='tight', pad_inches=0)
            plt.close(fig)
        else:
            plt.show()


    def plotSilhouette(fosc: FOSC, partition: Optional[np.ndarray]=np.array([]), saveDescription: Optional[str]=None):
        """
        Plots a silhouette-like plot. 
        
        Parameters
        ----------
        fosc: FOSC
            The FOSC instance.
        partition: Optional[np.ndarray]
            The partition of the objects. If provided, the silhouettes are cutted, showing the groups extracted.
        saveDescription: Optional[str]
            The path to save the silhouette plot. If `None`, the plot will be shown interactively.
        """

        has_partition = partition.size
        distances = fosc.ds.getSignificantLevels()
        hierarchy_matrix = fosc.getHierarchyMatrix()
        # print("hierarchy_matrix", hierarchy_matrix, "\n")

        def dict_to_tuple_list(input_dict):

            for key, value in input_dict.items():
                if value == 0.0:
                    input_dict[key] = [255, 0, 0]
                elif value == 1.0:
                    input_dict[key] = [0, 0, 255]
                elif value == 2.0:
                    input_dict[key] = [255, 255, 0]
                elif value == 3.0:
                    input_dict[key] = [0, 255, 0]
                elif value == 4.0:
                    input_dict[key] = [255,192,203]
                else:
                    input_dict[key] = 'error'
            
            input_dict[0.0] = [192, 192, 192]

            return input_dict
        
        def create_graph(hierarchical_matrix):

            # Create a graph
            g = nx.Graph()

            def find_neighbors(i, j, matrix):
                if i == 0:
                    if j == 0:
                        return [matrix[i, j + 1], matrix[i + 1, j], matrix[i + 1, j + 1]]
                    elif j == matrix.shape[1] - 1:
                        return [matrix[i, j - 1], matrix[i + 1, j - 1], matrix[i + 1, j]]
                    else:
                        return [matrix[i, j - 1], matrix[i, j + 1], matrix[i + 1, j - 1], matrix[i + 1, j], matrix[i + 1, j + 1]]
                elif i == matrix.shape[0] - 1:
                    if j == 0:
                        return [matrix[i - 1, j], matrix[i - 1, j + 1], matrix[i, j + 1]]
                    elif j == matrix.shape[1] - 1:
                        return [matrix[i - 1, j - 1], matrix[i - 1, j], matrix[i, j - 1]]
                    else:
                        return [matrix[i - 1, j - 1], matrix[i - 1, j], matrix[i - 1, j + 1], matrix[i, j - 1], matrix[i, j + 1]]
                else:
                    if j == 0:
                        return [matrix[i - 1, j], matrix[i - 1, j + 1], matrix[i, j + 1], matrix[i + 1, j], matrix[i + 1, j + 1]]
                    elif j == matrix.shape[1] - 1:
                        return [matrix[i - 1, j - 1], matrix[i - 1, j], matrix[i, j - 1], matrix[i + 1, j - 1], matrix[i + 1, j]]
                    else:
                        return [matrix[i - 1, j - 1], matrix[i - 1, j], matrix[i - 1, j + 1], matrix[i, j - 1], matrix[i, j + 1],
                                matrix[i + 1, j - 1], matrix[i + 1, j], matrix[i + 1, j + 1]]
                
            for i in range(hierarchical_matrix.shape[0]):
                for j in range(hierarchical_matrix.shape[1]):
                    neighbors = find_neighbors(i, j, hierarchical_matrix)
                    for n in neighbors:
                        if n != hierarchical_matrix[i, j] and n != 0 and hierarchical_matrix[i, j] != 0:     
                            g.add_edge(hierarchical_matrix[i, j], n)
            
            return g
        
        def colored_matrix(matrix, colormap):
            
            # print("matrix\n", matrix, "\n")
            # print("colLabels\n", colLabels, "\n")

            rgb_matrix = np.zeros(matrix.shape + (3,), dtype=np.uint8)
            for i in range(matrix.shape[0]):
                for j in range(matrix.shape[1]):
                    if not has_partition:
                        rgb_matrix[i, j] = colormap[matrix[i, j]]
                    else:
                        if matrix[i, j] >= partition[colLabels[j] - 1]:
                            # print("if", f"matrix[{i},{j}]","==", f"partition[{colLabels[j] - 1}]")
                            rgb_matrix[i, j] = colormap[partition[colLabels[j] - 1]]
                        else:
                            rgb_matrix[i, j] = [192, 192, 192]
            
            return rgb_matrix

        num_rows, num_cols = hierarchy_matrix.shape

        rowLabels = [d for d in list(reversed(distances))]
        rowLabels.insert(0, 0.0)
        colLabels = [i for i in range(1, num_rows + 1)]

        rotated_matrix = np.rot90(hierarchy_matrix)
        # print("rotated_matrix", rotated_matrix, "\n")
        
        # Find permutation to reorder columns lexicographically
        indexes = np.lexsort(rotated_matrix)
        colLabels = [colLabels[i] for i in indexes]
        ordered_matrix = rotated_matrix[:, indexes]

        g = create_graph(ordered_matrix)
        coloring = nx.coloring.greedy_color(g, strategy="largest_first")
        coloring_list = dict_to_tuple_list(coloring)

        # Create a Matplotlib figure
        fig, ax = plt.subplots()
        im = ax.imshow(colored_matrix(ordered_matrix, coloring_list))

        ax.axis('off')
        def format_coord(x, y):
            x = int(x + 0.5)
            y = int(y + 0.5)
            if x >= 0 and y >= 0 and x < len(colLabels) and y < len(rowLabels):
                objct = colLabels[x]
                if not has_partition:
                    cluster = ordered_matrix[y, x]
                else:
                    if ordered_matrix[y, x] >= partition[objct - 1]:
                        cluster = partition[objct - 1]
                    else:
                        cluster = 0
                return f"Object: x{objct}\nDistance: {rowLabels[y]:.2f}\nCluster: {cluster:.0f}"
            else:
                return ""
        ax.format_coord = format_coord

        # ax.set_title('Silhouette plot')
        # Save the figure without white margins
        if(saveDescription):
            plt.savefig(saveDescription, bbox_inches='tight', pad_inches=0)
            plt.close(fig)
        else:
            plt.show()
        