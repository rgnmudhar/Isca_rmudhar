# The base set-up from Stephen edited to suit Regan requirements
# Daily outputs
# No restart file 
# Clouds: changes/additions as per https://github.com/ExeClim/Isca/blob/master/exp/test_cases/simple_clouds/socrates_simcloud.py
# Version with fixed SSTs


import os

import numpy as np

from isca import SocratesCodeBase, DiagTable, Experiment, Namelist, GFDL_BASE
from isca.util import exp_progress

NCORES = 16
base_dir = os.path.dirname(os.path.realpath(__file__))
# a CodeBase can be a directory on the computer,
# useful for iterative development
cb= SocratesCodeBase.from_directory(GFDL_BASE)

# create an Experiment object to handle the configuration of model parameters
# and output diagnostics

exp = Experiment('base_set-up_clouds_fixed_SSTs', codebase=cb)
exp.clear_rundir()

do_simple_global_value = False

inputfiles = [os.path.join(GFDL_BASE,'input/rrtm_input_files/ozone_1990.nc'),\
                os.path.join(base_dir,'input/era-spectral7_T42_64x128.out.nc'),\
                os.path.join(base_dir,'input/sp_lw_ga3_1.txt'),\
                os.path.join(base_dir,'input/sp_sw_ga3_0.txt'),\
                os.path.join(base_dir,'input/sst_clim_amip.nc'),\
                os.path.join(base_dir,'input/siconc_clim_amip.nc'),\
                os.path.join(base_dir,'input/ozone_1990_cmip5.nc')]

#Tell model how to write diagnostics
diag = DiagTable()
diag.add_file('atmos_daily', 1, 'days', time_units='days') # only daily


#Tell model which diagnostics to write
diag.add_field('dynamics', 'bk')
diag.add_field('dynamics', 'pk')

diag.add_field('dynamics', 'ps', time_avg=True, files=['atmos_daily'])
# diag.add_field('atmosphere', 'precipitation', time_avg=True, files=['atmos_daily'])
diag.add_field('dynamics', 'sphum', time_avg=True, files=['atmos_daily'])
diag.add_field('dynamics', 'ucomp', time_avg=True, files=['atmos_daily'])
diag.add_field('dynamics', 'vcomp', time_avg=True, files=['atmos_daily'])
diag.add_field('dynamics', 'temp', time_avg=True, files=['atmos_daily'])
diag.add_field('dynamics', 'zsurf', time_avg=True, files=['atmos_daily'])
diag.add_field('dynamics', 'height', time_avg=True, files=['atmos_daily'])
diag.add_field('dynamics', 'omega', time_avg=True, files=['atmos_daily'])
# diag.add_field('atmosphere', 'flux_u', time_avg=True, files=['atmos_daily'])

exp.diag_table = diag
exp.inputfiles = inputfiles

#Define values for the 'core' namelist
exp.namelist = namelist = Namelist({
    'main_nml':{
     'days'   : 30,
     'hours'  : 0,
     'minutes': 0,
     'seconds': 0,
     'dt_atmos':600,
     'current_date' : [1,1,1,0,0,0],
     'calendar' : 'thirty_day'
    },
    'socrates_rad_nml': {
        'stellar_constant':1370.,
        'lw_spectral_filename':'INPUT/sp_lw_ga3_1.txt',
        'sw_spectral_filename':'INPUT/sp_sw_ga3_0.txt',
        'do_read_ozone': True,
        'ozone_file_name':'ozone_1990_cmip5',
        'ozone_field_name':'ozone_1990_cmip5',
        'dt_rad': 4320, # CHANGED from 3600
        'store_intermediate_rad':True,
        'chunk_size': 16,
        'use_pressure_interp_for_half_levels':False,
        'tidally_locked':False,
        'co2_ppmv':400.,
        #'solday': 90
    }, 
    'idealized_moist_phys_nml': {
        'do_damping': True,
        'turb':True,
        'mixed_layer_bc':True,
        'do_virtual' :False,
        'do_simple': True, # CHANGED
        'roughness_mom':3.21e-05,
        'roughness_heat':3.21e-05,
        'roughness_moist':3.21e-05,            
        'two_stream_gray': False,     #Use the grey radiation scheme
        'do_socrates_radiation': True,
        'convection_scheme': 'SIMPLE_BETTS_MILLER', #Use simple Betts miller convection        
        'do_cloud_simple': True, # ADDED: Turn on the cloud scheme switch 
        'land_option' : 'input',                     # !Use land mask from input file
        'land_file_name' : 'INPUT/era-spectral7_T42_64x128.out.nc',  # !Tell model where to find input file
        'land_roughness_prefactor' :10.0,           # !How much rougher to make land than ocean
        'roughness_mom'   : 2.e-04,                  # !Ocean roughness lengths  
        'roughness_heat'  : 2.e-04,                  # !Ocean roughness lengths  
       'roughness_moist' : 2.e-04,                  # !Ocean roughness lengths              
        'bucket':True,
        'init_bucket_depth_land':0.15, #Set initial bucket depth over land, default = 20
    },

    # Following 4 nmls are NEWLY ADDED
    # Using linear cloud scheme option
    'cloud_simple_nml': {
        'do_qcl_with_temp': True,
        'do_cloud_cover_diags': True,
        'do_add_stratocumulus': True,
        'reff_liq': 14, # Units: micron
        'reff_ice': 25, # Units: micron
        'qcl_val': 0.18, # Units: g/kg, not kg/kg
    },

    'large_scale_cloud_nml': {
        'cf_diag_formula_name': 'linear',
        'do_adjust_cld_by_omega': False,
        'do_freezedry': True,
        'qv_polar_val': 0.006,  # Units: kg/kg
        'freezedry_power': 2.5,
        'do_fitted_rhcrit': False,
        'linear_a_surf': 42,
        'linear_a_top': 13,
        'linear_power': 11,
    },

    'marine_strat_cloud_nml': {
        'sc_diag_method': 'Park_ELF',
        'intermediate_outputs_diags': False,
        'dthdp_min_threshold': -0.08,
        'park_a': 1.3,
        'park_b': -0.1,
    },

    'cloud_cover_diag_nml':{
        'overlap_assumption': 'maximum-random', # or 'maximum', 'random'
        'mid_cld_bottom': 7.0e4,
        'high_cld_bottom': 4.0e4,
        'cf_min': 0,
    },

    'vert_turb_driver_nml': {
        'do_mellor_yamada': False,     # default: True
        'do_diffusivity': True,        # default: False
        'do_simple': True,             # CHANGED: default: False
        'constant_gust': 0.0,          # default: 1.0
        'use_tau': False
    },
    
    'diffusivity_nml': { # CHANGED
        'do_entrain': True,
        'do_simple': True
    },

    'surface_flux_nml': { # CHANGED 
        'use_virtual_temp': False,
        'do_simple': True,
        'old_dtaudv': True,
        'land_humidity_prefactor': 1,
        'land_evap_prefactor': 0.6,
        #'ocean_evap_prefactor': 1,
    },

    'atmosphere_nml': {
        'idealized_moist_model': True
    },

    #Use a large mixed-layer depth, and the Albedo of the CTRL case in Jucker & Gerber, 2017
    'mixed_layer_nml': {        
        'do_qflux' : False, #Don't use analytic formula for q-fluxes 
        #'load_qflux' : False, #Do load q-flux field from an input file
        #'time_varying_qflux' : False, #q-flux will be time-varying
        #'qflux_file_name' : 'soc_ga3_bucket_jra_55_ice_temps', #Name of q-flux input file 
        'do_read_sst' : True, #Read in sst values from input file
        'do_sc_sst' : True, #Do specified ssts (need both to be true)
        'sst_file' : 'sst_clim_amip', #Set name of sst input file
        'specify_sst_over_ocean_only' : True, #Make sure sst only specified in regions of ocean.
        
        # NEED TO CHECK WITH STEPHEN IF NEED ALL OF THE FOLLOWING ---------->
        'tconst' : 200.,
        'prescribe_initial_dist':True,
        'evaporation':True,  
        'depth': 20.,                          #Depth of mixed layer used
        'albedo_value': 0.12,                  # CHANGED from 0.2: Albedo value used     
        'land_albedo_prefactor': 1.3, # CHANGED from (0.325/0.20)
        'land_option':'input', #!Tell mixed layer to get land mask from input file
        'land_h_capacity_prefactor': 0.1,    #!What factor to multiply mixed-layer depth by over land. 
        'update_albedo_from_ice':True,
        'ice_albedo_value':0.7, 
        'ice_albedo_method':'ramp_function', 
        'ice_file_name':'siconc_clim_amip',
        'specify_sst_over_sea_ice':False, 
        # 'linearly_interpolate_sea_ice_temp_and_sst':True,
        # 'ice_sst_file': 'temp_2m_input',
        'update_land_mask_from_ice':False,

    },

    'qe_moist_convection_nml': {
        'rhbm':0.7, # CHANGED from 0.5
        'Tmin':160.,
        'Tmax':350.   
    },
    
    'lscale_cond_nml': {
        'do_simple':True, # CHANGED
        'do_evap':True
    },
    
    'sat_vapor_pres_nml': { # CHANGED
            'do_simple': True,
            'construct_table_wrt_liq_and_ice': True,
            'show_all_bad_values': True,
    },

    'damping_driver_nml': {
        'do_rayleigh': True,
        'trayfric': -0.5,              # neg. value: time in *days*
        'sponge_pbottom':  150., #Setting the lower pressure boundary for the model sponge layer in Pa.
        'do_conserve_energy': True,      
    },

    # FMS Framework configuration
    'diag_manager_nml': {
        'mix_snapshot_average_fields': False  # time avg fields are labelled with time in middle of window
    },

    'fms_nml': {
        'domains_stack_size': 600000                        # default: 0
    },

    'fms_io_nml': {
        'threading_write': 'single',                         # default: multi
        'fileset_write': 'single',                           # default: multi
    },

    'spectral_dynamics_nml': {
        'damping_order': 4,             
        'water_correction_limit': 200.e2,
        'reference_sea_level_press':1.0e5,
        'num_levels':40,      #How many model pressure levels to use
        'valid_range_t':[100.,800.],
        'initial_sphum':[2.e-6],
        'vert_coord_option':'uneven_sigma',
        'surf_res':0.03, #CHANGED from 0.2: Parameter that sets the vertical distribution of sigma levels
        'scale_heights' : 11.0,
        'exponent':7.0,
        'robert_coeff':0.03,
        'ocean_topog_smoothing': 0.8, # CHANGED from 0.0
    },

    'spectral_init_cond_nml' : {
        'topog_file_name': 'era-spectral7_T42_64x128.out.nc',
        'topography_option' : 'input',
        'initial_temperature': 240.,
    }

})

#Lets do a run!
if __name__=="__main__":

        cb.compile()
        exp.set_resolution('T42', 40)

        exp.run(1, use_restart=True, num_cores=NCORES, overwrite_data=False, multi_node=False)
        for i in range(2,721): # 720 months = 60 years
            exp.run(i, num_cores=NCORES, overwrite_data=False, multi_node=False)
