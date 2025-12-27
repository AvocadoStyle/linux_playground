"""
Will image manipulation using opencv & numpy
"""
import random

from linux_playground.utils.path_utils.specific_paths import relative_path
import cv2

def image_color_processing():
    image_path = relative_path("../data/rgb.png")
    img = cv2.imread(filename=image_path, flags=-1)
    for i in range(0, img.shape[0]):
        for j in range(img.shape[1]):
            img[i][j] = [random.randint(0, 255),
                         random.randint(0, 255),
                         random.randint(0, 255), 255]

    cv2.imshow("Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    image_color_processing()


