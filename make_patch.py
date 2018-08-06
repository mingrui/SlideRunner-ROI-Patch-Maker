import sqlite3
import argparse
import os

import openslide

SIZE = (512, 512)

parser = argparse.ArgumentParser()
parser.add_argument('--sqlite', help='path to .sqlite file')
parser.add_argument('--wsidir', help='path to wsi directory')
parser.add_argument('--pngdir', help='path to png output directory')
args = parser.parse_args()

UID = 0
TYPE = 1
X = 2
Y = 3

ANTT_TYPE = ['', 'spot', 'rectangular', 'circular', 'important', 'polygon']
SPOT = 1
RECT = 2
CIRC = 3
IMPT = 4
POLY = 5

def batch(db_path, wsi_dir, png_dir):
    if not os.path.exists(png_dir):
        os.mkdir(png_dir)

    conn = sqlite3.connect(db_path)

    # find annotated slides that exists both in sqlite database and wsi directory
    dir_slides = os.listdir(wsi_dir)
    database_slides = [s[1] for s in get_slides(conn)]
    annotated_and_existing_slides = list(set(dir_slides) & set(database_slides))

    for sld in annotated_and_existing_slides:
        antt_data = get_annotations(conn, sld)
        process_slide(antt_data, os.path.join(wsi_dir, sld), SIZE, png_dir)

def get_wsi(wsi_path):
    print(wsi_path)

def get_slides(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Slides")
    slides = cursor.fetchall()
    return slides

def get_annotations(conn, slide_name):
    cursor = conn.cursor()

    # get slide id
    cursor.execute("""
                      SELECT *
                      FROM Slides
                      WHERE (Slides.filename = ?)
                      """, (slide_name,))
    slide = cursor.fetchall()
    slide_id = slide[0][0]

    # delete not agreed on classes
    cursor.execute("""
                      DELETE 
                      FROM Annotations
                      WHERE (agreedClass = 0) 
                      """)

    # select based on slide id
    cursor.execute("""
                      SELECT Annotations.uid,
                             Annotations.type, 
                             Annotations_coordinates.coordinateX,
                             Annotations_coordinates.coordinateY,
                             Annotations.agreedClass,
                             Classes.name,
                             Slides.filename,
                             Persons.name
                      FROM Annotations
                      INNER JOIN Slides
                      ON Slides.uid = Annotations.slide
                      INNER JOIN Annotations_label
                      ON Annotations.uid = Annotations_label.annoId
                      INNER JOIN Annotations_coordinates
                      ON Annotations_label.annoId = Annotations_coordinates.annoId
                      INNER JOIN Persons
                      ON Annotations_label.person = Persons.uid
                      INNER JOIN Classes
                      ON Annotations.agreedClass = Classes.uid
                      WHERE Annotations.slide = ? 
                      """, (slide_id,))
    view_data = cursor.fetchall()

    return view_data

def process_slide(annotation_data, slide_path, size, png_dir):
    sld = openslide.OpenSlide(slide_path)

    for antt in annotation_data:
        if antt[TYPE] == SPOT:
            x, y = antt[X], antt[Y]
            region = sld.read_region((x-size[0]//2, y-size[1]//2), 0, size)
            region.save(os.path.join(png_dir, '{}-{}.png'.format(x, y)), 'PNG')

if __name__=='__main__':
    batch(args.sqlite, args.wsidir, args.pngdir)
