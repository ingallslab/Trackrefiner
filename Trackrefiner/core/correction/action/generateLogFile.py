import pandas as pd


def find_noise_bac(raw_df, final_df, logs_list, parent_image_number_col, parent_object_number_col):
    noise_bac_df = raw_df.loc[~ raw_df['prev_index'].isin(final_df['prev_index'])].copy()
    noise_bac_df['NoiseObject'] = True
    noise_bac_df['TrackingLinkModified'] = False
    noise_bac_df['UnexpectedEnd_by_CellProfiler'] = False
    noise_bac_df['UnexpectedEnd_by_Trackrefiner'] = False
    noise_bac_df['UnexpectedBeginning_by_CellProfiler'] = False
    noise_bac_df['UnexpectedBeginning_by_Trackrefiner'] = False

    noise_bac_df[[parent_image_number_col, parent_object_number_col, 'id', 'parent_id']] = 0

    msg = '\nTotal Number of Noise Objects: ' + str(noise_bac_df.shape[0])
    logs_list.append(msg)

    return noise_bac_df, logs_list


def find_unexpected_beginning(final_df, raw_df, logs_list):
    unexpected_beginning_bac_df = final_df.loc[final_df['Unexpected_Beginning']].copy()

    unexpected_beginning_bac_df['ub_index'] = unexpected_beginning_bac_df.index
    unexpected_beginning_bac_df['NoiseObject'] = False
    unexpected_beginning_bac_df['TrackingLinkModified'] = False
    unexpected_beginning_bac_df['UnexpectedBeginning_by_CellProfiler'] = True
    unexpected_beginning_bac_df['UnexpectedBeginning_by_Trackrefiner'] = False
    unexpected_beginning_bac_df['UnexpectedEnd_by_CellProfiler'] = False
    unexpected_beginning_bac_df['UnexpectedEnd_by_Trackrefiner'] = False

    # now we should find which UB made by TR and which one by CP
    merged_dfs = unexpected_beginning_bac_df.merge(raw_df, on=['ImageNumber', 'ObjectNumber'],
                                                   suffixes=('_1', '_2'))

    # it means in raw df, object was not ub
    ub_made_by_tr = merged_dfs.loc[merged_dfs['Unexpected_Beginning_2'] == False]
    unexpected_beginning_bac_df.loc[ub_made_by_tr['ub_index'].values, 'UnexpectedBeginning_by_Trackrefiner'] = True
    unexpected_beginning_bac_df.loc[ub_made_by_tr['ub_index'].values, 'UnexpectedBeginning_by_CellProfiler'] = False

    msg = ('Total Number of Unexpected Beginning Bacteria Generated by TrackRefiner or CellProfiler: '
           + str(unexpected_beginning_bac_df.shape[0]))
    logs_list.append(msg)

    msg = ('Total Number of Unexpected Beginning Bacteria Generated by TrackRefiner: '
           + str(unexpected_beginning_bac_df.loc[
                     unexpected_beginning_bac_df['UnexpectedBeginning_by_Trackrefiner'] == True].shape[0]))
    logs_list.append(msg)

    msg = ('Total Number of Unexpected Beginning Bacteria Generated by CellProfiler: '
           + str(unexpected_beginning_bac_df.loc[
                     unexpected_beginning_bac_df['UnexpectedBeginning_by_CellProfiler'] == True].shape[0]))
    logs_list.append(msg)

    return unexpected_beginning_bac_df, logs_list


def find_unexpected_end(final_df, raw_df, logs_list):
    unexpected_end_bac_df = final_df.loc[final_df['Unexpected_End']].copy()

    unexpected_end_bac_df['ue_index'] = unexpected_end_bac_df.index

    unexpected_end_bac_df['NoiseObject'] = False
    unexpected_end_bac_df['TrackingLinkModified'] = False
    unexpected_end_bac_df['UnexpectedBeginning_by_CellProfiler'] = False
    unexpected_end_bac_df['UnexpectedBeginning_by_Trackrefiner'] = False

    unexpected_end_bac_df['UnexpectedEnd_by_CellProfiler'] = True
    unexpected_end_bac_df['UnexpectedEnd_by_Trackrefiner'] = False

    # now we should find which UB made by TR and which one by CP
    merged_dfs = unexpected_end_bac_df.merge(raw_df, on=['ImageNumber', 'ObjectNumber'], suffixes=('_1', '_2'))

    # it means in raw df, object was not ub
    ue_made_by_tr = merged_dfs.loc[merged_dfs['Unexpected_End_2'] == False]
    unexpected_end_bac_df.loc[ue_made_by_tr['ue_index'].values, 'UnexpectedEnd_by_Trackrefiner'] = True
    unexpected_end_bac_df.loc[ue_made_by_tr['ue_index'].values, 'UnexpectedEnd_by_CellProfiler'] = False

    msg = ('Total Number of Unexpected End Bacteria Generated by TrackRefiner or CellProfiler: ' +
           str(unexpected_end_bac_df.shape[0]))
    logs_list.append(msg)

    msg = ('Total Number of Unexpected End Bacteria Generated by TrackRefiner: ' +
           str(unexpected_end_bac_df.loc[unexpected_end_bac_df['UnexpectedEnd_by_Trackrefiner'] == True].shape[0]))
    logs_list.append(msg)

    msg = ('Total Number of Unexpected End Bacteria Generated by CellProfiler: ' +
           str(unexpected_end_bac_df.loc[unexpected_end_bac_df['UnexpectedEnd_by_CellProfiler'] == True].shape[0]))
    logs_list.append(msg)

    return unexpected_end_bac_df, logs_list


def bacteria_with_change_relation(raw_df, final_df, logs_list, parent_image_number_col, parent_object_number_col):
    merged_df = raw_df.merge(final_df, on='prev_index', how='inner', suffixes=('_raw', ''))

    identified_tracking_errors_df = \
        merged_df.loc[
            (merged_df[parent_image_number_col + '_raw'] !=
             merged_df[parent_image_number_col]) |
            (merged_df[parent_object_number_col + '_raw'] !=
             merged_df[parent_object_number_col])].copy()

    identified_tracking_errors_df['NoiseObject'] = False
    identified_tracking_errors_df['TrackingLinkModified'] = True
    identified_tracking_errors_df['UnexpectedBeginning_by_CellProfiler'] = False
    identified_tracking_errors_df['UnexpectedBeginning_by_Trackrefiner'] = False

    identified_tracking_errors_df['UnexpectedEnd_by_CellProfiler'] = False
    identified_tracking_errors_df['UnexpectedEnd_by_Trackrefiner'] = False

    changed_link_to_come_ub = \
        identified_tracking_errors_df.loc[identified_tracking_errors_df[parent_image_number_col] == 0]

    identified_tracking_errors_df.loc[
        changed_link_to_come_ub.index.values, 'UnexpectedBeginning_by_Trackrefiner'] = True

    msg = 'Total Number of Bacteria with Modified Links: ' + str(identified_tracking_errors_df.shape[0])
    logs_list.append(msg)

    msg = ('Total Number of Bacteria with Modified Links Excluding Unexpected Beginnings: ' +
           str(identified_tracking_errors_df.loc[identified_tracking_errors_df[parent_image_number_col] != 0].shape[0]))
    logs_list.append(msg)

    msg = ('Total Number of Bacteria with Modified Links Limited to Unexpected Beginnings: ' +
           str(identified_tracking_errors_df.loc[
                   identified_tracking_errors_df[parent_image_number_col] == 0].shape[0])) + '\n'
    logs_list.append(msg)

    return identified_tracking_errors_df, logs_list


def generate_log_file(raw_df, final_df, logs_list, parent_image_number_col, parent_object_number_col,
                      center_coordinate_columns):
    # find noise objects
    noise_bac_df, logs_list = find_noise_bac(raw_df, final_df, logs_list, parent_image_number_col,
                                             parent_object_number_col)

    # find unexpected beginning
    unexpected_beginning_bac_df, logs_list = find_unexpected_beginning(final_df, raw_df, logs_list)

    # find unexpected end bacteria
    unexpected_bac_df, logs_list = find_unexpected_end(final_df, raw_df, logs_list)

    # now we should merge dataframes
    # noise_bac	unexpected_end	unexpected_beginning	changed
    merged_ub_bac_ue_bac = \
        unexpected_beginning_bac_df[
            ['ImageNumber', 'ObjectNumber', center_coordinate_columns['x'], center_coordinate_columns['y'],
             'AreaShape_MajorAxisLength', parent_image_number_col, parent_object_number_col, 'id', 'parent_id',
             'NoiseObject', 'UnexpectedEnd_by_CellProfiler', 'UnexpectedEnd_by_Trackrefiner',
             'UnexpectedBeginning_by_CellProfiler', 'UnexpectedBeginning_by_Trackrefiner', 'TrackingLinkModified']
        ].merge(unexpected_bac_df[
                    ['ImageNumber', 'ObjectNumber', center_coordinate_columns['x'], center_coordinate_columns['y'],
                     'AreaShape_MajorAxisLength', parent_image_number_col, parent_object_number_col, 'id',
                     'parent_id', 'NoiseObject', 'UnexpectedEnd_by_CellProfiler', 'UnexpectedEnd_by_Trackrefiner',
                     'UnexpectedBeginning_by_CellProfiler', 'UnexpectedBeginning_by_Trackrefiner',
                     'TrackingLinkModified']
                ],
                on=['ImageNumber', 'ObjectNumber', center_coordinate_columns['x'], center_coordinate_columns['y'],
                    'AreaShape_MajorAxisLength', parent_image_number_col, parent_object_number_col, 'id',
                    'parent_id'],
                how='outer', suffixes=('_ub', '_ue'))

    merged_ub_bac_ue_bac = merged_ub_bac_ue_bac.map(lambda x: False if str(x) in ['nan', "b''"] else x)

    merged_ub_bac_ue_bac['NoiseObject'] = (merged_ub_bac_ue_bac['NoiseObject_ub'] +
                                           merged_ub_bac_ue_bac['NoiseObject_ue'])

    merged_ub_bac_ue_bac['UnexpectedEnd_by_CellProfiler'] = \
        (merged_ub_bac_ue_bac['UnexpectedEnd_by_CellProfiler_ub'] +
         merged_ub_bac_ue_bac['UnexpectedEnd_by_CellProfiler_ue'])

    merged_ub_bac_ue_bac['UnexpectedEnd_by_Trackrefiner'] = \
        merged_ub_bac_ue_bac['UnexpectedEnd_by_Trackrefiner_ub'] + merged_ub_bac_ue_bac[
            'UnexpectedEnd_by_Trackrefiner_ue']

    merged_ub_bac_ue_bac['UnexpectedBeginning_by_CellProfiler'] = \
        (merged_ub_bac_ue_bac['UnexpectedBeginning_by_CellProfiler_ub'] +
         merged_ub_bac_ue_bac['UnexpectedBeginning_by_CellProfiler_ue'])

    merged_ub_bac_ue_bac['UnexpectedBeginning_by_Trackrefiner'] = \
        (merged_ub_bac_ue_bac['UnexpectedBeginning_by_Trackrefiner_ub'] +
         merged_ub_bac_ue_bac['UnexpectedBeginning_by_Trackrefiner_ue'])

    merged_ub_bac_ue_bac['TrackingLinkModified'] = \
        merged_ub_bac_ue_bac['TrackingLinkModified_ub'] + merged_ub_bac_ue_bac['TrackingLinkModified_ue']

    merged_ub_bac_ue_bac['index'] = merged_ub_bac_ue_bac.index.values

    merged_ub_bac_ue_bac_noise = \
        pd.concat([noise_bac_df[
                       ['ImageNumber', 'ObjectNumber', center_coordinate_columns['x'], center_coordinate_columns['y'],
                        'AreaShape_MajorAxisLength', parent_image_number_col, parent_object_number_col, 'id',
                        'parent_id', 'NoiseObject', 'UnexpectedEnd_by_CellProfiler', 'UnexpectedEnd_by_Trackrefiner',
                        'UnexpectedBeginning_by_CellProfiler', 'UnexpectedBeginning_by_Trackrefiner',
                        'TrackingLinkModified']
                   ],
                   merged_ub_bac_ue_bac[
                       ['ImageNumber', 'ObjectNumber', center_coordinate_columns['x'], center_coordinate_columns['y'],
                        'AreaShape_MajorAxisLength', parent_image_number_col, parent_object_number_col, 'id',
                        'parent_id', 'NoiseObject', 'UnexpectedEnd_by_CellProfiler', 'UnexpectedEnd_by_Trackrefiner',
                        'UnexpectedBeginning_by_CellProfiler', 'UnexpectedBeginning_by_Trackrefiner',
                        'TrackingLinkModified']
                   ]
                   ])

    # Bacteria with a change of link
    bac_with_changes_df, logs_list = bacteria_with_change_relation(raw_df, final_df, logs_list,
                                                                   parent_image_number_col, parent_object_number_col)

    logs_df = merged_ub_bac_ue_bac_noise.merge(
        bac_with_changes_df[
            ['ImageNumber', 'ObjectNumber', center_coordinate_columns['x'], center_coordinate_columns['y'],
             'AreaShape_MajorAxisLength', parent_image_number_col, parent_object_number_col, 'id', 'parent_id',
             'NoiseObject', 'UnexpectedEnd_by_CellProfiler', 'UnexpectedEnd_by_Trackrefiner',
             'UnexpectedBeginning_by_CellProfiler', 'UnexpectedBeginning_by_Trackrefiner', 'TrackingLinkModified']
        ], on=['ImageNumber', 'ObjectNumber', center_coordinate_columns['x'], center_coordinate_columns['y'],
               'AreaShape_MajorAxisLength', parent_image_number_col, parent_object_number_col, 'id', 'parent_id'],
        how='outer', suffixes=('_1', '_2'))

    logs_df = logs_df.map(lambda x: False if str(x) in ['nan', "b''"] else x)

    for col in ['NoiseObject', 'UnexpectedEnd_by_CellProfiler', 'UnexpectedEnd_by_Trackrefiner',
                'UnexpectedBeginning_by_CellProfiler', 'UnexpectedBeginning_by_Trackrefiner', 'TrackingLinkModified']:
        logs_df[col] = logs_df[col + '_1'] + logs_df[col + '_2']

    logs_df = logs_df.sort_values(by=['ImageNumber', 'ObjectNumber'])
    logs_df = logs_df[["ImageNumber", "ObjectNumber", center_coordinate_columns['x'], center_coordinate_columns['y'],
                       'AreaShape_MajorAxisLength', parent_image_number_col, parent_object_number_col, 'id',
                       'parent_id', 'NoiseObject', 'UnexpectedEnd_by_CellProfiler', 'UnexpectedEnd_by_Trackrefiner',
                       'UnexpectedBeginning_by_CellProfiler', 'UnexpectedBeginning_by_Trackrefiner',
                       'TrackingLinkModified']]

    return logs_df, logs_list
