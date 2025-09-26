import shutil
import os
import shutil
from pyBat import SaveLoad
from pyBat import FileOperations
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.cluster.hierarchy as sch
from PIL import Image
from sklearn.cluster import KMeans
from sklearn.decomposition import FastICA
from sklearn.decomposition import PCA
from sklearn.manifold import MDS
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import pairwise_distances


# def read_png_folder(folder_path):
#     png_files = [file for file in os.listdir(folder_path) if file.endswith('.png')]
#     # Initialize an empty list to store image arrays
#     image_data = []
#     for index, png_file in enumerate(png_files):
#         # Read each image
#         image_path = os.path.join(folder_path, png_file)
#         with Image.open(image_path) as img:
#             # Convert the image to grayscale (optional, depending on use case)
#             img = img.convert('L')  # 'L' mode converts to grayscale
#             # Flatten the image to a 1D array
#             img_array = np.array(img).flatten()
#             image_data.append(img_array)
#         if index % 1000 == 0: print(f"Read {index} image of {len(png_files)}")
#     # Stack all image arrays into an n x m matrix
#     image_matrix = np.stack(image_data, axis=0)
#     return image_matrix, png_files



def hierarchical_clustering(data, method='ward', metric='euclidean', plot_dendrogram=True, num_clusters=None, simple=True):
    if not isinstance(data, np.ndarray):
        raise ValueError("Input data must be a numpy array.")

    if data.ndim != 2:
        raise ValueError("Input data must be a 2D array.")

    # Compute the linkage matrix
    linkage_matrix = sch.linkage(data, method=method, metric=metric)

    cluster_labels = None
    if num_clusters is not None:
        # Form flat clusters
        cluster_labels = sch.fcluster(linkage_matrix, t=num_clusters, criterion='maxclust')

    if plot_dendrogram:
        # Plot the dendrogram
        plt.figure(figsize=(10, 7))
        sch.dendrogram(linkage_matrix, labels=np.arange(data.shape[0]))
        plt.title("Hierarchical Clustering Dendrogram")
        plt.xlabel("Sample Index")
        plt.ylabel(f"{metric.capitalize()} Distance")
        plt.show()
    if simple: return cluster_labels
    return linkage_matrix, cluster_labels


def extract_png_metadata(folder_path):
    if not os.path.isdir(folder_path):
        raise ValueError(f"Invalid folder path: {folder_path}")
    png_files = [file for file in os.listdir(folder_path) if file.endswith('.png')]
    if not png_files:
        raise ValueError("No PNG files found in the folder.")
    metadata_list = []
    for png_file in png_files:
        try:
            image_path = os.path.join(folder_path, png_file)
            with Image.open(image_path) as img:
                metadata = img.info  # Extract metadata (PNG-specific info)
                metadata["filename"] = png_file  # Include filename
                metadata_list.append(metadata)
        except Exception as e:
            print(f"Error reading metadata from file {png_file}: {e}")
    # Convert list of dictionaries to a DataFrame
    if metadata_list:
        metadata_df = pd.DataFrame(metadata_list)
        return metadata_df
    else:
        raise ValueError("No metadata found in the images.")

def read_png_folder(folder_path, flatten=True):
    png_files = [file for file in os.listdir(folder_path) if file.endswith('.png')]
    # Initialize an empty list to store image arrays
    image_data = []
    for index, png_file in enumerate(png_files):
        # Read each image
        image_path = os.path.join(folder_path, png_file)
        with Image.open(image_path) as img:
            # Convert the image to grayscale (optional, depending on use case)
            img = img.convert('L')  # 'L' mode converts to grayscale
            img = np.array(img)
            if flatten:
                img_array = img.flatten()
            else:
                axis0 = np.min(img, axis=0)
                axis1 = np.min(img, axis=1)
                img_array = np.concatenate([axis0, axis1])
            image_data.append(img_array)
        if index > 0 and index % 100 == 0: print(f"Read {index + 1} image of {len(png_files)}")
    # Stack all image arrays into an n x m matrix
    print(f"Read {index + 1} image of {len(png_files)}")
    image_matrix = np.stack(image_data, axis=0)
    return image_matrix, png_files

def apply_pca(image_matrix, n_components):
    pca = PCA(n_components=n_components)
    # Fit and transform the image matrix
    reduced_matrix = pca.fit_transform(image_matrix)
    # Calculate cumulative explained variance
    explained_variance = np.cumsum(pca.explained_variance_ratio_) * 100  # Convert to percentage
    # Return results in a dictionary
    result = {'reduced_matrix': reduced_matrix, 'explained_variance': explained_variance,'pca_model': pca}
    return result

def apply_ica(image_matrix, n_components, simple=True):
    ica = FastICA(n_components=n_components, random_state=0)
    # Fit and transform the image matrix
    reduced_matrix = ica.fit_transform(image_matrix)
    # Extract the mixing matrix
    mixing_matrix = ica.mixing_
    # Return results in a dictionary
    if simple: return reduced_matrix
    result = {'reduced_matrix': reduced_matrix, 'mixing_matrix': mixing_matrix, 'ica_model': ica}
    return result

def visualize_distances(reduced_matrix, metric='euclidean'):
    # Step 1: Compute the pairwise distance matrix
    distances = pairwise_distances(reduced_matrix, metric=metric)
    # Step 2: Apply MDS to embed distances into 2D space
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=0)
    embedding = mds.fit_transform(distances)
    # Step 3: Create a scatter plot
    plt.figure(figsize=(8, 6))
    plt.scatter(embedding[:, 0], embedding[:, 1], c='blue', alpha=0.7, s=50)
    plt.title("Scatter Plot of Distances (MDS Embedding)")
    plt.xlabel("MDS Dimension 1")
    plt.ylabel("MDS Dimension 2")
    plt.grid(True)
    plt.show()
    return distances, embedding

def visualize_with_tsne(reduced_matrix, perplexity=30, learning_rate=200, n_iter=1000, random_state=0, n_clusters=5):
    tsne = TSNE(n_components=2, perplexity=perplexity, learning_rate=learning_rate, n_iter=n_iter, random_state=random_state)
    tsne_embedding = tsne.fit_transform(reduced_matrix)
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    cluster_labels = kmeans.fit_predict(tsne_embedding)
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(tsne_embedding[:, 0], tsne_embedding[:, 1], c=cluster_labels, cmap='jet', alpha=0.7, s=50)
    #for i, (x, y) in enumerate(tsne_embedding):
    #    plt.text(x, y, str(i), fontsize=8, ha='right', va='bottom', color='red')
    plt.title("t-SNE with K-Means Clusters")
    plt.xlabel("t-SNE Dimension 1")
    plt.ylabel("t-SNE Dimension 2")
    plt.colorbar(scatter, label='Cluster')
    plt.grid(True)
    plt.show()
    return tsne_embedding, cluster_labels

def sort_images_by_cluster(basefile_names, base_path, cluster_labels, output_folder):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    for basefile_name, cluster_label in zip(basefile_names, cluster_labels):
        cluster_folder = os.path.join(output_folder, f"cluster_{cluster_label}")
        os.makedirs(cluster_folder, exist_ok=True)
        shutil.copy(os.path.join(base_path, basefile_name), cluster_folder)
####################################################################################################################
####################################################################################################################

read_files = False

folder = "/media/dieter/DataLinux/processed_audio/2024_03_17_Ind03/spectrograms"
clustered_spectrograms = '/media/dieter/DataLinux/processed_audio/2024_03_17_Ind03/clustered_spectrograms'

matrix_file = 'transform_steps/matrix.pkl'
files_file = 'transform_steps/files.pkl'
meta_file = 'transform_steps/meta.pkl'
reduced_file = 'transform_steps/reduced.pkl'

matrix_exists = FileOperations.check_file_exists(matrix_file)
files_exists = FileOperations.check_file_exists(files_file)
meta_exists = FileOperations.check_file_exists(meta_file)
reduced_exists = FileOperations.check_file_exists(reduced_file)

if matrix_exists:
    matrix = SaveLoad.pickle_load(matrix_file)
    files = SaveLoad.pickle_load(files_file)
    meta = SaveLoad.pickle_load(meta_file)
else:
    matrix, files = read_png_folder(folder)
    meta = extract_png_metadata(folder)
    SaveLoad.pickle_save(matrix_file, matrix)
    SaveLoad.pickle_save(files_file, files)
    SaveLoad.pickle_save(meta_file, meta)

if reduced_exists:
    reduced = SaveLoad.pickle_load(reduced_file)
else:
    reduced = apply_pca(matrix, 150)

reduced_matrix = reduced['reduced_matrix']
clusters = hierarchical_clustering(reduced_matrix, plot_dendrogram=False, num_clusters=3)
sort_images_by_cluster(files, folder, clusters, clustered_spectrograms)
meta['cluster'] = clusters
meta['dummy'] = 1
#%%

selected = meta.query('cluster in [0, 1, 2, 3]')
grouped = selected.groupby(['channel_idx'])
counts = grouped.agg({'dummy': 'count'})
counts = counts.reset_index()
# sort counts on the channel_idx
counts['channel_idx'] = pd.to_numeric(counts['channel_idx'], errors='coerce')
counts = counts.sort_values(by='channel_idx')


#PLot a bar chart of the channel_idx and counts (dummy)
plt.figure(figsize=(10, 7))
plt.bar(counts['channel_idx'], counts['dummy'])
plt.xlabel('Channel Index')
plt.ylabel('Number of Spectrograms')
plt.title('Number of Spectrograms per Channel')
plt.grid(axis='y')
plt.show()


