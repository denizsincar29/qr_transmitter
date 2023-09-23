from base64 import b64decode
from time import sleep, time
import cv2
import playsound
import chunker
play=lambda x: playsound.playsound(f"audio/{x}.wav", False)

cap = cv2.VideoCapture(0)  # just for debugging. after success we'll make webcam.
try:
    detector = cv2.wechat_qrcode_WeChatQRCode("models/detect.prototxt", "models/detect.caffemodel", "models/sr.prototxt", "models/sr.caffemodel")
except Exception as e:
    print("download models via git cloning https://github.com/WeChatCV/opencv_3rdparty and rename the cloned folder as models")
    raise e


def dqr(data):
    data=b64decode(data)
    if data.startswith(b'meta'):
        return True, chunker.demetadata(data)
    return False, chunker.decode_chunk(data)

chunks={}
a=""
c=0
size=0
filename=""
qte=0
metastring=b''
while c!=27:
    ret, img = cap.read()
    #ret, img = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)
    #img = cv2.bitwise_not(img)
    data, bbox = detector.detectAndDecode(img)
    if data:
        print(data)
        data=data[-1]
        if a!=data:
            a=data
            play("dong")
            ismeta, dat=dqr(data)
            if ismeta:
                play("success")
                size, qte, filename=dat
            elif metastring!=b'':
                chunks[dat[0]]=dat[1]
                gotall, missaray=chunker.notmissing(chunks, metastring)
                if gotall:
                    chunker.dechunk(chunks, metastring)
    cv2.imshow("QR file receiver", img)
    c=cv2.waitKey(1)
    # if c>-1: print(c)

cap.release()
cv2.destroyAllWindows()