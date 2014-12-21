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
        self.cur.execute("""DROP TABLE buffers;""")
        self.cur.execute("""DROP TABLE ring;""")
        self.cur.execute("""DROP TABLE ringbuff;""")
        self.cur.execute("""DROP TABLE intersection;""")
        self.cur.execute("""DROP TABLE strike;""")
        self.conn.commit()
        self.cur.execute("""CREATE TABLE buffers(id serial, st_buffer geometry, pi integer);""")
        self.cur.execute("""CREATE TABLE ring(id serial, extring geometry, pi integer);""")
        self.cur.execute("""CREATE TABLE ringbuff(ringbuffer geometry, pi integer);""")
        self.cur.execute("""CREATE TABLE intersection(id serial, polly geometry);""")
        self.cur.execute("""CREATE TABLE strike(id serial, location geometry, time timestamp);""")
        self.conn.commit()
        # create buffers
        self.cur.execute("""SELECT ST_Buffer(the_geom, 0.13)
                            FROM pi
                            WHERE pi = 1""")
        buff_1 = self.cur.fetchone()
        self.conn.commit()
        self.cur.execute("""SELECT ST_Buffer(the_geom, 0.13)
                            FROM pi
                            WHERE pi = 2""")
        buff_2 = self.cur.fetchone()
        self.conn.commit()
        self.cur.execute("""SELECT ST_Buffer(the_geom, 0.265)
                            FROM pi
                            WHERE pi = 3""")
        buff_3 = self.cur.fetchone()
        self.conn.commit()
        # insert to database
        self.cur.execute("""INSERT INTO buffers(st_buffer, pi)
                            VALUES(%s, 1);""", (buff_1,))
        self.conn.commit()
        self.cur.execute("""INSERT INTO buffers(st_buffer, pi)
                            VALUES(%s, 2);""", (buff_2,))
        self.conn.commit()
        self.cur.execute("""INSERT INTO buffers(st_buffer, pi)
                            VALUES(%s, 3);""", (buff_3,))
        self.conn.commit()
        # create exterior ring
        self.cur.execute("""SELECT ST_ExteriorRing(st_buffer) FROM buffers
                            WHERE pi = 1;""")
        a = self.cur.fetchone()
        self.conn.commit()
        self.cur.execute("""SELECT ST_ExteriorRing(st_buffer) FROM buffers
                            WHERE pi = 2;""")
        b = self.cur.fetchone()
        self.conn.commit()
        self.cur.execute("""SELECT ST_ExteriorRing(st_buffer) FROM buffers
                            WHERE pi = 3;""")
        c = self.cur.fetchone()
        self.conn.commit()
        # insert into database
        self.cur.execute("""INSERT INTO ring(extring, pi)
                            VALUES(%s, 1);""", (a,))
        self.conn.commit()
        self.cur.execute("""INSERT INTO ring(extring, pi)
                            VALUES(%s, 2);""", (b,))
        self.conn.commit()
        self.cur.execute("""INSERT INTO ring(extring, pi)
                            VALUES(%s, 3);""", (c,))
        self.conn.commit()
        # buffer the extring
        self.cur.execute("""SELECT ST_Buffer(extring, 0.01)
                            FROM ring
                            WHERE pi = 1""")
        ring_buff_1 = self.cur.fetchone()
        self.conn.commit()
        self.cur.execute("""SELECT ST_Buffer(extring, 0.01)
                            FROM ring
                            WHERE pi = 2""")
        ring_buff_2 = self.cur.fetchone()
        self.conn.commit()
        self.cur.execute("""SELECT ST_Buffer(extring, 0.01)
                            FROM ring
                            WHERE pi = 3""")
        ring_buff_3 = self.cur.fetchone()
        self.conn.commit()
        # insert into database
        self.cur.execute("""INSERT INTO ringbuff(ringbuffer, pi)
                            VALUES(%s, 1);""", (ring_buff_1,))
        self.conn.commit()
        self.cur.execute("""INSERT INTO ringbuff(ringbuffer, pi)
                            VALUES(%s, 2);""", (ring_buff_2,))
        self.conn.commit()
        self.cur.execute("""INSERT INTO ringbuff(ringbuffer, pi)
                            VALUES(%s, 3);""", (ring_buff_3,))
        self.conn.commit()
        # select intersection
        self.cur.execute("""SELECT ST_Intersection(%s, ST_Intersection(%s, %s));""",
                         (ring_buff_1, ring_buff_2, ring_buff_3,))
        y = self.cur.fetchone()
        self.conn.commit()
        self.cur.execute("""INSERT INTO intersection(polly)
                            VALUES(%s);""", (y,))
        self.conn.commit()
        # select centroid of the intersect polly
        self.cur.execute("""SELECT ST_Centroid(polly)
                            FROM intersection;""")
        z = self.cur.fetchone()
        self.conn.commit()
        # insert into database
        self.cur.execute("""INSERT INTO strike(location, time)
                            VALUES(%s, now());""", (z,))
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
