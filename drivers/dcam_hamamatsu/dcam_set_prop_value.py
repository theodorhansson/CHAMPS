import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
from dcam_hamamatsu.dcam import *
from dcam_hamamatsu.dcamapi4 import DCAMPROP

def idprpo_to_hex(idprop):
    return '0x{:08X}: '.format(idprop)
    
def dcam_show_properties(iDevice=0):
    """
    Show supported properties
    """
    
    if Dcamapi.init() is not False:

        dcam = Dcam(iDevice)
  
        if dcam.dev_open() is not False:
        
            idprop = dcam.prop_getnextid(0)
            while idprop is not False:
                if idprop == DCAM_IDPROP.EXPOSURETIME:
                    
                    # 
                    # exposure_time_prop_value = dcam.prop_getvaluetext(DCAM_IDPROP.EXPOSURETIME_CONTROL, 1)
                    # print(exposure_time_prop_value)
                    
                    # exposure_time_control_value = dcam.prop_getvaluetext(DCAM_IDPROP.EXPOSURETIME_CONTROL, 1)
                    # print(exposure_time_control_value)
                    
                    exposure_time_control_value = dcam.prop_setvalue(DCAM_IDPROP.EXPOSURETIME_CONTROL, 2)
                    print(exposure_time_control_value)
                    
                    # # exposure_time_control_value = dcam.prop_getvaluetext(DCAM_IDPROP.EXPOSURETIME_CONTROL, 1)
                    # # print(exposure_time_control_value)
                    
                    # success = dcam.prop_setvalue(DCAM_IDPROP.EXPOSURETIME, 1)
                    # # print(success)
                    
                    # exposure_time_control_value = dcam.prop_setvalue(DCAM_IDPROP.EXPOSURETIME, 3)
                    # print(dcam.prop_getvaluetext(DCAM_IDPROP.EXPOSURETIME, 0))
                    
                    
                    
                    
                idprop = dcam.prop_getnextid(idprop)

            dcam.dev_close()
        else:
            print('-NG: Dcam.dev_open() fails with error {}'.format(dcam.lasterr()))
    else:
        print('-NG: Dcamapi.init() fails with error {}'.format(Dcamapi.lasterr()))

    Dcamapi.uninit()


if __name__ == '__main__':
    dcam_show_properties()
