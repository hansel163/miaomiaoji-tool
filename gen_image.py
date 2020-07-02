import cv2
import numpy as np

WIDTH = 384
PATTERN = '2014'

def gen_img(height=50):
    num = height * WIDTH
    pat_str = PATTERN * (num // len(PATTERN) * 2)
    buf = bytes.fromhex(pat_str)
    img = np.frombuffer(buf, np.uint8)
    img = img.reshape([height, WIDTH])
   
    return img


if __name__ == "__main__":
    img = gen_img()
    cv2.imshow("test", img)
    cv2.imwrite('test.jpg', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
