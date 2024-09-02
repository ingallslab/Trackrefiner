import pandas as pd


def calculate_intersections_and_unions(df, col1, col2):

    df['intersection'] = df[col1].values & df[col2].values
    df['union'] = df[col1].values | df[col2].values

    df['intersection'] = df['intersection'].map(len)
    df['union'] = df['union'].map(len)

    df['intersection'] = df['intersection'].astype('int64')
    df['union'] = df['union'].astype('int64')

    df['iou'] = df['intersection'] / df['union']

    return df


def calculate_intersections_and_unions_division(df, col1, col2):

    df['intersection'] = df[col1].values & df[col2].values
    df['intersection'] = df['intersection'].map(len)

    # Calculate unique areas for mask 2 (daughter)
    df['unique_masks2'] = df[col2] - df[col1]
    df['unique_masks2'] = df['unique_masks2'].map(len)

    df['intersection'] = df['intersection'].astype('int64')
    df['unique_masks2'] = df['unique_masks2'].astype('int64')

    # Calculate IoU based on daughter_flag
    df['iou'] = df['intersection'] / (df['intersection'] + df['unique_masks2'])

    return df


def find_overlap_mother_bad_daughters(mother_bad_daughters_df):
    # Calculate intersection by merging on coordinates
    mother_bad_daughters_df = \
        calculate_intersections_and_unions(mother_bad_daughters_df, 'coordinate_mother',
                                           'coordinate_daughter')

    # Pivot this DataFrame to get the desired structure
    overlap_df = \
        mother_bad_daughters_df[['index_mother', 'index_daughter', 'iou']].pivot(index='index_mother',
                                                                                 columns='index_daughter',
                                                                                 values='iou')
    overlap_df.columns.name = None
    overlap_df.index.name = None
    overlap_df = overlap_df.astype(float)

    return overlap_df


def find_overlap_object_for_division_chance(source_with_candidate_neighbors, center_coordinate_columns, col1, col2,
                                            daughter_flag=False):
    if daughter_flag:
        # Calculate intersection by merging on coordinates
        source_with_candidate_neighbors = \
            calculate_intersections_and_unions_division(source_with_candidate_neighbors,
                                                        'coordinate' + col1, 'coordinate' + col2)
    else:
        # Calculate intersection by merging on coordinates
        source_with_candidate_neighbors = \
            calculate_intersections_and_unions(source_with_candidate_neighbors,
                                               'coordinate' + col1, 'coordinate' + col2)

    # Pivot this DataFrame to get the desired structure
    overlap_df = \
        source_with_candidate_neighbors[['index' + col1, 'index' + col2,
                                         'iou']].pivot(index='index' + col1, columns='index' + col2, values='iou')

    overlap_df.columns.name = None
    overlap_df.index.name = None
    overlap_df = overlap_df.astype(float)

    return overlap_df


def find_overlap_object_to_next_frame(current_df, selected_objects, next_df, selected_objects_in_next_time_step,
                                      center_coordinate_columns, daughter_flag=False):

    if len(current_df['color_mask'].values.tolist()) != len(set(current_df['color_mask'].values.tolist())):
        print(current_df['ImageNumber'].values[0])
        breakpoint()

    if len(next_df['color_mask'].values.tolist()) != len(set(next_df['color_mask'].values.tolist())):
        print(next_df['ImageNumber'].values[0])
        breakpoint()

    product_df = pd.merge(
        selected_objects.reset_index(),
        selected_objects_in_next_time_step.reset_index(),
        how='cross',
        suffixes=('_current', '_next')
    )
    product_df[['index_current', 'index_next']] = product_df[['index_current', 'index_next']].astype('int64')
    product_df[[center_coordinate_columns['x'] + '_current',
                center_coordinate_columns['y'] + '_current',
                center_coordinate_columns['x'] + '_next',
                center_coordinate_columns['y'] + '_next',
                'endpoint1_X_current', 'endpoint1_Y_current',
                'endpoint2_X_current', 'endpoint2_Y_current',
                'endpoint1_X_next', 'endpoint1_Y_next',
                'endpoint2_X_next', 'endpoint2_Y_next']] = (
        product_df[[center_coordinate_columns['x'] + '_current', center_coordinate_columns['y'] + '_current',
                    center_coordinate_columns['x'] + '_next', center_coordinate_columns['y'] + '_next',
                    'endpoint1_X_current', 'endpoint1_Y_current',
                    'endpoint2_X_current', 'endpoint2_Y_current',
                    'endpoint1_X_next', 'endpoint1_Y_next',
                    'endpoint2_X_next', 'endpoint2_Y_next'
                    ]].astype('float64'))

    if daughter_flag:
        # Calculate intersection by merging on coordinates
        product_df = \
            calculate_intersections_and_unions_division(product_df, 'coordinate_current', 'coordinate_next')
    else:
        # Calculate intersection by merging on coordinates
        product_df = calculate_intersections_and_unions(product_df, 'coordinate_current', 'coordinate_next')

    # Pivot this DataFrame to get the desired structure
    overlap_df = \
        product_df[['index_current', 'index_next', 'iou']].pivot(index='index_current', columns='index_next',
                                                                 values='iou')

    overlap_df.columns.name = None
    overlap_df.index.name = None
    overlap_df = overlap_df.astype(float)

    return overlap_df, product_df


def find_overlap_object_to_next_frame_maintain(division_df, same_df):
    if division_df.shape[0] > 0:
        division_df = calculate_intersections_and_unions_division(division_df, 'coordinate_parent',
                                                                  'coordinate_daughter')

        # Pivot this DataFrame to get the desired structure
        division_overlap = division_df[['index_parent', 'index_daughter', 'iou']].pivot(index='index_parent',
                                                                                        columns='index_daughter',
                                                                                        values='iou')

    if same_df.shape[0] > 0:
        same_df = calculate_intersections_and_unions(same_df, 'coordinate_1', 'coordinate_2')
        same_df_overlap = same_df[['index_1', 'index_2', 'iou']].pivot(index='index_1', columns='index_2', values='iou')

    if division_df.shape[0] > 0 and same_df.shape[0] > 0:
        overlap_df = pd.concat([division_overlap, same_df_overlap], axis=0)
    elif division_df.shape[0] > 0:
        overlap_df = division_overlap
    elif same_df.shape[0] > 0:
        overlap_df = same_df_overlap
    else:
        breakpoint()

    overlap_df.columns.name = None
    overlap_df.index.name = None
    overlap_df = overlap_df.astype(float)

    return overlap_df


def find_overlap_object_to_next_frame_unexpected(final_candidate_bac):

    if final_candidate_bac.shape[0] > 0:

        final_candidate_bac = calculate_intersections_and_unions(final_candidate_bac, 'coordinate',
                                                                 'coordinate_candidate')

    overlap_df = final_candidate_bac[['index', 'index_candidate', 'iou']].pivot(
        index='index', columns='index_candidate', values='iou')
    overlap_df.columns.name = None
    overlap_df.index.name = None
    overlap_df = overlap_df.astype(float)

    return overlap_df