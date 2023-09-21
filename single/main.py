import qrcode
q=input("enter data to generate")
img = qrcode.make(q)
img.save("result.png")