import sqlite3
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--sqlite', help='path to .sqlite file')
parser.add_argument('--wsidir', help='path to wsi directory')
args = parser.parse_args()

def batch(db_path, wsi_dir):
    conn = sqlite3.connect(db_path)

    # find annotated slides that exists both in sqlite database and wsi directory
    dir_slides = os.listdir(wsi_dir)
    database_slides = [s[1] for s in get_slides(conn)]
    annotated_and_existing_slides = list(set(dir_slides) & set(database_slides))

    for sld in annotated_and_existing_slides:
        get_annotations(conn, sld)

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
    for vw in view_data:
        print(vw)

    print('slide name:', slide_name)
    print('len(view_data):', len(view_data))
    print('Annotations_label.uid')

if __name__=='__main__':
    batch(args.sqlite, args.wsidir)

