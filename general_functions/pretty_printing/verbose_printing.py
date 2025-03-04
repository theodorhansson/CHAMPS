#%%

def headline(message, verbose=True):
    print('###-------- ' + message + ' --------###')
    
def message(message, verbose=True):
    print('--- ' + message + ' ---')
    
    
def check_flag_for_verbose_printing(config_lower):
    
    if 'verbose_level' in config_lower['measurement'].keys():
        return config_lower['measurement']['verbose_level']
    else:
        headline('Verbose level not specified. Setting verbose to default 1.')
        return 1
    
    
    