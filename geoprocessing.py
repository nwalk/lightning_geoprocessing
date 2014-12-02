import psycopg2
#import time
#from datetime import datetime

class DBConnect():
    """Creates a database connection and a cursor"""
    def __init__(self):
        try:
            self.conn = psycopg2.connect("dbname=postgres user=postgres host=localhost password=postgres")
            self.cur = self.conn.cursor()
            self.conn.commit()
        except:
            print("Unable to connect to database...")

    def Query(self):
        raise NotImplementedError


class Sql(DBConnect):

    def execute(self):
        """
        Selects buffers around sensor locations
        Inserts buffer gometry into table
        Selects exterior ring 
        """
        self.cur.execute("""DROP TABLE inside;""")
        self.conn.commit()
        self.cur.execute("""DROP TABLE outside;""")
        self.conn.commit()
        self.cur.execute("""DROP TABLE band;""")
        self.conn.commit()
        self.cur.execute("""DROP TABLE buffers;""")
        self.conn.commit()
        self.cur.execute("""DROP TABLE ring;""")
        self.conn.commit()
        self.cur.execute("""DROP TABLE strike;""")
        self.conn.commit()
        self.cur.execute("""CREATE TABLE buffers(id serial, st_buffer geometry, pi integer);""")
        self.conn.commit()
        self.cur.execute("""CREATE TABLE ring(id serial, extring geometry, pi integer);""")
        self.conn.commit()
        self.cur.execute("""CREATE TABLE inside(inbuffer geometry);""")
        self.conn.commit()
        self.cur.execute("""CREATE TABLE outside(outbuffer geometry);""")
        self.conn.commit()
        self.cur.execute("""CREATE TABLE band(band geometry);""")
        self.conn.commit()
        # create inner and outer buffers
        # insert to database
        self.cur.execute("""SELECT ST_Buffer(the_geom, 20200)
                            FROM raspberrypi
                            WHERE gid = 1""")
        outer = self.cur.fetchone()
        self.conn.commit()
        self.cur.execute("""SELECT ST_Buffer(the_geom, 19800)
                            FROM raspberrypi
                            WHERE gid = 1""")
        inner = self.cur.fetchone()
        self.conn.commit()
        self.cur.execute("""INSERT INTO inside(inbuffer)
                            VALUES(%s);""", (inner,))
        self.conn.commit()
        self.cur.execute("""INSERT INTO outside(outbuffer)
                            VALUES(%s);""", (outer,))
        self.conn.commit()
        self.cur.execute("""SELECT inbuffer FROM inside;""")
        inside = self.cur.fetchone()
        self.cur.execute("""SELECT outbuffer FROM outside;""")
        outside = self.cur.fetchone()
        self.cur.execute("""SELECT ST_Difference(%s, %s);""", (outside, inside,))
        band = self.cur.fetchone()
        self.cur.execute("""INSERT INTO band(band)
                            VALUES(%s);""", (band,))
        self.conn.commit()
        # select other 2 buffers
        # insert into database
        self.cur.execute("""SELECT ST_Buffer(the_geom, 38237)
                            FROM raspberrypi
                            WHERE gid = 2""")
        y = self.cur.fetchone()
        self.conn.commit()
        self.cur.execute("""SELECT ST_Buffer(the_geom, 20000)
                            FROM raspberrypi
                            WHERE gid = 3""")
        z = self.cur.fetchone()
        self.conn.commit()
        self.cur.execute("""INSERT INTO buffers(st_buffer, pi)
                            VALUES(%s, 2);""", (y,))
        self.conn.commit()
        self.cur.execute("""INSERT INTO buffers(st_buffer, pi)
                            VALUES(%s, 3);""", (z,))
        self.conn.commit()
        # create ext ring
        # insert into database
        self.cur.execute("""SELECT ST_ExteriorRing(st_buffer) FROM buffers
                            WHERE pi = 2;""")
        a = self.cur.fetchone()
        self.conn.commit()
        self.cur.execute("""SELECT ST_ExteriorRing(st_buffer) FROM buffers
                            WHERE pi = 3;""")
        b = self.cur.fetchone()
        self.conn.commit()
        self.cur.execute("""INSERT INTO ring(extring, pi)
                            VALUES(%s, 2);""", (a,))
        self.conn.commit()
        self.cur.execute("""INSERT INTO ring(extring, pi)
                            VALUES(%s, 3);""", (b,))
        self.conn.commit()
        self.cur.execute("""SELECT ST_Intersection(%s, %s) INTO strike;""", (a, b,))
        self.conn.commit()
        self.cur.execute("""SELECT * FROM strike;""")
        points = self.cur.fetchone()
        self.cur.execute("""SELECT ST_Intersection(%s, %s) INTO strikelocation;""", (points, band,))
        self.conn.commit()
        self.cur.execute("""DELETE FROM buffers WHERE pi = 1;""")
        self.conn.commit()
        self.cur.execute("""DELETE FROM buffers WHERE pi = 2;""")
        self.conn.commit()
        self.cur.execute("""DELETE FROM buffers WHERE pi = 3;""")
        self.conn.commit()
        print("no errors?")


        
class Menu():
    """Displays a menu and respond to choices when run."""
    def __init__(self):
        self.SQL = Sql()
        self.choices = {
                1: self.execute,
                }

    def display_menu(self):
        print("""

MAIN MENU
                
1 execute

""")

    def run(self):
        """Display the menu and respond to choices."""
        while True:
            self.display_menu()
            choice = input("Enter an option: ")
            action = self.choices.get(choice)
            if action:
                action()
            else:
                print("{} is not a valid choice".format(choice))

    def execute(self):
        return self.SQL.execute()


if __name__ == "__main__":
    Menu().run()
