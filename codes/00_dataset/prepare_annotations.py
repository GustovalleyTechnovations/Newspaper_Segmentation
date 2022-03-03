import pandas as pd
import json
import os
from PIL import Image,ImageDraw
from itertools import chain
from copy import deepcopy

annot_file_path = r'files/'

def load_csv(file_path):
    column_names = ['class', 'x','y','w','h','filename','imgWidth','imgHeight']
    csv_files = [file_path+file for file in os.listdir(file_path) if file[-3:]=='csv']
    rect_annots = pd.concat([pd.read_csv(df, names=column_names) for df in csv_files])
    return rect_annots

def load_json(file_path):
    json_files = [file_path+file for file in os.listdir(file_path) if file[-4:]=='json']
    poly_annots = [json.load(open(f, 'r')) for f in json_files]
    poly_annots = dict(chain.from_iterable(d.items() for d in (poly_annots)))
    return poly_annots

rect_annots = load_csv(annot_file_path)
poly_annots = load_json(annot_file_path)


annot_dict = dict()
file_template = {"fileref":"",
                "size": 0,
                "filename": "",
                "base64_img_data": "",
                "file_attributes": {},
                "regions": {}
                }
annot_template = {"shape_attributes": {
                        "name": "rectangle",
                        "xmin": 0,
                        "ymin": 0,
                        "xmax": 0,
                        "ymax": 0
                    },
                    "region_attributes": {
                        "label": ""
                    }
                  }

unique_fnames = list(rect_annots['filename'].unique())

for fname in unique_fnames:
    temp = rect_annots[rect_annots['filename'] == fname]
    file_templ = deepcopy(file_template)
    
    for each in range(0,len(temp)):
        annot_templ = deepcopy(annot_template)
        bboxes = temp.iloc[each]
        annot_templ["shape_attributes"]["xmin"] = bboxes['x']
        annot_templ["shape_attributes"]["ymin"] = bboxes['y']
        annot_templ["shape_attributes"]["xmax"] = bboxes['x']+bboxes['w']
        annot_templ["shape_attributes"]["ymax"] = bboxes['y']+bboxes['h']
        annot_templ["region_attributes"]["label"] = bboxes['class']
        file_templ["regions"][str(each)] = annot_templ

    if fname in poly_annots.keys():
        poly_reg = poly_annots[fname]["regions"]
        
        for poly in range(0,len(poly_reg)):
            file_templ["regions"][str(each+poly+1)] = poly_reg[str(poly)]
        
    file_templ["size"] = os.path.getsize("data/"+fname)
    file_templ["filename"] = fname

    annot_dict[fname] = file_templ

try:    
    with open("out/sample_annot.json", "w") as outfile:
        json.dump(annot_dict, outfile)
except:
    print("Cannot export the file, save them manually")




def drawFunc():
    img = Image.open("FinExp_0001.png")
    draw = ImageDraw.Draw(img)
    draw.rectangle([(sample['x'],sample['y']),(sample['x']+sample['w'],sample['y']+sample['h'])],  width=10)
    img.show()
