import os, shutil
import sys

AVAILABLE_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz._0123456789"
def value(bytes_list):
    n = 0
    for i, b in enumerate(bytes_list):
        n += b * (256**i)
    return n

def extract_bul(filename, out = None, verbose = False):
    available_ext = ["nfnt", "wav", "ao", "rgb", "jpg", "b16", "txt"]
    dir_out = os.path.basename(filename).split(".bul")[0]
    if out==None:
        out = os.path.dirname(filename)
        if out=='':
            out = '.'
    if verbose:
        print("Extracting from "+filename+"...")
    if dir_out!="":
        if not os.path.exists(out+os.path.sep+dir_out):
            os.makedirs(out+os.path.sep+dir_out, exist_ok=True)
        else:
            shutil.rmtree(out+os.path.sep+dir_out)
            os.mkdir(out+os.path.sep+dir_out)
    try:
        with open(filename, "rb") as file:
            data_bul = file.read()
            file.close()
    except:
        print("Can't extract from "+filename+"!")
        raise Exception("Can't extract from "+filename+"!")
    last_file = None
    start = 0
    for i in range(len(data_bul)):
        if data_bul[i]==ord('.'):
            j = 1
            is_ext = False
            ext = ''
            try:
                while j<=6:
                    if data_bul[i+j]==0:
                        is_ext = True
                        break
                    else:
                        ext += chr(data_bul[i+j])
                        j+=1
            except:pass
            if is_ext and ext.lower() in available_ext:
                k = 1
                while i-k>=0 and chr(data_bul[i-k]) in AVAILABLE_CHARS:
                    k+=1
                k-=1
                if last_file!=None:
                    if verbose:
                        print("Extracting "+last_file+"...")
                    with open(out+os.path.sep+dir_out+os.path.sep+last_file, "wb") as file:
                        file.write(data_bul[start:i+j])
                        file.close()
                    
                last_file = data_bul[i-k:i+j].decode(encoding="ascii")
                start = i+j+1
    if last_file!=None:
        if verbose:
            print("Extracting "+last_file+"...")
        with open(out+os.path.sep+dir_out+os.path.sep+last_file, "wb") as file:
            file.write(data_bul[start:])
            file.close()

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
    if len(arg)-end_opt>=2:
        extract_bul(arg[end_opt], arg[end_opt+1], verbose=verbose)
    else:
        extract_bul(arg[end_opt], verbose=verbose)
else:
    print("Usage: "+arg[0]+" <options> bul_file [output_dir]\n\nOptions: \n -v Verbose")
