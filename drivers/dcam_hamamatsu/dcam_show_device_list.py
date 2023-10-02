import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
from dcam_hamamatsu.dcam import *


def dcam_show_device_list():
    """
    Show device list
    """
    if Dcamapi.init() is not False:
        n = Dcamapi.get_devicecount()
        for i in range(0, n):
            dcam = Dcam(i)
            output = '#{}: '.format(i)

            model = dcam.dev_getstring(DCAM_IDSTR.MODEL)
            if model is False:
                output = output + 'No DCAM_IDSTR.MODEL'
            else:
                output = output + 'MODEL={}'.format(model)

            cameraid = dcam.dev_getstring(DCAM_IDSTR.CAMERAID)
            if cameraid is False:
                output = output + ', No DCAM_IDSTR.CAMERAID'
            else:
                output = output + ', CAMERAID={}'.format(cameraid)

            print(output)
    else:
        print('-NG: Dcamapi.init() fails with error {}'.format(Dcamapi.lasterr()))

    Dcamapi.uninit()


if __name__ == '__main__':
    dcam_show_device_list()
