import os, sys
from PIL import Image
from xml.etree import ElementTree
from common.tools import *

def getImageMasks(lst_imgs):
    new_lst = []
    for im in lst_imgs:
        int_mask = []
        for pixel in im.getdata():
            if pixel[3]>=128:
                int_mask.append(0)
            else:
                int_mask.append(255)
        mask = Image.frombytes(mode="L", data = bytes(int_mask), size = im.size)
        im.convert("RGB")
        new_lst.append((im, mask))
    return new_lst

def getImageCommonPalette(lst_imgs_mask):
    by_color = dict()
    for im in lst_imgs_mask:
        px_mask = im[1].getdata()
        for i, pixel in enumerate(im[0].getdata()):
            if px_mask[i]==0:
                pixel = pixel[:3]
                if pixel in by_color:
                    by_color[pixel] += 1
                else:
                    by_color[pixel] = 1
    lst = [(x, by_color[x]) for x in by_color.keys()]
    lst.sort(key=lambda x:-x[1])
    commonPalette = [x[0] for x in lst[:256]]
    return commonPalette

MAX_DATA_SINGLE = 254
MAX_DATA_GROUP = 250
def getCompressedDataPalette(lst_imgs_mask, palette = None):
    if palette==None:
        palette = getImageCommonPalette(lst_imgs_mask)
    lst_mem = [[[None for k in range(256)] for j in range(256)] for i in range(256)]
    for index, pal in enumerate(palette):
        lst_mem[pal[0]][pal[1]][pal[2]] = index
    new_lst = []
    for im in lst_imgs_mask:
        int_data = [4, 0, im[0].size[0]%256, im[0].size[0]//256, im[0].size[1]%256, im[0].size[1]//256]
        px_mask = im[1].getdata()
        last_num = None
        qty = 0
        tmp_data = []
        width = im[0].size[0]
        for i, pixel in enumerate(im[0].getdata()):
            if px_mask[i]==255:
                cur_num = -1
            else:
                indexUsed = 0
                if lst_mem!=None and lst_mem[pixel[0]][pixel[1]][pixel[2]]!=None:
                    cur_num = lst_mem[pixel[0]][pixel[1]][pixel[2]]
                else:
                    MinUsed = abs(pixel[0]-palette[0][0])+abs(pixel[1]-palette[0][1])+abs(pixel[1]-palette[0][2])
                    for index, pal in enumerate(palette):
                        calc = abs(pixel[0]-pal[0])+abs(pixel[1]-pal[1])+abs(pixel[2]-pal[2])
                        if calc<MinUsed:
                            MinUsed = calc
                            indexUsed = index
                    cur_num = indexUsed
                    if lst_mem!=None:
                        lst_mem[pixel[0]][pixel[1]][pixel[2]] = indexUsed
            if cur_num!=last_num or qty==MAX_DATA_GROUP or i%width==0:
                if last_num!=None:
                    if last_num==-1:
                        while len(tmp_data)>0:
                            int_data.append(min(len(tmp_data), MAX_DATA_SINGLE))
                            int_data.extend(tmp_data[:MAX_DATA_SINGLE])
                            tmp_data = tmp_data[MAX_DATA_SINGLE:]
                        int_data.append(0)
                        int_data.append(qty)
                    else:
                        if qty>2:
                            while len(tmp_data)>0:
                                int_data.append(min(len(tmp_data), MAX_DATA_SINGLE))
                                int_data.extend(tmp_data[:MAX_DATA_SINGLE])
                                tmp_data = tmp_data[MAX_DATA_SINGLE:]
                            int_data.append(255)
                            int_data.append(last_num)
                            int_data.append(qty)
                        else:
                            for j in range(qty):
                                tmp_data.append(last_num)
                    if i%width==0:
                        while len(tmp_data)>0:
                            int_data.append(min(len(tmp_data), MAX_DATA_SINGLE))
                            int_data.extend(tmp_data[:MAX_DATA_SINGLE])
                            tmp_data = tmp_data[MAX_DATA_SINGLE:]
                last_num = cur_num
                qty = 1
            else:
                qty += 1
        if last_num!=None:
            if last_num==-1:
                while len(tmp_data)>0:
                    int_data.append(min(len(tmp_data), MAX_DATA_SINGLE))
                    int_data.extend(tmp_data[:MAX_DATA_SINGLE])
                    tmp_data = tmp_data[MAX_DATA_SINGLE:]
                int_data.append(0)
                int_data.append(qty)
            else:
                if qty>2:
                    while len(tmp_data)>0:
                        int_data.append(min(len(tmp_data), MAX_DATA_SINGLE))
                        int_data.extend(tmp_data[:MAX_DATA_SINGLE])
                        tmp_data = tmp_data[MAX_DATA_SINGLE:]
                    int_data.append(255)
                    int_data.append(last_num)
                    int_data.append(qty)
                else:
                    for i in range(qty):
                        tmp_data.append(last_num)
            while len(tmp_data)>0:
                int_data.append(min(len(tmp_data), MAX_DATA_SINGLE))
                int_data.extend(tmp_data[:MAX_DATA_SINGLE])
                tmp_data = tmp_data[MAX_DATA_SINGLE:]
        new_lst.append(bytes(int_data))
    return new_lst

def extract_animations(path, out, elt, verbose):
    if verbose:
        print("Building "+elt+".ao...")
    tree = ElementTree.parse(path+os.path.sep+elt+os.path.sep+"anim.xml")
    root = tree.getroot()
    lst = []
    nb = 1
    while os.path.exists(path+os.path.sep+elt+os.path.sep+"nb"+str(nb)+".png"):
        lst.append(Image.open(path+os.path.sep+elt+os.path.sep+"nb"+str(nb)+".png"))
        nb+=1
    nb-=1
    lst_imgs_mask = getImageMasks(lst)
    pal = getImageCommonPalette(lst_imgs_mask)
    lst_dat = getCompressedDataPalette(lst_imgs_mask, pal)
    header = root.find("header")
    bytes_ao = b'\x01\x00'+byte_value(nb, 2)+byte_value(int(header.findtext("speed").strip()),2)+byte_value(int(header.findtext("unknown1").strip()), 2)+byte_value(int(header.findtext("unknown2").strip()), 2)
    data = b''
    for d in lst_dat:
        bytes_ao += byte_value(len(data), 4)
        data += d
    header2 = root.find("header2")
    bytes_ao += byte_value(int(header2.findtext("unknown1").strip()), 2)+byte_value(int(header2.findtext("unknown2").strip()), 2)
    anims = root.find("animation").findall("part")
    bytes_ao += byte_value(len(anims), 2)
    for a in anims:
        bytes_ao += byte_value(int(a.findtext("xpos").strip()), 2)
        bytes_ao += byte_value(int(a.findtext("ypos").strip()), 2)
        img = int(a.findtext("img").strip())
        if img>0:
            img -= 1
        bytes_ao += byte_value(img, 2)
        bytes_ao += byte_value(int(a.findtext("other").strip()), 2)
    if not os.path.exists(out):
        os.makedirs(out, exist_ok=True)
    bytes_ao += data
    with open(out+os.path.sep+elt+".ao", 'wb') as file:
        file.write(bytes_ao)
        file.close()
    bytes_pal = b''
    for i in range(256):
        if i<len(pal):
            c = pal[i]
        else:
            c = (0,0,0)
        bytes_pal += bytes([c[0], c[0], c[1], c[1], c[2], c[2]])
    with open(out+os.path.sep+elt+".rgb", 'wb') as file:
        file.write(bytes_pal)
        file.close()

def search_animations(path=".", out=None, verbose=False):
    if out==None:
        out = path
    lst = os.listdir(path)
    for elt in lst:
        if os.path.isdir(path+os.path.sep+elt):
            if os.path.exists(path+os.path.sep+elt+os.path.sep+"anim.xml"):
                extract_animations(path, out, elt, verbose)
            else:
                search_animations(path+os.path.sep+elt, out+os.path.sep+elt, verbose)

arg = sys.argv
end_opt = 1
lst_opts = []
while end_opt<len(arg):
    opt = arg[end_opt]
    if opt[0]!="-":
        break
    else:
        lst_opts.append(opt)
    end_opt += 1
if len(arg)-end_opt>0:
    verbose = False
    if "-v" in lst_opts:
        verbose = True
    leftovers = False
    if len(arg)-end_opt>=2:
        search_animations(arg[end_opt], arg[end_opt+1], verbose=verbose)
    else:
        search_animations(arg[end_opt], verbose=verbose)
else:
    print("Usage: "+arg[0]+" <options> from_path [output_dir]\n\nOptions: \n -v Verbose")
