from qrcode import QRCode
q="a"*1024
qr=QRCode()
qr.add_data(q)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
img.save("result.png")