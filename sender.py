from time import sleep, time
import cv2
import chunker
from filedialogs import open_file_dialog


openpath=open_file_dialog("choose file", ".")
if not openpath: exit()
meta=chunker.enqrcode(chunker.metadata(openpath))
t=time()
i=0
c=0
emergency=False
while c!=32 and c!=27:
    cv2.imshow("file sender (ready to send)", meta)
    if time()-t>0.25:
        t=time()
    c=cv2.waitKey(1)
    # if c>-1: print(c)
emergency = (c==27)

for code in chunker.enchunk(openpath):
    if emergency: break # immediately!
    t=time()
    while time()-t<0.25 and c!=27:
        c=cv2.waitKey(1)
    # if c>-1: print(c)
    if c==27: break
    img=chunker.enqrcode(code)
    cv2.imshow("qr sender", img)
cv2.destroyAllWindows()