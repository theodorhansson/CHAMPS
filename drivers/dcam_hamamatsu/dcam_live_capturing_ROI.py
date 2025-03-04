import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
from dcam_hamamatsu.dcam import *
import threading
import cv2
import time

import numpy as np

def dcamtest_show_framedata(data, windowtitle, iShown, ROI, mirror_x, mirror_y, transpose):
    """
    Show numpy buffer as an image

    Arg1:   NumPy array
    Arg2:   Window name
    Arg3:   Last window status.
        0   open as a new window
        <0  already closed
        >0  already openend
        
    """
    if iShown > 0 and cv2.getWindowProperty(windowtitle, cv2.WND_PROP_VISIBLE) == 0:
        return (-1, cv2)
    if iShown < 0:
        return (-1, cv2)  
    
    cv2.namedWindow(windowtitle, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(windowtitle, 1024, 1024)
    
    if data.dtype == np.uint16:
        imax = np.amax(data)
        if imax > 0:
            imul = int(65535 / imax)
            data = data * imul
            
        if mirror_x:
            data = np.flip(data, axis=0)
        if mirror_y:
            data = np.flip(data, axis=1)
        if transpose:
            data = data.T
            
        for roi in ROI:
            pos_x = roi[0]
            pos_y = roi[1]
            width = roi[2]
            height = roi[3]
            
            line_width = 3
            
            ## Right line
            data[pos_y - height//2:pos_y + height//2, 
                 pos_x + width//2:pos_x + width//2 + line_width] = imax     
            
            ## Left line
            data[pos_y - height//2:pos_y + height//2, 
                 pos_x - width//2 - line_width:pos_x - width//2] = imax     
            
            ## Bottom line
            data[pos_y + height//2:pos_y + height//2 + line_width, 
                 pos_x - width//2:pos_x + width//2] = imax 
            
            ## Top line
            data[pos_y - height//2 - line_width:pos_y - height//2,
                 pos_x - width//2:pos_x + width//2] = imax 
            
            
            
        img = cv2.imshow(windowtitle, data)
        
        return (1, cv2)
    
    else:
        print('-NG: dcamtest_show_image(data) only support Numpy.uint16 data')
        return (-1, cv2)


def dcamtest_thread_live(dcam, ROI, mirror_x, mirror_y, transpose):
    """
    Show live image

    Arg1:   Dcam instance
    """
    if dcam.cap_start() is not False:

        timeout_milisec = 100
        iWindowStatus = 0
        while iWindowStatus >= 0:
            if dcam.wait_capevent_frameready(timeout_milisec) is not False:
                data = dcam.buf_getlastframedata()
                (iWindowStatus, cv_object) = dcamtest_show_framedata(data, 
                                                                     'Live image', 
                                                                     iWindowStatus, 
                                                                     ROI,
                                                                     mirror_x,
                                                                     mirror_y,
                                                                     transpose)
            else:
                dcamerr = dcam.lasterr()
                if dcamerr.is_timeout():
                    # print('===: timeout')
                    pass
                else:
                    print('-NG: Dcam.wait_event() fails with error {}'.format(dcamerr))
                    break

            key = cv2.waitKey(1)
            if key == ord('q') or key == ord('Q'):  # if 'q' was pressed with the live window, close it
                cv_object.destroyAllWindows()
                break

    else:
        print('-NG: Dcam.cap_start() fails with error {}'.format(dcam.lasterr()))


def dcam_live_capturing(ROI, mirror_x, mirror_y, transpose, iDevice=0, exposure_time=0.03):
    """
    Capture and show a image
    """
    if Dcamapi.init() is not False:
        dcam = Dcam(iDevice)
        if dcam.dev_open() is not False:
            dcam.prop_setvalue(DCAM_IDPROP.EXPOSURETIME_CONTROL, 2)
            dcam.prop_setvalue(DCAM_IDPROP.EXPOSURETIME, exposure_time)
            
            if dcam.buf_alloc(3) is not False:
                dcamtest_thread_live(dcam, ROI, mirror_x, mirror_y, transpose)

                # release buffer
                dcam.buf_release()
            else:
                print('-NG: Dcam.buf_alloc(3) fails with error {}'.format(dcam.lasterr()))
            dcam.dev_close()
        else:
            print('-NG: Dcam.dev_open() fails with error {}'.format(dcam.lasterr()))
    else:
        print('-NG: Dcamapi.init() fails with error {}'.format(Dcamapi.lasterr()))

    Dcamapi.uninit()
    time.sleep(1)


if __name__ == '__main__':
    dcam_live_capturing()
