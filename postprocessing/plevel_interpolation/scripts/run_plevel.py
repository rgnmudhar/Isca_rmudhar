#!/bin/env python
# -*- cofing: utf-8 -*-

from netCDF4 import Dataset  
from plevel_fn import plevel_call, daily_average, join_files, two_daily_average, monthly_average
import sys
import os
import time
import argparse

def main(nc_file_in, nc_file_out,  frequency, levels, variables):
    avg_or_daily_list = [frequency] # user-defined, default was 'monthly'

    do_extra_averaging=False #If true, then 6hourly data is averaged into daily data using cdo
    group_months_into_one_file=False # If true then monthly data files and daily data files are merged into one big netcdf file each.
    level_set='standard' #Default is the standard levels used previously - now changed to match the pfull Isca output
    mask_below_surface_set=' '  
    #Default is to mask values that lie below the surface pressure when interpolated. 
    #For some applications, e.g. Tom Clemo's / Mark Baldwin's stratosphere index, you want to have values interpolated below ground, i.e. as if the ground wasn't there. 
    #To use this option, this value should be set to '-x '. 

    plevs={}
    var_names={}

    if level_set=='standard':
        # Set plevels to be same as pfull from Isca output (for 40 levels) for use in EOF analysis, calculated using find_phalf.py script
        # Same levels used for monthly, daily and 6hourly:
        if levels == 40:
            # For 40 levels:
            plevels = ' -p "1 3 6 10 16 25 39 60 90 133 192 273 384 532 726 978 1301 1710 2223 2856 3633 4573 5703 7049 8638 10501 12672 15186 18082 21403 25198 29521 34436 40014 46340 53516 61661 70918 81460 93499"'

        elif levels == 60:
            # For 60 levels:
            plevels = ' -p "0 2 4 5 8 11 15 20 27 36 49 64 84 109 140 180 228 288 362 451 558 687 841 1023 1238 1490 1784 2124 2518 2969 3486 4074 4740 5492 6338 7286 8344 9522 10828 12274 13869 15625 17554 19668 21982 24509 27267 30273 33546 37107 40982 45195 49776 54760 60183 66088 72522 79540 87204 95585"' 

        plevs['monthly']= plevels
        plevs['daily']= plevels
        plevs['6hourly']= plevels 

        # User-defined list of variables
        # Same variables used for monthly, daily and 6hourly:
        var_names['monthly']= variables
        var_names['daily']= variables
        var_names['6hourly']= variables

    for avg_or_daily in avg_or_daily_list:  
        if not os.path.isfile(nc_file_out):
            plevel_call(nc_file_in,nc_file_out, var_names = var_names[avg_or_daily], p_levels = plevs[avg_or_daily], mask_below_surface_option=mask_below_surface_set)

    return 

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        prog='Interpolation script',
        description='Script used to interpolate Isca output models')

    #nc_file_in =  ${GFDL_DATA}/${EXP}/${RUN}/atmos_daily.nc one at a time
    #nc_file_out =  ${GFDL_BASE}/postprocessing/plevel_interpolation/plevel.nc
    #frequency = 'daily' # or '6hourly'
    #levels = 40 # or 60
    #variables = 'ucomp vcomp omega temp height'
    parser.add_argument('nc_file_in')
    parser.add_argument('nc_file_out')
    parser.add_argument('frequency')
    parser.add_argument('levels', type=int)
    parser.add_argument('variables')

    args = parser.parse_args()

    main(args.nc_file_in, args.nc_file_out, args.frequency, args.levels, args.variables) 
