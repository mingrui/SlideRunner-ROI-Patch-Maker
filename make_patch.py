import sqlite3

def main(db_path):
    conn = sqlite3.connect(db_path)
    # get_slides(conn)
    get_annotations(conn)

def get_slides(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Slides")
    slides = cursor.fetchall()
    print(slides)

def get_annotations(conn):
    cursor = conn.cursor()
    cursor.execute("""SELECT Annotations.uid, 
                             Slides.filename, 
                             Annotations.type, 
                             Annotations.agreedClass
                      FROM Annotations
                      INNER JOIN Slides
                      ON Slides.uid = Annotations.slide""")
    view_data = cursor.fetchall()
    print(view_data)

if __name__=='__main__':
    main('sliderunner-test.sqlite')
    pass

