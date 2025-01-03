from Trackrefiner.correction.modelTraning.mlModelDivisionVsNonDivision import train_division_vs_non_division_model
from Trackrefiner.correction.modelTraning.mlModelNonDividedBacteria import train_non_divided_bacteria_model
from Trackrefiner.correction.modelTraning.mlModelDividedBacteria import train_divided_bacteria_model


def train_bacterial_behavior_models(df, neighbors_df, neighbor_list_array, center_coord_cols, parent_image_number_col,
                                    parent_object_number_col, output_directory, clf, n_cpu, coordinate_array):

    """
    Trains machine learning models to predict bacterial behaviors, including division, non-division,
    and distinguishing between divided and non-divided bacteria.

    :param pandas.DataFrame df:
        DataFrame containing bacterial tracking data with spatial, temporal, and neighbor information.
    :param pandas.DataFrame neighbors_df:
        DataFrame containing bacterial neighbor relationships for all time steps.
    :param csr_matrix neighbor_list_array:
        Sparse matrix representing neighbor relationships for efficient lookup.
    :param dict center_coord_cols:
        Dictionary specifying the column names for x and y coordinates of bacterial centroids
        (e.g., `{"x": "Center_X", "y": "Center_Y"}`).
    :param str parent_image_number_col:
        Column name representing the image number of parent bacteria.
    :param str parent_object_number_col:
        Column name representing the object number of parent bacteria.
    :param str output_directory:
        Directory to save the trained models and performance logs.
    :param str clf:
        Classifier type (e.g., `'LogisticRegression'`, `'GaussianProcessClassifier'`, `'SVC'`).
    :param int n_cpu:
        Number of CPUs to use for parallel processing during model training.
    :param np.ndarray coordinate_array:
        Array of spatial coordinates for evaluating bacterial connections.

    **Returns**:
        tuple: Three trained machine learning models:
            - **divided_vs_non_divided_model**: Model to distinguish between dividing and non-dividing bacteria.
            - **non_divided_model**: Model to predict the behavior of non-dividing bacteria.
            - **divided_bac_model**: Model to analyze the characteristics of dividing bacteria.
    """

    # first of all we should fine continues life history
    # inner: for removing unexpected beginning bacteria
    # also unexpected end bacteria removed

    important_cols = ['ImageNumber', 'ObjectNumber', 'unexpected_end', 'unexpected_beginning', 'bad_daughters_flag',
                      parent_image_number_col, parent_object_number_col,
                      'LengthChangeRatio', 'index', 'prev_index',
                      'common_neighbors', 'difference_neighbors',
                      'direction_of_motion', 'MotionAlignmentAngle',
                      center_coord_cols['x'], center_coord_cols['y'],
                      'endpoint1_X', 'endpoint1_Y', 'endpoint2_X', 'endpoint2_Y',
                      'daughter_length_to_mother', 'daughter_mother_LengthChangeRatio',
                      'AreaShape_MajorAxisLength', 'other_daughter_index', 'id', 'parent_id', 'age', 'bacteria_slope']

    connected_bac = df[important_cols].merge(
        df[important_cols], left_on=[parent_image_number_col, parent_object_number_col],
        right_on=['ImageNumber', 'ObjectNumber'], how='inner', suffixes=('', '_prev'))

    target_bac_with_neighbors = connected_bac.merge(neighbors_df, left_on=['ImageNumber', 'ObjectNumber'],
                                                    right_on=['First Image Number', 'First Object Number'], how='left')

    target_bac_with_neighbors_info = \
        target_bac_with_neighbors.merge(df[['ImageNumber', 'ObjectNumber', 'unexpected_beginning']],
                                        left_on=['Second Image Number', 'Second Object Number'],
                                        right_on=['ImageNumber', 'ObjectNumber'], how='left',
                                        suffixes=('', '_neighbor_target'))

    bad_daughters_target = \
        target_bac_with_neighbors_info.loc[(target_bac_with_neighbors_info['bad_daughters_flag'] == True)]

    connected_bac_high_chance_to_be_correct = \
        connected_bac.loc[(~ connected_bac['index'].isin(bad_daughters_target['index'].values))]

    # now we should check daughters and remove division with one daughter (due to neighboring to unexpected end and
    # unexpected beginning)
    division = \
        connected_bac_high_chance_to_be_correct.loc[
            ~ connected_bac_high_chance_to_be_correct['daughter_length_to_mother_prev'].isna()]

    # sometimes it can be possible one daughter filtered in prev steps and the other daughter is existing
    # I want to remove another daughter
    mother_with_two_daughters = division.duplicated(subset=[parent_image_number_col, parent_object_number_col],
                                                    keep=False)
    mother_with_one_daughter = ~ mother_with_two_daughters
    division_with_one_daughter = division[mother_with_one_daughter]

    connected_bac_high_chance_to_be_correct = \
        connected_bac_high_chance_to_be_correct.loc[~ connected_bac_high_chance_to_be_correct['index'].isin(
            division_with_one_daughter['index'].values)]

    divided_vs_non_divided_model = \
        train_division_vs_non_division_model(connected_bac_high_chance_to_be_correct,
                                             center_coord_cols, parent_image_number_col,
                                             parent_object_number_col, output_directory, clf, n_cpu, coordinate_array)

    connected_bac_high_chance_to_be_correct_with_neighbors = \
        connected_bac_high_chance_to_be_correct.merge(neighbors_df, left_on=['ImageNumber_prev', 'ObjectNumber_prev'],
                                                      right_on=['First Image Number', 'First Object Number'],
                                                      how='left')

    connected_bac_high_chance_to_be_correct_with_neighbors_info = \
        connected_bac_high_chance_to_be_correct_with_neighbors.merge(
            df[important_cols], left_on=['Second Image Number', 'Second Object Number'],
            right_on=['ImageNumber', 'ObjectNumber'], how='left', suffixes=('', '_prev_neighbor'))

    non_divided_model = \
        train_non_divided_bacteria_model(df, connected_bac_high_chance_to_be_correct_with_neighbors_info,
                                         neighbors_df, neighbor_list_array, center_coord_cols,
                                         parent_image_number_col, parent_object_number_col, output_directory,
                                         clf, n_cpu, coordinate_array)

    divided_bac_model = \
        train_divided_bacteria_model(df, connected_bac_high_chance_to_be_correct_with_neighbors_info,
                                     neighbor_list_array, center_coord_cols,
                                     parent_image_number_col, parent_object_number_col, output_directory,
                                     clf, n_cpu, coordinate_array)

    return divided_vs_non_divided_model, non_divided_model, divided_bac_model
