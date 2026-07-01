import math
import numpy as np
from sklearn.cluster import DBSCAN

def perform_super_clustering(vehicles, eps=150, min_samples=3):
    """
    Performs DBSCAN clustering on vehicles and assigns CH/SCH roles.

    :param vehicles: List of Vehicle objects
    :param eps: DBSCAN max distance between two vehicles in the same cluster
    :param min_samples: Minimum vehicles to form a cluster
    """
    positions = np.array([[v.x, v.y] for v in vehicles])
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(positions)
    labels = db.labels_  # -1 means noise

    for v, cluster_id in zip(vehicles, labels):
        v.cluster_id = cluster_id
        v.is_ch = False
        v.is_sch = False

    unique_clusters = set(labels)
    if -1 in unique_clusters:
        unique_clusters.remove(-1)

    for cluster_id in unique_clusters:
        cluster_vehicles = [v for v in vehicles if v.cluster_id == cluster_id]
        if not cluster_vehicles:
            continue

        # Step 1: Assign Cluster Head (CH) as the geometric center
        ch = find_cluster_head(cluster_vehicles)
        ch.is_ch = True

        # Step 2: Assign SCHs at boundary (farthest from CH)
        assign_slave_cluster_heads(cluster_vehicles, ch)


def find_cluster_head(vehicles):
    """
    Returns the vehicle closest to the geometric center.
    """
    centroid_x = sum(v.x for v in vehicles) / len(vehicles)
    centroid_y = sum(v.y for v in vehicles) / len(vehicles)

    min_dist = float('inf')
    ch_vehicle = None
    for v in vehicles:
        dist = math.sqrt((v.x - centroid_x) ** 2 + (v.y - centroid_y) ** 2)
        if dist < min_dist:
            min_dist = dist
            ch_vehicle = v
    return ch_vehicle


def assign_slave_cluster_heads(vehicles, ch_vehicle, num_sch=2):
    """
    Assigns slave cluster heads (SCHs) as farthest from CH.
    """
    distances = [(v, math.sqrt((v.x - ch_vehicle.x)**2 + (v.y - ch_vehicle.y)**2))
                 for v in vehicles if v != ch_vehicle]
    distances.sort(key=lambda x: x[1], reverse=True)

    for i in range(min(num_sch, len(distances))):
        distances[i][0].is_sch = True
