from PIL import Image


def squarify(filename):
    im = Image.open(filename)
    x, y = im.size
    if x > y:
        crop_settings = (x // 2 - y // 2, 0, x // 2 + y // 2, y)
    elif y > x:
        crop_settings = (0, y // 2 - x // 2, x, y // 2 + x // 2)
    else:
        return "already was square"
    out = im.crop(crop_settings)
    if out.size[0] > 1080:
        out = out.resize((1080, 1080))
    out.save(filename)
    return "successfully squarified"


def resize_for_avatar(filename):
    squarify(filename)
    im = Image.open(filename)
    x, y = im.size
    if x > 200:
        out = im.resize((200, 200))
    else:
        return "already was small"
    out.save(filename)
    return "successfully resized"
