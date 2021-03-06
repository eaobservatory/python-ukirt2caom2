recipe_names = {
    'cgs4': {
        'cal': [
            'ARRAY_TESTS',
            'EMISSIVITY',
            'READNOISE',
            'REDUCE_ARC',
            'REDUCE_BIAS',
            'REDUCE_DARK',
            'REDUCE_FLAT',
            'REDUCE_SKY',
        ],
        'sci': [
            'EXTENDED_SOURCE',
            'EXTENDED_SOURCE_NOSTD',
            'EXTENDED_SOURCE_WITH_SEPARATE_SKY',
            'FAINT_POINT_SOURCE',
            'POINT_SOURCE',
            'POINT_SOURCE_NOFLAT',
            'POINT_SOURCE_NOSTD',
            'QUICK_LOOK',
            'REDUCE_SINGLE_FRAME'
            'REDUCE_SINGLE_FRAME',
            'REDUCE_SINGLE_FRAMES_ONLY',
            'REDUCE_SINGLE_FRAME_NOFLAT',
            'SOURCE_PAIRS_ON_SLIT',
            'SOURCE_PAIRS_ON_SLIT_NO_FLAT',
            'SOURCE_PAIRS_ON_SLIT_NO_STD',
            'SOURCE_PAIRS_TO_SKY',
            'SOURCE_WITH_NOD_TO_BLANK_SKY',
            'STANDARD_QUADS',
        ],
        'std': [
            'STANDARD_STAR',
            'STANDARD_STAR_NOFLAT',
            'STANDARD_STAR_NO_FLAT',
        ],
    },
    'ircam': {
        'cal': [
            'ARRAY_TESTS',
            'REDUCE_DARK',
            'REDUCE_SKY',
            'SKY_FLAT',
            'SKY_FLAT_MASKED',
            'SKY_FLAT_POL',
            'SKY_FLAT_POL_ANGLE',
        ],
        'sci': [
            'BRIGHT_POINT_SOURCE_APHOT',
            'CHOP_SKY_JITTER',
            'CHOP_SKY_JITTER8',
            'DARK_SUBTRACT',
            'DARK_SUBTRACT_BASIC',
            'EXTENDED_3X3',
            'EXTENDED_3x3',
            'EXTENDED_5x5',
            'JITTER12_SELF_FLAT',
            'JITTER5_SELF_FLAT',
            'jitter5_self_flat',
            'JITTER5_SELF_FLAT_APHOT',
            'JITTER5_SELF_FLAT_NCOLOUR',
            'JITTER5_SELF_FLAT_NO_MASK',
            'JITTER5_SELF_FLAT_TELE',
            'JITTER8_SELF_FLAT',
            'JITTER9_SELF_FLAT',
            'JITTER9_SELF_FLAT_BASIC',
            'JITTER9_SELF_FLAT_NO_MASK',
            'JITTER_SELF_FLAT',
            'JITTER_SELF_FLAT_APHOT',
            'JITTER_SELF_FLAT_NCOLOUR',
            'MOVING_JITTER_SELF_FLAT',
            'NOD16_SELF_FLAT_NO_MASK_APHOT',
            'NOD4_SELF_FLAT_NO_MASK',
            'NOD4_SELF_FLAT_NO_MASK_APHOT',
            'NOD8_SELF_FLAT_NO_MASK',
            'NOD8_SELF_FLAT_NO_MASK_APHOT',
            'NOD_SELF_FLAT_NO_MASK',
            'NOD_SELF_FLAT_NO_MASK_APHOT',
            'POINT_SOURCE_BASIC',
            'POL_ANGLE_JITTER',
            'POL_JITTER',
            'QUADRANT_JITTER',
            'QUADRANT_JITTER_NO_MASK',
            'QUICK_LOOK',
            'quick_look',
            'SKY_AND_JITTER',
            'SKY_AND_JITTER5_APHOT'
            'SKY_AND_JITTER_APHOT',
        ],
        'std': [
        ],
    },
    'michelle': {
        'cal': [
            'ARRAY_TESTS',
            'DIFFERENCE_STATS',
            'EMISSIVITY',
            'PEAK_UP',
            'PEAK_UP_PAIRS',
            'REDUCE_ARC',
            'REDUCE_BIAS',
            'REDUCE_DARK',
            'REDUCE_DARK_SPECT'
            'REDUCE_FLAT',
            'REDUCE_FLAT_GROUP',
            'REDUCE_SKY',
        ],
        'sci': [
            'CHOPCONV',
            'ENTER_YPOINT_SOURCE_NOSTD',
            'FAINT_POINT_SOURCE',
            'FITSCONV',
            'INTERLEAVE_FRAMES',
            'MOVING_NOD_CHOP',
            'NOD_CHOP',
            'NOD_CHOP_APHOT',
            'NOD_CHOP_FAINT',
            'NOD_CHOP_SCAN',
            'POINT_SOURCE',
            'POINT_SOURCE_NOFLAT',
            'POINT_SOURCE_NOFLAT_NOSTD',
            'POINT_SOURCE_NOSTD',
            'POINT_SOURCE_POL',
            'POL_ANGLE_NOD_CHOP',
            'POL_NOD_CHOP',
            'POL_QU_FIRST_NOD_CHOP',
            'QUADRANT_JITTER_BASIC',
            'QUICK_LOOK',
            'REDUCE_SINGLE_FRAME_NOFLAT',
            'SBPOL_POINT_SOURCE',
            'SBPOL_POINT_SOURCE_',
            'SOURCE_PAIRS_ON_SLIT',
            'SOURCE_PAIRS_ON_SLIT_NO_STD',
            'STANDARD_QUADS',
        ],
        'std': [
            'STANDARD_STAR',
            'STANDARD_STAR_NOFLAT',
        ],
    },
    'ufti': {
        'cal': [
            'ARRAY_TESTS',
            'DARK',
            'DARK_REDUCE',
            'RECUDE_DARK',
            'REDUCE_DARK',
            'reduce_dark',
            'REDUCE_SKY',
            'SKYFLAT',
            'SKY_FLAT',
            'SKY_FLAT_FP',
            'SKY_FLAT_MASKED',
            'SKY_FLAT_POL',
            'SKY_FLAT_POL_ANGLE',
        ],
        'sci': [
            'BRIGHT_POINT_SOURCE',
            'BRIGHT_POINT_SOURCE_APHOT',
            'BRIGHt_POINT_SOURCE_APHOT',
            'BRIGHT_POINT_SOURCE_APHOTI',
            'BRIGHT_POINT_SOURCE_NCOLOUR_APHOT',
            'CHOP_SKY_JITTER',
            'CHOP_SKY_JITTER9_BASIC',
            'CHOP_SKY_JITTER_BASIC',
            'EXTENDED_3X3',
            'EXTENDED_3x3',
            'extended_3x3',
            'EXTENDED_3X3_BASIC',
            'EXTENDED_3x3_BASIC',
            'EXTENDED_5X5',
            'EXTENDED_5x5',
            'EXTENDED_5x5_BASIC',
            'FOCUS_RUN',
            'FP',
            'FP_JITTER',
            'FP_JITTER_NO_SKY',
            'FP_JITTER_ONE_SIDE',
            'JITTER5_SELF_FLAT',
            'JITTER5_SELF_FLAT_A',
            'JITTER5_SELF_FLAT_APHOT',
            'jitter5_self_flat_APHOT',
            'jitter5_self_flat_aphot',
            'JITTER5_SELF_FLAT_BASI',
            'JITTER5_SELF_FLAT_BASIC',
            'JITTER5_SELF_FLAT_NCOLOUR',
            'JITTER5_SELF_FLAT_NOMASK',
            'JITTER5_SELF_FLAT_NO_MASK',
            'JITTER9_SELF_FLAT',
            'JITTER9_SELF_FLAT_APHOT',
            'JITTER9_SELF_FLAT_B',
            'JITTER9_SELF_FLAT_BASIC',
            'JITTER9_SELF_FLAT_basic',
            'JITTER9_SELF_FLAT_NOMASK',
            'JITTER9_SELF_FLAT_NO_MASK',
            'JITTER9_SELF_FLAT_TELE',
            'JITTER9_SELF_FLAT_TURBO',
            'JITTER_SELFFLAT',
            'JITTER_SELF_FLAT',
            'jitter_self_flat',
            'JITTER_SELF_FLAT5',
            'JITTER_SELF_FLAT_APHOT',
            'JITTER_SELF_FLAT_BASIC',
            'JITTER_SELF_FLAT_NCOLOUR',
            'JITTER_SELF_FLAT_NCOLOUR_APHOT',
            'JITTER_SELF_FLAT_NO_MASK',
            'JITTER_SELF_FLAT_TELE',
            'MOVIMG_JITTER9_SELF_FLAT_BASIC',
            'MOVING_JITTER9_SELF_FLAT',
            'MOVING_JITTER9_SELF_FLAT_BASIC',
            'MOVING_JITTER_SELF_FLAT',
            'MOVING_JITTER_SELF_FLAT_BASIC',
            'MOVING_QUADRANT_JITTER',
            'no_file_read_yet',
            'null'
            'POL_ANGLE_JITTER',
            'POL_EXTENDED',
            'POL_JITTER',
            'POL_JITTER3',
            'QUADRANT_JITTER',
            'QUADRANT_JITTER_BASIC',
            'QUADRANT_JITTER_NOROT',
            'QUADRANT_JITTER_TURBO',
            'QUICK',
            'QUICKLOOK',
            'QUICK_LOOK',
            'quick_look',
            'REDUCE',
            'SKY+JITTER5',
            'SKY+JITTER5_APHOT',
            'SKY_AND_JITTER',
            'SKY_AND_JITTER5',
            'SKY_AND_JITTER5_APHOT',
            '_JITTER9_SELF_FLAT_BASIC',
        ],
        'std': [
        ],
    },
    'uist': {
        'cal': [
            'ARRAY_TESTS',
            'DARK_AND_BPM',
            'EMISSIVITY',
            'MEASURE_READNOISE',
            'REDUCE_ARC',
            'REDUCE_DARK',
            'REDUCE_FLAT',
            'REDUCE_SKY',
            'SKY_FLAT',
            'SKY_FLAT_MASKED',
            'SKY_FLAT_POL',
            'SKY_FLAT_POL_ANGLE',
        ],
        'sci': [
            'BRIGHT_POINT_SOURCE',
            'BRIGHT_POINT_SOURCE_APHOT',
            'BRIGHT_POINT_SOURCE_CATALOGUE',
            'BRIGHT_POINT_SOURCE_NCOLOUR',
            'BRIGHT_POINT_SOURCE_NCOLOUR_APHOT',
            'CHOP_SKY_JITTER',
            'EXTENDED_3x3',
            'EXTENDED_5x5',
            'EXTENDED_SOURCE',
            'EXTENDED_SOURCE_NOSTD',
            'EXTRACT_SLICES',
            'FAINT_POINT_SOURCE',
            'JITTER_SELF_FLAT',
            'JITTER_SELF_FLAT_APHOT',
            'JITTER_SELF_FLAT_NCOLOUR',
            'JITTER_SELF_FLAT_NCOLOUR_APHOT',
            'JITTER_SELF_FLAT_NO_MASK',
            'MAP_EXTENDED_SOURCE',
            'MAP_EXTENDED_SOURCE_NOSTD',
            'NOD_SELF_FLAT_NO_MASK',
            'NOD_SELF_FLAT_NO_MASK_APHOT',
            'NOD_SKY_FLAT_THERMAL',
            'POINT_SOURCE',
            'POINT_SOURCE_CIRCULAR_POL',
            'POINT_SOURCE_NOSTD',
            'POINT_SOURCE_POL',
            'POL_ANGLE_JITTER',
            'POL_EXTENDED',
            'POL_JITTER',
            'POL_JITTER_CORON',
            'QUADRANT_JITTER',
            'QUICK_LOOK',
            'REDUCE_SINGLE_FRAME',
            'REDUCE_SINGLE_FRAMES_ONLY',
            'SOURCE_WITH_NOD_TO_BLANK_SKY',
        ],
        'std': [
            'STANDARD_STAR',
            'STANDARD_STAR_NOD_ON_IFU',
            'STANDARD_STAR_NOD_TO_SKY',
        ],
    },
}
