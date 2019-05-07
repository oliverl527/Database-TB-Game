import sqlite3
import re

conn = sqlite3.connect('mollys_mansion.db')
c = conn.cursor()
c.execute("SELECT * FROM object;")
visited = []
i = 0
for row in c.fetchall():
    visited.insert(i, False)
    i = i+1
i = 0
startingRoom = 1
visited[0] = True
print(visited)
#   Starting flavor text
c.execute("SELECT desc FROM object WHERE object.id == 0;")
print(c.fetchall()[0][0])
while startingRoom != 0:
    #   Setting up the name of the current room
    c.execute("SELECT holder FROM object WHERE object.name == 'player';")
    for row in c.fetchall():
        startingRoom = row[0]
    #   Display name, first desc
    if visited[startingRoom] is False:
        s = ("SELECT name, first_time_desc FROM object WHERE object.id == " + str(startingRoom) + ";")
        visited[startingRoom] = True
        c.execute(s)
        for row in c.fetchall():
            print("\n" + row[0].upper() + "\n" + str(row[1]))
    else:
        s = ("SELECT name, desc FROM object WHERE object.id == " + str(startingRoom) + ";")
        c.execute(s)
        for row in c.fetchall():
            print("\n" + row[0].upper())
    ans = ""
    next_room = None
    ans = input(">")
    ans = ans.lower()
    ans = re.sub(r" {2,}", " ", ans)
    prints = None
    #   if look
    if "examine" in ans:
        c.execute("SELECT name FROM object WHERE object.holder == " + str(startingRoom) + ";")
        for row in c.fetchall():
            if ("look " + str(row[0])) in ans:
                c.execute("SELECT desc FROM object WHERE object.name == '" + str(row[0]) + "';")
                prints = c.fetchall()[0][0]
                if prints:
                    print(prints + "\n")
                else:
                    print("No description given.")
                    prints = "failed"
                continue
        if prints is None:
            c.execute("SELECT name FROM object WHERE object.holder == 1;")
            for row in c.fetchall():
                if ("look " + str(row[0])) in ans:
                    c.execute("SELECT desc FROM object WHERE object.name == '" + str(row[0]) + "';")
                    prints = c.fetchall()[0][0]
                    if prints:
                        print(prints + "\n")
                    else:
                        print("No description given.")
                        prints = "failed"
                    continue
        if prints is None:
            if " look " in ans or ans == "look":
                c.execute("SELECT short_desc FROM object WHERE object.id == " + str(startingRoom) + ";")
                prints = c.fetchall()[0][0]
                if prints:
                    print(prints + "\n")
                else:
                    print("No description given.")
                    prints = "failed"
        if prints is not None:
            continue
    #   If it isn't look
    for x in {"n", "s", "e", "w", "u", "d"}:
        if (" " + x + " ") in ans or ans == x or (len(ans) > 1 and ans[len(ans)-2:len(ans)] == (" " + x)):
            #print(x)
            chosen_dir = x
            s = ("SELECT " + str(chosen_dir).upper() + " FROM object WHERE object.id == " + str(startingRoom) + ";")
            c.execute(s)
            next_room = c.fetchall()[0][0]
            if next_room is not None:
                c.execute("UPDATE object SET holder = " + str(next_room) + " WHERE object.id == 1;")
            break
conn.close()