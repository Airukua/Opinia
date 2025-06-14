# ------------------------------------------------------------------------------
# MIT License
# Copyright (c) 2025 Abdul Wahid Rukua
#
# This code is open-source under the MIT License.
# See LICENSE file in the root of the repository for full license information.
# ------------------------------------------------------------------------------

import numpy as np
import hdbscan
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

class HDBSCANClusterer:
    """
    Wrapper class for HDBSCAN clustering algorithm.

    Parameters
    ----------
    min_cluster_size : int, optional
        The minimum size of clusters.
    min_samples : int, optional
        The number of samples in a neighborhood for a point to be considered a core point.
    cluster_selection_epsilon : float, default=0.0
        A distance threshold for cluster selection. Clusters below this threshold are merged.
    metrics : str, default='jaccard'
        Distance metric to use with HDBSCAN.
    """

    def __init__(self, min_cluster_size=None, min_samples=None, cluster_selection_epsilon=0.0, metrics='jaccard'):
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.cluster_selection_epsilon = cluster_selection_epsilon
        self.metrics = metrics
        self.model = None
        self.data = None

    def fit(self, data):
        """
        Fit the HDBSCAN model to the data.

        Parameters
        ----------
        data : array-like, shape (n_samples, n_features)
            Input data to cluster.

        Returns
        -------
        model : hdbscan.HDBSCAN
            The fitted HDBSCAN model instance.
        """
        self.data = data  
        self.model = hdbscan.HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
            cluster_selection_epsilon=self.cluster_selection_epsilon,
            metric=self.metrics
        ).fit(data)
        return self.model

    def evaluate(self):
        """
        Evaluate clustering results and return cluster statistics.

        Returns
        -------
        dict
            Contains number of clusters, number of noise points,
            cluster sizes, and label assignments.
        """
        if self.model is None:
            raise ValueError("Model has not been fitted yet. Call 'fit' before 'evaluate'.")

        labels = self.model.labels_
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = np.sum(labels == -1)
        cluster_sizes = {
            label: np.sum(labels == label)
            for label in set(labels) if label != -1
        }

        print(f"Number of clusters: {n_clusters}")
        print(f"Number of noise points: {n_noise}")
        print("Cluster sizes:")
        for cluster_label, size in cluster_sizes.items():
            print(f"  Cluster {cluster_label}: {size} points")

        return {
            "n_clusters": n_clusters,
            "n_noise": n_noise,
            "cluster_sizes": cluster_sizes,
            "labels": labels
        }

    def hyperparameter_search(self, data, min_cluster_sizes, min_samples_list):
        """
        Perform a simple grid search over min_cluster_size and min_samples parameters.

        Parameters
        ----------
        data : array-like of shape (n_samples, n_features)
            Input data to perform clustering on.
        min_cluster_sizes : list of int
            List of candidate values for min_cluster_size.
        min_samples_list : list of int
            List of candidate values for min_samples.

        Returns
        -------
        dict
            Best parameter combination found and corresponding cluster statistics.
        """
        best_result = None

        for min_cluster_size in min_cluster_sizes:
            for min_samples in min_samples_list:
                try:
                    model = hdbscan.HDBSCAN(
                        min_cluster_size=min_cluster_size,
                        min_samples=min_samples,
                        cluster_selection_epsilon=self.cluster_selection_epsilon,
                        metric=self.metrics
                    ).fit(data)

                    labels = model.labels_
                    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                    n_noise = np.sum(labels == -1)

                    print(f"min_cluster_size={min_cluster_size}, min_samples={min_samples} => "
                          f"{n_clusters} clusters, {n_noise} noise points")

                    if best_result is None or \
                       n_clusters > best_result['n_clusters'] or \
                       (n_clusters == best_result['n_clusters'] and n_noise < best_result['n_noise']):
                        best_result = {
                            'min_cluster_size': min_cluster_size,
                            'min_samples': min_samples,
                            'n_clusters': n_clusters,
                            'n_noise': n_noise
                        }
                except Exception as e:
                    print(f"Error with min_cluster_size={min_cluster_size}, min_samples={min_samples}: {e}")

        print(f"\nBest Parameters: {best_result}")
        return best_result

    def visualize(self):
        """
        Visualize the clustering results using PCA for dimensionality reduction.

        Returns
        -------
        None
        """
        if self.model is None or self.data is None:
            raise ValueError("Model has not been fitted or data is not available.")

        labels = self.model.labels_
        pca = PCA(n_components=2)
        try:
            reduced_data = pca.fit_transform(self.data)
        except Exception as e:
            raise ValueError(f"Error reducing dimensionality with PCA: {e}")

        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=labels, cmap='Spectral', s=50)
        plt.colorbar(scatter, label='Cluster Label')
        plt.title('HDBSCAN Clustering Results')
        plt.xlabel('PCA Component 1')
        plt.ylabel('PCA Component 2')
        plt.show()
