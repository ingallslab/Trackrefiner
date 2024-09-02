
def calculate_intersections_and_unions(df, col1, col2, stat='same'):

    if stat == 'same':
        df['intersection'] = df[col1].values & df[col2].values
        df['union'] = df[col1].values | df[col2].values

        df['intersection'] = df['intersection'].map(len)
        df['union'] = df['union'].map(len)

        df['intersection'] = df['intersection'].astype('int64')
        df['union'] = df['union'].astype('int64')

        df['iou'] = df['intersection'] / df['union']

    elif stat == 'div':
        df['intersection'] = df[col1].values & df[col2].values
        df['intersection'] = df['intersection'].map(len)

        df['union'] = df[col1].values | df[col2].values
        df['union'] = df['union'].map(len)

        # Calculate unique areas for mask 2 (daughter)
        df['unique_masks2'] = df[col2] - df[col1]
        df['unique_masks2'] = df['unique_masks2'].map(len)

        df['intersection'] = df['intersection'].astype('int64')
        df['unique_masks2'] = df['unique_masks2'].astype('int64')
        df['union'] = df['union'].astype('int64')

        # Calculate IoU based on daughter_flag
        df['iou'] = df['intersection'] / (df['intersection'] + df['unique_masks2'])
        df['iou_same'] = df['intersection'] / df['union']

    return df


def iou_calc(df, stat, col_source='coordinate_prev', col_target='coordinate'):

    df = calculate_intersections_and_unions(df, col1=col_source, col2=col_target, stat=stat)

    df['iou'] = 1 - df['iou']

    if stat == 'div':
        df['iou_same'] = 1 - df['iou_same']

    return df