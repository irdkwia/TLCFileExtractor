import os, sys
from PIL import Image
from xml.etree import ElementTree
from common.tools import *

def getImageMasks(lst_imgs):
    new_lst = []
    for im in lst_imgs:
        im = im.convert("RGBA")
        int_mask = []
        for pixel in im.getdata():
            if pixel[3]>=128:
                int_mask.append(0)
            else:
                int_mask.append(255)
        mask = Image.frombytes(mode="L", data = bytes(int_mask), size = im.size)
        im = im.convert("RGB")
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

def getDataMode2(lst_img):
    lst_dat = []
    for im in lst_img:
        width = im.size[0]
        height = im.size[1]
        header = b'\x02\x00'+byte_value(im.size[0], 2)+byte_value(height, 4)
        data = b''
        line_data = []
        off = len(header)+height*4
        last_state = -1
        tmp = 0
        for i, pixel in enumerate(im.getdata()):
            r = pixel[0]//8
            g = pixel[1]//8
            b = pixel[2]//8
            color = b+(g*64)+(r*2048)
            a = pixel[3]
            if a==0:
                cur_state = 0
            elif a==255:
                cur_state = 1
            else:
                cur_state = 2
            if i%width==0 or cur_state!=last_state:
                if last_state>=0:
                    line_data.append(last_state%256)
                    line_data.append(last_state//256)
                    if last_state==0:
                        line_data.append(tmp%256)
                        line_data.append(tmp//256)
                    elif last_state==1:
                        line_data.append(len(tmp)%256)
                        line_data.append(len(tmp)//256)
                        for t in tmp:
                            line_data.append(t%256)
                            line_data.append(t//256)
                    elif last_state==2:
                        line_data.append(len(tmp)%256)
                        line_data.append(len(tmp)//256)
                        for t in tmp:
                            line_data.append(t[0]%256)
                            line_data.append(t[0]//256)
                            line_data.append(t[1])
                if cur_state==0:
                    tmp = 1
                elif cur_state==1:
                    tmp = [color]
                elif cur_state==2:
                    tmp = [(color, a)]
                last_state = cur_state
            else:
                if cur_state==0:
                    tmp += 1
                elif cur_state==1:
                    tmp.append(color)
                elif cur_state==2:
                    tmp.append((color, a))
            if i%width==0:
                data += bytes(line_data)
                line_data = []
                header += byte_value(off+len(data), 4)
        if last_state>=0:
            line_data.append(last_state%256)
            line_data.append(last_state//256)
            if last_state==0:
                line_data.append(tmp%256)
                line_data.append(tmp//256)
            elif last_state==1:
                line_data.append(len(tmp)%256)
                line_data.append(len(tmp)//256)
                for t in tmp:
                    line_data.append(t%256)
                    line_data.append(t//256)
            elif last_state==2:
                line_data.append(len(tmp)%256)
                line_data.append(len(tmp)//256)
                for t in tmp:
                    line_data.append(t[0]%256)
                    line_data.append(t[0]//256)
                    line_data.append(t[1])
        data += bytes(line_data)
        lst_dat.append(header+data)
    return lst_dat

def extract_animations(path, out, elt, verbose, mode = None):
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
    header = root.find("header")
    if mode == None:
        if header.findtext("mode")==None:
            mode = int(header.findtext("unknown2").strip())
        else:
            mode = int(header.findtext("mode").strip())
    if mode==1:
        lst_imgs_mask = getImageMasks(lst)
        pal = getImageCommonPalette(lst_imgs_mask)
        lst_dat = getCompressedDataPalette(lst_imgs_mask, pal)
    elif mode==2:
        lst_dat = getDataMode2(lst)
    bytes_ao = b'\x01\x00'+byte_value(nb, 2)+byte_value(int(header.findtext("speed").strip()),2)+byte_value(int(header.findtext("unknown1").strip()), 2)+byte_value(mode, 2)
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
    if mode==1:
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

def search_animations(path=".", out=None, verbose=False, mode=None):
    if out==None:
        out = path
    lst = os.listdir(path)
    for elt in lst:
        if os.path.isdir(path+os.path.sep+elt):
            if os.path.exists(path+os.path.sep+elt+os.path.sep+"anim.xml"):
                extract_animations(path, out, elt, verbose, mode)
            else:
                search_animations(path+os.path.sep+elt, out+os.path.sep+elt, verbose, mode)

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
    mode = None
    if "-m=1" in lst_opts:
        mode = 1
    elif "-m=2" in lst_opts:
        mode = 2
    if len(arg)-end_opt>=2:
        search_animations(arg[end_opt], arg[end_opt+1], verbose=verbose, mode=mode)
    else:
        search_animations(arg[end_opt], verbose=verbose, mode=mode)
else:
    print("Usage: "+arg[0]+" <options> from_path [output_dir]\n\nOptions: \n -v Verbose\n -m=X Force mode X")
