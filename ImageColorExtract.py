import operator

def image_histogram(img):
    rgb_im = img.convert('RGB')
    hist = {}
    for i in range(300):
        for j in range(300):
            r, g, b = rgb_im.getpixel((i, j))
            s = str(r) + " " + str(g) + " " + str(b) + " => "
            r = r - r%32
            g = g - g%32
            b = b - b%32
            s += str(r) + " " + str(g) + " " + str(b)
            key = '#%02x%02x%02x' % (r, g, b)
            print(s + " => " + key)
            if key in hist:
                hist[key] += 1
            else:
                hist[key] = 1
    return dict(sorted(hist.items(), key=operator.itemgetter(1), reverse=True))
