import sqlite3
import re

conn = sqlite3.connect('mollys_mansion.db')
c = conn.cursor()


def move(ans, sr):
    next_room = None
    for x in {"n", "s", "e", "w", "u", "d"}:
        if (" " + x + " ") in ans or ans == x or (len(ans) > 1 and ans[len(ans)-2:len(ans)] == (" " + x)):
            chosen_dir = x
            s = ("SELECT " + str(chosen_dir) + " FROM object WHERE object.id == " + str(sr) + ";")
            c.execute(s)
            next_room = c.fetchall()[0][0]
            if next_room is not None:
                c.execute("UPDATE object SET holder = " + str(next_room) + " WHERE object.id == 1;")
                look(next_room, "look")
            else:
                print("That's not a valid exit!")
            return True
    return False


def examine(sr, ans):
    prints = None
    viewed = 0
    counter = 0
    extra_check = ""
    i = 0
    j = 0
    if "inventory" in ans or "inv" in ans:
        c.execute("SELECT name from object WHERE object.holder == 1;")
        print("\nINVENTORY:")
        for row in c.fetchall():
            print(row[0])
        return True
    while i < 2 and prints is None:
        if i == 0:
            c.execute("SELECT id FROM object WHERE object.holder == " + str(sr) + ";")
        if i == 1:
            c.execute("SELECT id FROM object WHERE object.holder == 1;")
        for row in c.fetchall():
            c.execute("SELECT name FROM object WHERE object.id == " + str(row[0]) + ";")
            name = str(c.fetchall()[0][0])
            if name in ans:
                c.execute("SELECT COUNT(name) FROM object WHERE object.name == '" + str(name) + "';")
                counter = c.fetchall()[0][0]
                if counter > 1:
                    c.execute("SELECT short_desc FROM object WHERE object.id == " + str(row[0]) + ";")
                    extra_check = c.fetchall()[0][0]
                    if not extra_check or extra_check.lower() not in ans:
                        if counter - j == 1:
                            print("\nYou need to state which " + name + ":")
                            c.execute("SELECT short_desc FROM object WHERE object.name == '" + str(name) + "';")
                            for row in c.fetchall():
                                print(row[0])
                            return True
                        j = j + 1
                        continue
                if extra_check and extra_check != "":
                    print("\n(" + extra_check.upper() + ") " + name.upper())
                else:
                    print("\n" + name.upper())
                c.execute("SELECT is_viewed FROM object WHERE object.id == " + str(row[0]) + ";")
                viewed = c.fetchall()[0][0]
                if viewed == 0:
                    c.execute("UPDATE object SET is_viewed = 1 WHERE object.id == " + str(row[0]) + ";")
                c.execute("SELECT first_time_desc FROM object WHERE object.id == " + str(row[0]) + ";")
                prints = c.fetchall()[0][0]
                if prints:
                    print(prints)
                else:
                    print("No description given.")
                    prints = "failed"
                break
        i = i + 1
    if prints is None:
        if ans == "examine":
            c.execute("SELECT name FROM object WHERE object.id == " + str(sr) + ";")
            print("\n" + c.fetchall()[0][0].upper())
            c.execute("SELECT is_viewed FROM object WHERE object.id == " + str(sr) + ";")
            viewed = c.fetchall()[0][0]
            if viewed == 0:
                c.execute("UPDATE object SET is_viewed = 1 WHERE object.id == " + str(sr) + ";")
            c.execute("SELECT first_time_desc FROM object WHERE object.id == " + str(sr) + ";")
            prints = c.fetchall()[0][0]
            if prints:
                print(prints)
            else:
                print("No description given.")
                prints = "failed"
    if prints is not None:
        return True
    return False


def look(sr, ans):
    prints = None
    viewed = 0
    extra_check = ""
    j = 0
    i = 0
    if "inventory" in ans or "inv" in ans:
        c.execute("SELECT name from object WHERE object.holder == 1;")
        print("\nINVENTORY:")
        for row in c.fetchall():
            print(row[0])
        return True
    while i < 2 and prints is None:
        if i == 0:
            c.execute("SELECT id FROM object WHERE object.holder == " + str(sr) + ";")
        if i == 1:
            c.execute("SELECT id FROM object WHERE object.holder == 1;")
        for row in c.fetchall():
            c.execute("SELECT name FROM object WHERE object.id == " + str(row[0]) + ";")
            name = str(c.fetchall()[0][0])
            if name in ans:
                c.execute("SELECT is_viewed FROM object WHERE object.id == '" + str(row[0]) + "';")
                viewed = c.fetchall()[0][0]
                if viewed == 0:
                    return examine(sr, ans.replace("look", "examine"))
                else:
                    c.execute("SELECT COUNT(name) FROM object WHERE object.name == '" + str(name) + "';")
                    counter = c.fetchall()[0][0]
                    if counter > 1:
                        c.execute("SELECT short_desc FROM object WHERE object.id == " + str(row[0]) + ";")
                        extra_check = c.fetchall()[0][0]
                        if not extra_check or extra_check.lower() not in ans:
                            if counter - j == 1:
                                print("\nYou need to state which " + name + ":")
                                c.execute("SELECT short_desc FROM object WHERE object.name == '" + str(name) + "';")
                                for row in c.fetchall():
                                    print(row[0])
                                return True
                            j = j + 1
                            continue
                    if extra_check and extra_check != "" :
                        print("\n(" + extra_check.upper() + ") "+ name.upper())
                    else:
                        print("\n" + name.upper())
                    c.execute("SELECT desc FROM object WHERE object.id == " + str(row[0]) + ";")
                    prints = c.fetchall()[0][0]
                    if prints:
                        print(prints)
                    else:
                        print("No description given.")
                        prints = "failed"
                break
        i = i + 1
    if prints is None:
        if ans == "look":
            c.execute("SELECT is_viewed FROM object WHERE object.id == " + str(sr) + ";")
            viewed = c.fetchall()[0][0]
            if viewed == 0:
                return examine(sr, ans.replace("look", "examine"))
            else:
                c.execute("SELECT name FROM object WHERE object.id == " + str(sr) + ";")
                print("\n" + c.fetchall()[0][0].upper())
                c.execute("SELECT desc FROM object WHERE object.id == " + str(sr) + ";")
                prints = c.fetchall()[0][0]
                if prints:
                    print(prints)
                else:
                    print("No description given.")
                    prints = "failed"
    if prints is not None:
        return True
    return False


def get(sr, ans):
    prints = None
    viewed = 0
    j = 0
    if "inventory" in ans or "inv" in ans:
        c.execute("SELECT name from object WHERE object.holder == 1;")
        print("\nINVENTORY:")
        for row in c.fetchall():
            print(row[0])
        return True
    c.execute("SELECT id FROM object WHERE object.holder == " + str(sr) + ";")
    for rows in c.fetchall():
        c.execute("SELECT name FROM object WHERE object.id == " + str(rows[0]) + ";")
        name = str(c.fetchall()[0][0])
        if name in ans:
            c.execute("SELECT COUNT(name) FROM object WHERE object.name == '" + str(name) + "';")
            counter = c.fetchall()[0][0]
            if counter > 1:
                c.execute("SELECT short_desc FROM object WHERE object.id == " + str(rows[0]) + ";")
                extra_check = c.fetchall()[0][0]
                if not extra_check or extra_check.lower() not in ans:
                    if counter - j == 1:
                        print("\nYou need to state which " + name + ":")
                        c.execute("SELECT short_desc FROM object WHERE object.name == '" + str(name) + "';")
                        for row in c.fetchall():
                            print(row[0])
                        return True
                    j = j + 1
                    continue
            c.execute("SELECT is_getable FROM object WHERE object.id == " + str(rows[0]))
            prints = c.fetchall()[0][0]
            if prints == 1:
                print("You got the " + name + ".")
                c.execute("UPDATE object SET holder = 1 WHERE object.id == " + str(rows[0]) + ";")
            else:
                print("You can't get this item.")
            return True
    return False


def drop(sr, ans):
    prints = None
    viewed = 0
    j = 0
    c.execute("SELECT id FROM object WHERE object.holder == 1;")
    for row in c.fetchall():
        c.execute("SELECT name FROM object WHERE object.id == " + str(row[0]) + ";")
        name = str(c.fetchall()[0][0])
        if name in ans:
            c.execute("SELECT COUNT(name) FROM object WHERE object.name == '" + str(name) + "';")
            counter = c.fetchall()[0][0]
            if counter > 1:
                c.execute("SELECT short_desc FROM object WHERE object.id == " + str(row[0]) + ";")
                extra_check = c.fetchall()[0][0]
                if not extra_check or extra_check.lower() not in ans:
                    if counter - j == 1:
                        print("\nYou need to state which " + name + ":")
                        c.execute("SELECT short_desc FROM object WHERE object.name == '" + str(name) + "';")
                        for row in c.fetchall():
                            print(row[0])
                        return True
                    j = j + 1
                    continue
            c.execute("SELECT is_getable FROM object WHERE object.id == " + str(row[0]) + ";")
            prints = c.fetchall()[0][0]
            if prints != 0:
                print("You dropped the " + name + ".")
                c.execute("UPDATE object SET holder = " + str(sr) + " WHERE object.id == " + str(row[0]) + ";")
            else:
                print("You cannot drop this item.")
            return True
        break
    return False


def inventory_check():
    if answer == "inventory" or answer == "inv":
        c.execute("SELECT name FROM object WHERE object.holder == 1;")
        print("\nINVENTORY:")
        for row in c.fetchall():
            print(row[0])
        return True
    return False


if __name__ == '__main__':
    i = 0
    print("quit to exit the game. Inventory shortcut is inv.")
    c.execute("SELECT * FROM object;")
    #   Set visited command
    c.execute("SELECT desc FROM object WHERE object.id == 0;")
    print(c.fetchall()[0][0] + "\n")
    c.execute("SELECT holder FROM object WHERE object.id == 1;")
    starting_room = c.fetchall()[0][0]
    examine(starting_room, "examine")
    answer = ""
    working = -1
    while starting_room != 0 and answer != "quit":
        c.execute("SELECT holder FROM object WHERE object.id == 1;")
        starting_room = c.fetchall()[0][0]
        answer = input(">")
        answer = answer.lower()
        answer = re.sub(r" {2,}", " ", answer)
        if answer == "quit":
            print("Quitting the game.")
            continue
        if answer == "inventory" or answer == "inv":
            c.execute("SELECT name FROM object WHERE object.holder == 1;")
            print("\nINVENTORY:")
            for row in c.fetchall():
                print(row[0])
            continue
        while working == -1 and i <= 9:
            c.execute("SELECT verb FROM verbs WHERE verbs.verb_id == " + str(i) + ";")
            for row in c.fetchall():
                if (" " + row[0] + " ") in answer \
                        or (len(answer) > len(str(row[0])) and answer[0:len(row[0]) + 1] == (row[0] + " ")) \
                        or (len(answer)-len(row[0])-1 >= 0 and (answer[len(answer)-len(row[0])-1:len(answer)+1] == (" " + row[0]))) \
                        or str(row[0]) == answer:
                    working = i
                    break
            i = i + 1
        i = 0

        if working == 0 and get(starting_room, answer) is False:
            print("Couldn't read past 'get'.")
        elif working == 1 and look(starting_room, answer) is False:
            print("Couldn't read past 'look'.")
        elif working == 2 and examine(starting_room, answer) is False:
            print("Couldn't read past 'examine'.")
        elif working == 3 and drop(starting_room, answer) is False:
            print("Couldn't read past 'drop'.")
        elif (3 < working) and (working < 10):
            c.execute("SELECT verb FROM verbs WHERE verbs.id == " + str(working) + ";")
            s = str(c.fetchall()[0][0])
            move(s, starting_room)
        elif working == -1:
            print("I couldn't understand that.")
        i = 0
        working = -1
c.close()
