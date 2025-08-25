#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from copy import deepcopy
import numpy as np
import os as os_system
from os.path import exists as path_exist

'''
Initialization functions
'''

def save_system(input_nbook):

    #Deactivate all notebook plots
    for key_plot in ['system_view','prop_DI','prop_Intr','DI_prof','Intr_prof','map_Intr_prof','map_Intr_prof_est','map_Intr_prof_res','map_Diff_prof','flux_ar','trans_ar','gcal_ord','noises_ord','tell_CCF','tell_prop','Fbal_corr','cosm_corr']:input_nbook['settings']['plot_dic'][key_plot] = ''
    
    input_nbook['saved_data_path'] = input_nbook['working_path']+'/'+input_nbook['par']['star_name'] +'/'+input_nbook['par']['main_pl'] + '_Saved_data'
    print('System and data stored in : ', input_nbook['saved_data_path'])
    print('Plots stored in : ', input_nbook['plot_path'])
    if (not path_exist(input_nbook['saved_data_path'])): os_system.makedirs(input_nbook['saved_data_path'])
    if (not path_exist(input_nbook['plot_path'])): os_system.makedirs(input_nbook['plot_path'])

    #Saving previously processed notebooks
    if 'all_nbooks' in input_nbook:
        all_input_nbook = input_nbook['all_nbooks']
        input_nbook.pop('all_nbooks')
    else:all_input_nbook={}
    
    #Saving contents of current notebook under its name, so that we can track the origin of the settings in other notebooks
    all_input_nbook[input_nbook['type']] = input_nbook 
    
    return None

def init():
    input_nbook = {
        #current notebook type
        'type':'setup',
        #notebook inputs that will overwrite system properties file
        'system' : {},  
        #notebook inputs that will overwrite configuration settings file
        'settings' : {'gen_dic':{'data_dir_list':{},'type':{}},
                      'mock_dic':{'visit_def':{},'sysvel':{},'intr_prof':{},'flux_cont':{},'set_err':{}},
                      'theo_dic':{'nsub_Dar':{}, 'nsub_Dpl':{}},
                      'data_dic':{'DI':{'sysvel':{}},
                                  'Intr':{},'Diff':{}},
                      'glob_fit_dic':{'DIProp':{},'IntrProp':{},'IntrProf':{},'DiffProf':{}},
                      'plot_dic':{},
                      'detrend_prof_dic':{}
                     },
        #notebook inputs that will overwrite plot configuration settings file
        'plots' : {},
        #---------------------------------------
        #Notebook inputs for internal use
        #Processing and analysis
        'par' : {'loc_prof_est':False},      
        #Spectral reduction
        'sp_reduc':{},
        #Detrending of CCFs
        'DI_trend':{},
        #Tracks which fits were performed
        'fits':[],            
    }         

    return input_nbook

def init_star(input_nbook):
    input_nbook['settings']['gen_dic']['star_name'] = input_nbook['par']['star_name']
    if 'vsini' not in input_nbook['par']:vsini=1.
    else:vsini = input_nbook['par']['vsini']
    if 'istar' not in input_nbook['par']:istar=90.
    else:istar = input_nbook['par']['istar']
    input_nbook['system'][input_nbook['par']['star_name']]={  
            'star':{
                'Rstar':input_nbook['par']['Rs'],
                'veq':vsini,
                'istar':istar, 
                'sysvel':input_nbook['par']['sysvel'],
                }}
    input_nbook['settings']['data_dic']['DI']['system_prop']={'achrom':{'LD':['quadratic'],'LD_u1' : [input_nbook['par']['ld_u1']],'LD_u2' : [input_nbook['par']['ld_u2']]}}
    input_nbook['settings']['theo_dic']['nsub_Dstar'] = input_nbook['par']['nsub_Dstar']
    return None   

def init_ar(input_nbook,ar_type):
    inst = input_nbook['par']['instrument']
    vis = input_nbook['par']['night']
    if ar_type == 'main':
        input_nbook['settings']['mock_dic']['ar_prop']={inst:{
                                                                vis:{}
                                                                }
                                                           }
        input_nbook['settings']['gen_dic']['studied_ar'] = {}
        input_nbook['settings']['data_dic']['DI']['ar_prop'] = {'achrom':{'LD':['quadratic'],'LD_u1' : [input_nbook['par']['ld_ar_u1']],'LD_u2' : [input_nbook['par']['ld_ar_u2']]}}
        input_nbook['settings']['data_dic']['DI']['transit_prop'] = {'nsub_Dstar':101., 
                                                                     inst:{
                                                                          vis:{'mode':'simu', 'n_oversamp':5.}
                                                                          }
                                                                     }
    for key in ['lat', 'Tc', 'ang', 'fctrst']:
        if key=='Tc': temp=key+'_ar'
        else:temp=key
        input_nbook['settings']['mock_dic']['ar_prop'][inst][vis][temp+'__IS'+inst+'_VS'+vis+'__AR'+input_nbook['par']['ar_name']]=input_nbook['par'][key]
    input_nbook['settings']['gen_dic']['studied_ar'][input_nbook['par']['ar_name']]={inst:[vis]}
    input_nbook['settings']['data_dic']['DI']['ar_prop']['achrom'][input_nbook['par']['ar_name']]=[input_nbook['par']['ang']*np.pi/180.]
    input_nbook['settings']['theo_dic']['ar_prop']=input_nbook['settings']['mock_dic']['ar_prop']
    input_nbook['settings']['theo_dic']['nsub_Dar'].update({input_nbook['par']['ar_name'] : input_nbook['par']['nsub_Dar']})
    return None

def init_pl(input_nbook,pl_type):
    input_nbook['system'][input_nbook['par']['star_name']][input_nbook['par']['planet_name']]={  
                'period':input_nbook['par']['period'],
                'Tcenter':input_nbook['par']['T0'],  
                'ecc':input_nbook['par']['ecc'],
                'omega_deg':input_nbook['par']['long_per'],   
                'Kstar':input_nbook['par']['Kstar'],
                }
    input_nbook['settings']['theo_dic']['nsub_Dpl'].update({input_nbook['par']['planet_name'] :  input_nbook['par']['nsub_Dpl']})
    if pl_type=='main':
        input_nbook['par']['main_pl'] = deepcopy(input_nbook['par']['planet_name'])
        input_nbook['settings']['gen_dic']['studied_pl']={input_nbook['par']['main_pl']:{}}
        input_nbook['system'][input_nbook['par']['star_name']][input_nbook['par']['planet_name']]['inclination']=input_nbook['par']['incl']
        if 'lambda' not in input_nbook['par']:lambda_pl=0.
        else:lambda_pl = input_nbook['par']['lambda']
        input_nbook['system'][input_nbook['par']['star_name']][input_nbook['par']['planet_name']]['lambda_proj']=lambda_pl
        input_nbook['system'][input_nbook['par']['star_name']][input_nbook['par']['planet_name']]['aRs']=input_nbook['par']['aRs']
        input_nbook['settings']['data_dic']['DI']['system_prop']['achrom'][input_nbook['par']['planet_name']]=[input_nbook['par']['RpRs']]
    
        #Paths
        input_nbook['plot_path'] = input_nbook['working_path']+'/'+input_nbook['par']['star_name']+'/'+input_nbook['par']['main_pl']+'_Plots/'

    return None     
    
def add_vis(input_nbook,mock=False):
    inst = input_nbook['par']['instrument']
    vis = input_nbook['par']['night']
    if inst not in input_nbook['settings']['gen_dic']['studied_pl'][input_nbook['par']['main_pl']]:
        input_nbook['settings']['gen_dic']['studied_pl'][input_nbook['par']['main_pl']][inst]=[]
    input_nbook['settings']['gen_dic']['studied_pl'][input_nbook['par']['main_pl']][inst]+=[vis]
    
    #Initializing mock dataset
    if mock:   
        input_nbook['settings']['gen_dic']['mock_data']=True
        input_nbook['settings']['gen_dic']['type'][inst] = 'CCF'
        input_nbook['par']['type']='CCF'
        if inst not in input_nbook['settings']['mock_dic']['visit_def']:
            input_nbook['settings']['mock_dic']['visit_def'][inst]={}
        input_nbook['settings']['mock_dic']['visit_def'][inst][vis]={'exp_range':np.array(input_nbook['par']['range']),'nexp':int(input_nbook['par']['nexp'])}
        
        dbjd =  (input_nbook['settings']['mock_dic']['visit_def'][inst][vis]['exp_range'][1]-input_nbook['settings']['mock_dic']['visit_def'][inst][vis]['exp_range'][0])/input_nbook['settings']['mock_dic']['visit_def'][inst][vis]['nexp']
        n_in_visit = int((input_nbook['settings']['mock_dic']['visit_def'][inst][vis]['exp_range'][1]-input_nbook['settings']['mock_dic']['visit_def'][inst][vis]['exp_range'][0])/dbjd)
        bjd_exp_low = input_nbook['settings']['mock_dic']['visit_def'][inst][vis]['exp_range'][0] + dbjd*np.arange(n_in_visit)
        bjd_exp_high = bjd_exp_low+dbjd      
        bjd_exp_all = 0.5*(bjd_exp_low+bjd_exp_high)
        input_nbook['par']['t_BJD'] = {'inst':inst,'vis':vis,'t':bjd_exp_all}
    
    #Initializing real dataset
    else:
        input_nbook['settings']['gen_dic']['mock_data']=False
        input_nbook['settings']['gen_dic']['type'][inst] = deepcopy(input_nbook['par']['type'])
        if inst not in input_nbook['settings']['gen_dic']['data_dir_list']:
            input_nbook['settings']['gen_dic']['data_dir_list'][inst]={}
        input_nbook['settings']['gen_dic']['data_dir_list'][inst][vis] = input_nbook['par']['data_dir']

    return None

def set_sysvel(input_nbook):
    inst = input_nbook['par']['instrument']
    vis = input_nbook['par']['night'] 
    
    #For mock dataset generation
    if input_nbook['type'] == 'mock':
        if inst not in input_nbook['settings']['mock_dic']['sysvel']:input_nbook['settings']['mock_dic']['sysvel'][inst]={}
        input_nbook['settings']['mock_dic']['sysvel'][inst][vis] = input_nbook['par']['gamma']

    #For processing and trend characterization
    if inst not in input_nbook['settings']['data_dic']['DI']:input_nbook['settings']['data_dic']['DI']['sysvel'][inst]={}
    input_nbook['settings']['data_dic']['DI']['sysvel'][inst][vis] = input_nbook['par']['gamma']
    
    return None

'''
Processing functions
'''

def align_prof(input_nbook):
    input_nbook['settings']['gen_dic']['align_DI']=True
    return None

def flux_sc(input_nbook):
    input_nbook['settings']['gen_dic']['flux_sc']=True

    #Processing mock dataset: scaled to the correct level by construction
    if input_nbook['settings']['gen_dic']['mock_data']:
        input_nbook['settings']['data_dic']['DI']['rescale_DI'] = False 
    return None

def DImast_weight(input_nbook):
    input_nbook['settings']['gen_dic']['DImast_weight']=True
    return None

def extract_diff(input_nbook):
    input_nbook['settings']['gen_dic']['diff_data']=True
    input_nbook['settings']['gen_dic']['nthreads_diff_data'] = 2
    input_nbook['settings']['data_dic']['Diff']['extract_in'] = False
    return None

def extract_intr(input_nbook):
    input_nbook['settings']['gen_dic']['intr_data']=True
    return None

'''
Analysis functions
'''

def ana_prof(input_nbook,data_type):
    if ('CCF' not in input_nbook['par']['type']):
        print('Data in spectral mode: no fit performed')
    else:
        inst = input_nbook['par']['instrument']
        vis = input_nbook['par']['night'] 
        input_nbook['settings']['gen_dic']['fit_'+data_type]=True
    
        #Retrieval mode
        if 'calc_fit' in input_nbook['par']:
            input_nbook['settings']['gen_dic']['calc_fit_'+data_type] = deepcopy(input_nbook['par']['calc_fit'])
            input_nbook['par'].pop('calc_fit')

        #Fit and continuum ranges
        #    - notebook ranges are provided in the star rest frame
        #    - ANTARESS ranges are relative to the solar system barycenter for DI profiles (and must thus be shifted by the input 'sysvel', since at this stage of the notebooks the visit-specific values are not available), and relative to the star otherwise.
        if data_type=='DI':rv_shift = input_nbook['system'][input_nbook['par']['star_name']]['star']['sysvel']
        else:rv_shift=0.
        if 'cont_range' in input_nbook['par']:
            cont_range = deepcopy(input_nbook['par']['cont_range'])
            cont_range_shifted = []
            for bd in cont_range:cont_range_shifted+=[bd[0]+rv_shift,bd[1]+rv_shift]
            input_nbook['settings']['data_dic'][data_type]['cont_range']= {inst: {0:cont_range_shifted}}
            input_nbook['par'].pop('cont_range')
        if 'fit_range' in input_nbook['par']:
            input_nbook['settings']['data_dic'][data_type]['fit_range'] = {inst: {vis: input_nbook['par']['fit_range']+rv_shift}}
            input_nbook['par'].pop('fit_range')

        #Guess values
        if ('guess' in input_nbook['par']):
            input_nbook['settings']['data_dic']['mod_prop'] = {}
            for prop in input_nbook['par']['guess']:
                input_nbook['settings']['data_dic']['mod_prop'][prop] = {'vary':True, inst:{vis:{'guess':input_nbook['par']['guess'][prop]}}}

        #Fit settings
        if ('fit_mode' in input_nbook['par']):
            input_nbook['settings']['data_dic'][data_type]['fit_mode']=deepcopy(input_nbook['par']['fit_mode'])
            input_nbook['par'].pop('fit_mode')
            input_nbook['settings']['data_dic'][data_type]['progress']=False
        else:input_nbook['settings']['data_dic'][data_type]['fit_mode'] = 'chi2'
        if 'run_mode' in input_nbook['par']:
            input_nbook['settings']['data_dic'][data_type]['run_mode']=deepcopy(input_nbook['par']['run_mode'])   
            if input_nbook['par']['run_mode']=='reuse':
                input_nbook['settings']['data_dic'][data_type]['save_chains']=''
                input_nbook['settings']['data_dic'][data_type]['save_MCMC_corner']=''
            input_nbook['par'].pop('run_mode')        
            
        #Manual priors
        if ('priors' in input_nbook['par']):
            input_nbook['settings']['data_dic'][data_type]['priors']=deepcopy(input_nbook['par']['priors'])
            for key in input_nbook['settings']['data_dic'][data_type]['priors']:
                input_nbook['settings']['data_dic'][data_type]['priors'][key]['mod'] = 'uf'
            input_nbook['par'].pop('priors') 

        #Deactivate detection thresholds to avoid automatic computation of amplitude
        input_nbook['settings']['data_dic'][data_type]['thresh_area']=None
        input_nbook['settings']['data_dic'][data_type]['thresh_amp']=None

    return None

'''
Mock dataset functions
'''

def set_mock_rv(input_nbook):
    input_nbook['settings']['mock_dic']['DI_table'] = {key:input_nbook['par'][key] for key in ['x_start','x_end','dx']}
    return None

def set_mock_prof(input_nbook):
    inst = input_nbook['par']['instrument']
    vis = input_nbook['par']['night']   
    if inst not in input_nbook['settings']['mock_dic']['intr_prof']:
        input_nbook['settings']['mock_dic']['intr_prof'][inst] = {'mode':'ana','coord_line':'mu','model': 'gauss','line_trans':None,'mod_prop':{},'pol_mode' : 'modul'} 
    input_nbook['settings']['mock_dic']['intr_prof'][inst]['mod_prop']['ctrst__ord0__IS'+inst+'_VS'+vis] = input_nbook['par']['contrast'] 
    input_nbook['settings']['mock_dic']['intr_prof'][inst]['mod_prop']['FWHM__ord0__IS'+inst+'_VS'+vis]  = input_nbook['par']['FWHM']   
    if inst not in input_nbook['settings']['mock_dic']['flux_cont']:input_nbook['settings']['mock_dic']['flux_cont'][inst] = {}
    input_nbook['settings']['mock_dic']['flux_cont'][inst][vis]  = input_nbook['par']['flux']    
    input_nbook['settings']['mock_dic']['set_err'][inst]  = input_nbook['par']['noise']    
    return None

'''
Plot functions
'''

def plot_light_curve(input_nbook):
    input_nbook['settings']['plot_dic']['spectral_LC'] = 'png' 
    return None

def plot_system(input_nbook):
    input_nbook['settings']['plot_dic']['system_view'] = 'png' 
    input_nbook['plots']['system_view']={'t_BJD':input_nbook['par']['t_BJD'] ,'GIF_generation':True, 'n_stcell':101, 'n_arcell':51}
    return None

def plot_prop(input_nbook,data_type):
    inst = input_nbook['par']['instrument']
    input_nbook['settings']['plot_dic']['prop_'+data_type] = 'png' 

    #Plotted properties
    if input_nbook['type'] in ['Trends','Processing']:
        nbook_prop_names = ['rv','rv_res','contrast','FWHM']
        input_nbook['plots']['prop_'+data_type+'_ordin'] = ['rv','rv_res','ctrst','FWHM']
        input_nbook['par']['print_disp'] = ['plot']
    elif input_nbook['type']=='RMR':
        nbook_prop_names = ['rv','contrast','FWHM']
        input_nbook['plots']['prop_'+data_type+'_ordin'] = ['rv','ctrst','FWHM']
        input_nbook['par']['print_disp'] = ['plot']
    elif input_nbook['type']=='mock':
        nbook_prop_names = ['rv']
        input_nbook['plots']['prop_'+data_type+'_ordin'] = ['rv']
    input_nbook['plots']['prop_'+data_type+'_ordin'] = np.array(input_nbook['plots']['prop_'+data_type+'_ordin'])

    #Plot ranges
    for name_prop,plot_prop in zip(nbook_prop_names,input_nbook['plots']['prop_'+data_type+'_ordin']):
        input_nbook['plots']['prop_'+data_type+'_'+plot_prop]={}
        if 'x_range' in input_nbook['par']:
            input_nbook['plots']['prop_'+data_type+'_'+plot_prop]['x_range'] = deepcopy(input_nbook['par']['x_range'])
        if ('y_range' in input_nbook['par']) and (name_prop in input_nbook['par']['y_range']):
            input_nbook['plots']['prop_'+data_type+'_'+plot_prop]['y_range'] = deepcopy(input_nbook['par']['y_range'][name_prop])
    if 'x_range' in input_nbook['par']:input_nbook['par'].pop('x_range')            
    if 'y_range' in input_nbook['par']:input_nbook['par'].pop('y_range')              
    
    #Dispersion of properties
    if ('print_disp' in input_nbook['par']):  
        for plot_prop in input_nbook['plots']['prop_'+data_type+'_ordin']:
            input_nbook['plots']['prop_'+data_type+'_'+plot_prop]['print_disp']=input_nbook['par']['print_disp']
        input_nbook['par'].pop('print_disp') 
    
    #Set error bars depending on the type of fit
    if input_nbook['settings']['data_dic'][data_type]['fit_mode']=='mcmc':
        for plot_prop in input_nbook['plots']['prop_'+data_type+'_ordin']:
            input_nbook['plots']['prop_'+data_type+'_'+plot_prop]['plot_HDI']=True
            input_nbook['plots']['prop_'+data_type+'_'+plot_prop]['plot_err'] = False 

    if (data_type in ['DI','Intr']):      

        #Models
        prop_path = input_nbook['saved_data_path']+'/Joined_fits/'
        
        #Plot fit to joint properties if carried out
        if data_type+'Prop' in input_nbook['fits']:
            for plot_prop in input_nbook['plots']['prop_'+data_type+'_ordin']:
                input_nbook['plots']['prop_'+data_type+'_'+plot_prop].update({
                    data_type+'Prop_path' : prop_path+'/'+data_type+'Prop/'+input_nbook['settings']['glob_fit_dic'][data_type+'Prop']['fit_mode']+'/'   ,
                    'theo_HR_prop' : True})    
                
        if (data_type=='DI'):
            for plot_prop in input_nbook['plots']['prop_'+data_type+'_ordin']:
                if input_nbook['type']=='mock':coord = 'phase'
                elif input_nbook['type']=='Trends':
                    prop_fit = {'FWHM':'FWHM','ctrst':'contrast','rv_res':'rv_res','rv':'rv_res'}[plot_prop]
                    coord_ref = deepcopy(input_nbook['DI_trend'][prop_fit]['coord'])
                    if (inst=='ESPRESSO') and (coord_ref=='snr'):coord = 'snrQ'
                    elif 'phase' in coord_ref:coord = 'phase'
                    else:coord = coord_ref                
                input_nbook['plots']['prop_DI_'+plot_prop]['prop_DI_absc'] = coord
     
        elif (data_type=='Intr'):
            for plot_prop in input_nbook['plots']['prop_'+data_type+'_ordin']:
                input_nbook['plots']['prop_'+data_type+'_'+plot_prop]['plot_disp'] = False         

            #Plot fit to joint profiles if carried out
            if 'IntrProf' in input_nbook['fits']:        
                for plot_prop in input_nbook['plots']['prop_'+data_type+'_ordin']:
                    input_nbook['plots']['prop_Intr_'+plot_prop].update({
                        'IntrProf_path' : prop_path+'/IntrProf/'+input_nbook['settings']['glob_fit_dic'][data_type+'Prop']['fit_mode']+'/'   ,
                        'theo_HR_prof' : True}) 

    return None

def plot_prof(input_nbook,data_type):
    input_nbook['settings']['plot_dic'][data_type] = 'png'
    input_nbook['plots'][data_type]={
        'GIF_generation':True,
        'shade_cont':True,
        'plot_line_model':True,
        'plot_prop':False} 
    if input_nbook['type'] in ['Trends','RMR','Reduc']:
        if input_nbook['type'] in ['Trends','RMR']:input_nbook['par']['fit_type'] = 'indiv'   #overplot fits to individual exposures 
        input_nbook['plots'][data_type]['step'] = 'latest'
    if 'x_range' in input_nbook['par']:
        input_nbook['plots'][data_type]['x_range'] = deepcopy(input_nbook['par']['x_range'])
        input_nbook['par'].pop('x_range')
    if 'y_range' in input_nbook['par']:
        input_nbook['plots'][data_type]['y_range'] = deepcopy(input_nbook['par']['y_range'])
        input_nbook['par'].pop('y_range')
    if data_type in ['DI_prof','Intr_prof']:
        input_nbook['plots'][data_type]['norm_prof'] = True
    if 'fit_type' in input_nbook['par']:
        input_nbook['plots'][data_type]['fit_type'] = deepcopy(input_nbook['par']['fit_type'])
        input_nbook['par'].pop('fit_type')  
    return None

def plot_ar(input_nbook):
    input_nbook['plots']['system_view']['mock_ar_prop'] = True
    input_nbook['plots']['system_view']['n_arcell'] = 101
    return None

def plot_map(input_nbook,data_type):
    inst = input_nbook['par']['instrument']
    
    #Plot specific order only if spectral data
    if (input_nbook['settings']['gen_dic']['type'][inst]=='CCF'):input_nbook['par']['iord2plot']=0
    
    #Activate plot related to intrinsic CCF model only if model was calculated
    def_map = True
    if data_type in ['Intr_prof_est','Intr_prof_res'] and (not input_nbook['par']['loc_prof_est']):def_map=False
    if data_type in ['Diff_prof_est','Diff_prof_res'] and (not input_nbook['par']['diff_prof_corr']):def_map=False
    if def_map:
        input_nbook['settings']['plot_dic']['map_'+data_type] = 'png'
        input_nbook['plots']['map_'+data_type] = {}
        input_nbook['plots']['map_'+data_type]['verbose'] = False
        input_nbook['plots']['map_'+data_type]['iord2plot']=[deepcopy(input_nbook['par']['iord2plot'])]
        if 'x_range' in input_nbook['par']:
            input_nbook['plots']['map_'+data_type]['x_range'] = deepcopy(input_nbook['par']['x_range'])
        if 'v_range' in input_nbook['par']:
            input_nbook['plots']['map_'+data_type].update({'v_range_all':{inst:{input_nbook['par']['night']:deepcopy(input_nbook['par']['v_range'])}}}) 
            input_nbook['par'].pop('v_range')
        if data_type=='Intr_prof':
            input_nbook['plots']['map_'+data_type]['norm_prof'] = True
            input_nbook['plots']['map_'+data_type]['theoRV_HR'] = True
        elif data_type=='Intr_prof_est':
            input_nbook['plots']['map_'+data_type]['norm_prof'] = True
            input_nbook['plots']['map_'+data_type]['line_model']='rec'
        elif data_type=='Intr_prof_res':
            input_nbook['plots']['map_'+data_type]['cont_only']=False
            input_nbook['plots']['map_'+data_type]['line_model']='rec'
    return None



