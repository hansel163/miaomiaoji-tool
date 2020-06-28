from message_process import BtManager

# mmj = BtManager()
mmj = BtManager("fc:58:fa:1e:26:63")
if  mmj.connected:    
    # Print a pure black image with 300 lines
    img = "\xff" * 48 * 300
    mmj.sendImageToBt(img)
    mmj.disconnect()
else:
    print('connection is not established.')
