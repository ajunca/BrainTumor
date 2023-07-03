import os
import pandas as pd

fsaverage_parcel_file = 'data/ds001226-fmriprep/sourcedata/freesurfer/fsaverage/mri/aparc+aseg.mgz'
derivative_dir = 'data/derivatives/'
tumor_masks_dir = 'data/ds001226/derivatives/tumor_masks/'
lut_table_file = 'data/derivatives/parcellation_lut.txt'
fsaverage_stats_file = os.path.join(derivative_dir, 'fsaverage-aparc+aseg.stats')

# Let's output stats for the fsaverage of each reagion. So afterward for example we can know how much percentage of the
# region has tumor
os.system('mri_segstats --seg ' + fsaverage_parcel_file + ' --ctab ' + lut_table_file + ' --sum ' + fsaverage_stats_file)

# We read the table after creation
fsaverage_segstats_table = pd.read_csv(
    fsaverage_stats_file,
    sep='\s+',
    comment='#',
    header=None,
    names=['Index', 'SegId', 'NVoxels', 'Volume_mm3', 'RegionName'],
    index_col='RegionName'
)

# For each subject we need to compute which regions on the Desikan-Killiany parcellation have
# tumor (this is, at least one voxel intersection). It is performed as following:
#   - Mask the fsaverage with the tumor mask
#   - Compute stats using Desikan-Killiany lut table
#   - Read stats and output for each region tumor volume (or 0.0 if none)
#
# Notes:
#   - Freesurfer Desikan-Killiany has 35+35 regions in its LUT (ex. "colortable_desikan_killiany.txt")
#     and not 34+34, why?
#       - One region is ignored based on datasheet delivered from dataset authors:
#         ctx-XX-corpuscallosum
for pat in os.listdir(tumor_masks_dir):
    if os.path.isdir(tumor_masks_dir + pat):
        print ("------------- Processing patient " + pat + " -------------")

        pat_tumor_mask_file = os.path.join(tumor_masks_dir, pat, 'anat', 'sub-' + pat.replace("sub-", "") + '_space_MNI_label-tumor.nii')
        output_pat_dir = os.path.join(derivative_dir, pat)

        # Create output dir if non existent
        os.makedirs(output_pat_dir, exist_ok=True)

        # We need to mask fsaverage with tumor mask
        # $ mri_mask volume mask output
        output_masked_vol_file = os.path.join(output_pat_dir, 'aparc+aseg-tumor_masked.mgz')
        os.system('mri_mask ' + fsaverage_parcel_file + ' ' + pat_tumor_mask_file + ' ' + output_masked_vol_file)

        # Output masked file stats
        output_raw_maked_stats_file = os.path.join(output_pat_dir, 'aparc-aseg-tumor_masked.stats')
        os.system('mri_segstats --seg ' + output_masked_vol_file + ' --ctab ' + lut_table_file + ' --sum ' + output_raw_maked_stats_file)

        # Read the created stats file
        segstats_table = pd.read_csv(
            output_raw_maked_stats_file,
            sep='\s+',
            comment='#',
            header=None,
            names=['Index', 'SegId', 'NVoxels', 'Volume_mm3', 'RegionName'],
            index_col='RegionName'
        )

        # Read lut table so we know region indices
        lut_table = pd.read_csv(
            lut_table_file,
            sep='\s+',
            comment='#',
            header=None,
            names=['No.', 'RegionName', 'R', 'G', 'B', 'A'],
            # index_col='StructName'
        )

        # Let's create a table that has for each region of the parcellation its volumetric tumor intersection in mm³
        tumor_regions = lut_table[['RegionName']].copy()
        tumor_regions['Tumor_volume_mm3'] = {k: segstats_table['Volume_mm3'].get(r['RegionName'], 0.0) for k, r in lut_table.iterrows()}
        tumor_regions['Fsaverage_volume_mm3'] = {k: fsaverage_segstats_table['Volume_mm3'].get(r['RegionName'], 0.0) for k, r in lut_table.iterrows()}
        tumor_regions['Tumor_volume_percentage'] = {k: (segstats_table['Volume_mm3'].get(r['RegionName'], 0.0))/(fsaverage_segstats_table['Volume_mm3'].get(r['RegionName'], 0.0)) for k, r in lut_table.iterrows()}

        # Save tumor regions
        output_tumor_regions_file = os.path.join(output_pat_dir, 'tumor_regions.tsv')
        tumor_regions.to_csv(
            output_tumor_regions_file,
            sep='\t',
            index=True,
            index_label='RegionId',
            encoding='utf-8'
        )