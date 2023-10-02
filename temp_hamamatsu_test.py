#%%
import matplotlib.pyplot as plt
# from IPython.display import display, clear_output
import numpy as np
import time

from PIL import Image
import logging
from hamamatsu.dcam import copy_frame, dcam, Stream
from time import time

logging.basicConfig(level=logging.INFO)

import cv2

frame = 0

# im = plt.imshow(np, cmap='gist_gray_r', vmin=0, vmax=1)

#figure_folder = "C:\\Users\\Mindaugas Juodenas\\Documents\\GitHub\\CHAMPS_data"
figure_folder = "C:/Users/Mindaugas Juodenas/Documents/Microscopy Images/2023-09-27/SPR Test"
figure_number = 0

figure_list = []

with dcam:
    camera = dcam[0]
    with camera:

        nb_frames = 60
        exposure_time = camera["exposure_time"] = 0.010
        
        x_pixels = camera['image_width'].value
        y_pixels = camera['image_height'].value
        
        picture = np.zeros(shape=(x_pixels, y_pixels))
        # fig, ax = plt.subplots()
        
        # image = ax.imshow(picture, cmap='gist_gray_r', vmin=0, vmax=65500)
        
        
        with Stream(camera, nb_frames) as stream:
                # logging.info("start acquisition")
                camera.start()
                
                for i, frame_buffer in enumerate(stream):
                    start = time()

                    print(f'Taking Picture No {i}')
                    picture = copy_frame(frame_buffer)
                    # cv2.imshow('Webcam', picture)
                    
                    
                    figure_list.append(picture)
                    plt.imshow(picture)
                    plt.show()
                    print(f'Saving Picture No {i}')
                    im = Image.fromarray(picture)
                    im.save(figure_folder + "/image_" + str(i) + ".png")
                    print('Waiting')
                    plt.pause(60)
                    

                
# for i, img in enumerate(figure_list):
#     im = Image.fromarray(img)
#     im.save(figure_folder + "\\" + str(i) + ".png")
#     # np.savetxt(im, figure_folder + "\\" + str(figure_number) + ".csv")
 
#%%
