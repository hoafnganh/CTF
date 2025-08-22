from PIL import Image  # import the Image module from Pillow

# Opening the first image
img1 = Image.open("scrambled1.png")
pixels1 = img1.load()

# Opening the second image
img2 = Image.open("scrambled2.png")
pixels2 = img2.load()

# Creating a new image with the same size as the first image
flag = Image.new("RGB", img1.size)
flagpix = flag.load()

# Merging the two images
for row in range(img1.size[1]):  # img1.size[1] is the height of the image
    for col in range(img1.size[0]):  # img1.size[0] is the width of the image
        flagpix[col, row] = (
            (pixels1[col, row][0] + pixels2[col, row][0]) % 256, # R
            (pixels1[col, row][1] + pixels2[col, row][1]) % 256, # G
            (pixels1[col, row][2] + pixels2[col, row][2]) % 256 # B
        )

# Saving the merged image
flag.save("flag.png")