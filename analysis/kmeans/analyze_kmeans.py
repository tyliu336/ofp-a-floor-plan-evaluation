import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INPUT_CSV = BASE_DIR / "forKmeans.csv"
FEATURES = ["TD", "EWR", "SA", "CAC", "RG"]
N_CLUSTERS = 10
RANDOM_STATE = 42
N_INIT = 50


def main() -> None:
    df = pd.read_csv(INPUT_CSV)
    id_col = df.columns[0]

    data = df.copy()
    data[FEATURES] = data[FEATURES].apply(pd.to_numeric, errors="coerce")

    missing_mask = data[FEATURES].isna().any(axis=1)
    if missing_mask.any():
        raise ValueError(
            f"Found {missing_mask.sum()} rows with missing feature values. "
            "Please clean data before running K-means."
        )

    X = data[FEATURES].to_numpy(dtype=float)

    kmeans = KMeans(
        n_clusters=N_CLUSTERS,
        random_state=RANDOM_STATE,
        n_init=N_INIT,
    )
    labels = kmeans.fit_predict(X)
    centers = kmeans.cluster_centers_

    clustered = data[[id_col] + FEATURES].copy()
    clustered["cluster"] = labels
    clustered.to_csv(BASE_DIR / "kmeans_clustered.csv", index=False)

    centroids = pd.DataFrame(centers, columns=FEATURES)
    centroids.insert(0, "cluster", np.arange(N_CLUSTERS))
    centroids.to_csv(BASE_DIR / "kmeans_centroids.csv", index=False)

    representatives = []
    for c in range(N_CLUSTERS):
        cluster_idx = np.where(labels == c)[0]
        cluster_points = X[cluster_idx]
        centroid = centers[c]

        distances = np.linalg.norm(cluster_points - centroid, axis=1)
        local_min_pos = int(np.argmin(distances))
        best_global_idx = int(cluster_idx[local_min_pos])

        representatives.append(
            {
                "cluster": c,
                id_col: data.loc[best_global_idx, id_col],
                "distance_to_centroid": float(distances[local_min_pos]),
                **{f: float(data.loc[best_global_idx, f]) for f in FEATURES},
            }
        )

    reps_df = pd.DataFrame(representatives)
    reps_df = reps_df[["cluster", id_col, "distance_to_centroid"] + FEATURES]
    reps_df.to_csv(BASE_DIR / "kmeans_representatives.csv", index=False)

    cluster_sizes = clustered["cluster"].value_counts().sort_index()
    print("K-means completed")
    print(f"Rows: {len(data)}")
    print(f"Features: {FEATURES}")
    print(f"Clusters: {N_CLUSTERS}")
    print(f"Inertia: {kmeans.inertia_:.6f}")
    print("Cluster sizes:")
    for cluster_id, size in cluster_sizes.items():
        print(f"  Cluster {cluster_id}: {size}")


if __name__ == "__main__":
    main()
