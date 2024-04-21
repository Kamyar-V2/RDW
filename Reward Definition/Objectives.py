
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import NearestNeighbors
from scipy.ndimage import distance_transform_edt
from atomai.transforms import datatransform
from sklearn.decomposition import PCA
from skimage.morphology import disk, dilation
from skimage.measure import label, regionprops


### Define Oracle

model_load = aoi.load_model("/content/abc.tar")
nn_output, coordinates = model_load.predict(image)
Oracle = len(coordinates[0])


### Analysis of atoms via optimized LoG 

def Quality_count(params):
    min_sigma, max_sigma, threshold, overlap = params
    coms, log_count = apply_log(min_sigma, max_sigma, threshold, overlap)

    difference = abs((log_count - Oracle)/Oracle)

    return difference


def Error_count(params):
    min_sigma, max_sigma, threshold, overlap = params

    # Assume apply_log is defined elsewhere and returns coordinates and log_count
    coms, log_count = apply_log(min_sigma, max_sigma, threshold, overlap)

    # Safeguard for n_neighbors to not exceed number of samples
    n_neighbors = min(len(coms), 5)  # Ensure n_neighbors does not exceed the number of samples in coms

    # Calculate the sum of distances to the nearest neighbors for each point
    if n_neighbors > 1:  # Proceed only if there are at least 2 points (1 neighbor besides itself)
        nbrs = NearestNeighbors(n_neighbors=n_neighbors, algorithm='ball_tree').fit(coms)
        distances, _ = nbrs.kneighbors(coms)
        sum_of_distances = np.sum(distances[:, 1:], axis=1)  # Exclude the distance to itself (first column)
    else:
        sum_of_distances = np.array([0] * len(coms))  # If only 1 sample, the sum of distances is 0

    # Count points with the sum of distances below a certain threshold
    points_below_threshold = np.sum(sum_of_distances < 30)

    normalized_points = points_below_threshold / Oracle  # Assuming Oracle_A is defined and non-zero

    return normalized_points


### GMM clustering Reward driven

def Fit_GMM(threshold, covariance_type):

    imstack_grid = imstack_final
    # Fit a GMM to the reduced data
    flattened_imstack_grid = imstack_grid.reshape(imstack_grid.shape[0], -1)
    pca = PCA(n_components=2)
    reduced_data = pca.fit_transform(flattened_imstack_grid)

    gmm = GaussianMixture(n_components=2, covariance_type=covariance_type, random_state=42)
    gmm.fit(reduced_data)
    probabilities = gmm.predict_proba(reduced_data)

    # Identify the 'amorphous' cluster
    centroids = gmm.means_
    amorphous_cluster_index = np.argmax(centroids[:, 0])

    # Determine membership based on the threshold
    amorphous_membership_mask = probabilities[:, amorphous_cluster_index] > threshold

    # Assign colors based on membership
    colors = np.where(amorphous_membership_mask, 'red', 'blue')

    return colors, reduced_data

def analyze_image(window_size, threshold, covariance_type):

    # Fit a GMM to classify the detected features
    colors, reduced_data = Fit_GMM(threshold, covariance_type)

    #com_grid, imstack_grid , coms = Apply_LoG(window_size)
    # Create binary masks and calculate normalized amorphous area and perimeter
    normalized_amorphous_area, normalized_amorphous_perimeter = create_binary_masks_and_label(colors, window_size)

    return normalized_amorphous_area, normalized_amorphous_perimeter


def calculate_compactness(normalized_amorphous_perimeter, normalized_amorphous_area):

    perimeter = normalized_amorphous_perimeter
    area = normalized_amorphous_area

    comp = area / (perimeter ** 2)

    return comp, perimeter