import cv2
import numpy

import matplotlib.pyplot as plt
def test():
    test_dir = 'tableimage.jpg'
    mask_dir = 'C:\\Users\\CW-WM\\Desktop\\微信截图_20190902153158.png'
    save_dir = 'D:\\a123.jpg'
    src = cv2.imread(test_dir)
    mask = cv2.imread(mask_dir)
    save = numpy.zeros(src.shape, numpy.uint8)
    for row in range(src.shape[0]):
        for col in range(src.shape[1]):
            for channel in range(src.shape[2]):
                if mask[row, col, channel] == 0:
                    val = 0
                else:
                    reverse_val = 255 - src[row, col, channel]
                    val = 255 - reverse_val * 256 / mask[row, col, channel]
                    if val < 0:
                        val = 0
                save[row, col, channel] = val
    cv2.imwrite(save_dir, save)
def get_make():
    imagepath = r'tableimage.jpg'
    image = cv2.imread(imagepath)
    height, width, channel = image.shape
    for i in range(height):
        for j in range(width):
            b, g, r = image[i, j]
            if ((r - b) > 30 and (r - g) > 30):

                b = 0
                g = 0
                r = 0
            else:

                b = 255
                g = 255
                r = 255

            image[i, j] = [r, g, b]
    plt.imshow(image)
    plt.savefig("a.jpg", dpi=1080)
    # plt.show()
get_make()