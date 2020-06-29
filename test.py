from message_process import BtManager

# mmj = BtManager()
mmj = BtManager("fc:58:fa:1e:26:63")
if  mmj.connected:    
    # Print a pure black image with 300 lines
    # img = b"\xff" * 48 * 300

    # print text
    from image_process import TextConverter
    # img = TextConverter.text2bmp("Hello World!")
    img = TextConverter.text2bmp("1", size=1, pos=(0, 30), height=40, thick=50)
    mmj.sendImageToBt(img)
    mmj.disconnect()
else:
    print('connection is not established.')
