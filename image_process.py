#!/usr/bin/python
# -*-coding:utf-8-*-
__author__ = "ihciah"

import cv2

class ImageConverter:
    @staticmethod
    def pre_process(im, interpolation=cv2.INTER_AREA):
        fixed_width = 384
        # change to gray image
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) if len(im.shape) == 3 and im.shape[2] != 1 else im
        multi = float(fixed_width) / gray.shape[1]
        dim = (fixed_width, int(gray.shape[0] * multi))
        # scale image to fixed width and keep ratio
        new_im = cv2.resize(gray, dim, interpolation=interpolation)
        return new_im

    # pack eight 0/1 int to one byte, each bit is original one int
    @staticmethod
    def frombits(bits):
        byte_list = bytes()
        # Hansel, 20200629, '/' is normal divide while '//' is integer divide in Python 3
        for b in range(len(bits) // 8):
            byte = bits[b*8:(b+1)*8]
            # byte_list.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
            byte_list += (bytes([int(''.join([str(bit) for bit in byte]), 2)]))
        return byte_list

    @staticmethod
    def im2bmp(im, interpolation=cv2.INTER_AREA):
        im = ImageConverter.pre_process(im, interpolation)
        # convert to binary image, 0 or 255 if pixel > 127
        retval, im_binary = cv2.threshold(im, 127, 255, cv2.THRESH_BINARY)
        ret = bytes()
        for h in range(im_binary.shape[0]):
            # one line pixels
            pixels = [im_binary[h, w] for w in range(im_binary.shape[1])]
            # Hansel 20200629, map() does not return list in Python 3
            # binary = map(lambda x: 1 if x == 0 else 0, pixels)
            binary = [1 if x == 0 else 0 for x in pixels]
            ret += ImageConverter.frombits(binary)
        return ret

    @staticmethod
    def image2bmp(path, interpolation=cv2.INTER_AREA):
        return ImageConverter.im2bmp(cv2.imread(path), interpolation)

class TextConverter:
    @staticmethod
    def text2im(text, height=70, pos=(10, 50), font=cv2.FONT_HERSHEY_SIMPLEX, size=2, color=0, thick=2):
        import numpy as np
        blank_image = np.zeros((height, 384), np.uint8)
        blank_image.fill(255)
        img = cv2.putText(blank_image, text, pos, font, size, color, thick)
        return img

    @staticmethod
    def text2bmp(text, height=70, pos=(10, 50), font=cv2.FONT_HERSHEY_SIMPLEX, size=2, color=0, thick=2):
        return ImageConverter.im2bmp(TextConverter.text2im(text, height, pos, font, size, color, thick))

if __name__ == "__main__":
    img = TextConverter.text2im("Hello World!")
    # img = TextConverter.text2im("1", size=1, pos=(0,30), height=40, thick=50)
    bmp = ImageConverter.im2bmp(img)
    cv2.imshow("test", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
