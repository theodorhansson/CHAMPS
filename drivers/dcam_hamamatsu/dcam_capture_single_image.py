import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
from dcam_hamamatsu.dcam import *
import cv2
from PIL import Image

    
def dcam_capture_image(iDevice=0, exposure_time=0.03):
    """
    Capture and show a image
    """
    if Dcamapi.init() is not False:
        dcam = Dcam(iDevice)
        
        if dcam.dev_open() is not False:
            dcam.prop_setvalue(DCAM_IDPROP.EXPOSURETIME_CONTROL, 2)
            dcam.prop_setvalue(DCAM_IDPROP.EXPOSURETIME, exposure_time)
            
            if dcam.buf_alloc(1) is not False:
                
                if dcam.cap_snapshot() is not False:
                    
                    timeout_milisec = 100
                    while True:
                        if dcam.wait_capevent_frameready(timeout_milisec) is not False:
                            data = dcam.buf_getlastframedata()
                            break
                    
                        dcamerr = dcam.lasterr()
                        if dcamerr.is_timeout():
                            # print('===: timeout')
                            continue
                        

                        print('-NG: Dcam.wait_event() fails with error {}'.format(dcamerr))
                        break
                else:
                    print('-NG: Dcam.cap_start() fails with error {}'.format(dcam.lasterr()))

                dcam.buf_release()
            else:
                print('-NG: Dcam.buf_alloc(1) fails with error {}'.format(dcam.lasterr()))
            dcam.dev_close()
            
        else:
            print('-NG: Dcam.dev_open() fails with error {}'.format(dcam.lasterr()))
    else:
        print('-NG: Dcamapi.init() fails with error {}'.format(Dcamapi.lasterr()))

    Dcamapi.uninit()
    return data


if __name__ == '__main__':
    data = dcam_show_single_captured_image()
