import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
from dcam_hamamatsu.dcam import *
from dcam_hamamatsu.dcamapi4 import DCAM_IDPROP
import cv2

import time

def dcamtest_show_framedata(data):
    """
    Show numpy buffer as an image

    Arg1:   NumPy array
    """
    if data.dtype == np.uint16:
        imax = np.amax(data)
        if imax > 0:
            imul = int(65535 / imax)
            data = data * imul

        cv2.imshow('test', data)
        cv2.waitKey(0)
        
    else:
        print('-NG: dcamtest_show_image(data) only support Numpy.uint16 data')

    return (data, cv2)

def dcam_show_single_captured_image(iDevice=0, exposure_time=0.03):
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
                    
                    timeout_milisec = 1000
                    while True:
                        if dcam.wait_capevent_frameready(timeout_milisec) is not False:

                            data = dcam.buf_getlastframedata()
                            (data, cv_object) = dcamtest_show_framedata(data)
                            
                            cv_object.destroyAllWindows()
                            break

                        dcamerr = dcam.lasterr()
                        if dcamerr.is_timeout():
                            print('===: timeout')
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


if __name__ == '__main__':
    dcam_show_single_captured_image()
