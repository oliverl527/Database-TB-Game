import sqlite3
import re
conn = sqlite3.connect('mollys_mansion.db')


def select_comm(comm):
    c = conn.cursor()
    c.execute(comm)
    ret_str = None
    if "SELECT" in comm:
        ret_str = c.fetchall()
    c.close()
    return ret_str


def getRoomItems(sr, ans, tab):
    s = ""
    thing = select_comm("SELECT id FROM object WHERE object.holder == " + str(sr) + ";")
    if not thing:
        return "\n"
    for row in thing:
        n = select_comm("SELECT name FROM object WHERE object.id == " + str(row[0]) + ";")[0][0]
        n = n.lower()
        ans = ans.lower()
        if tab == "":
            s = s + n + getRoomItems(row[0], ans, tab + "\t")
        else:
            s = s + " - " + n + getRoomItems(row[0], ans, tab + "\t")
    return s


def item_chosen(sr, ans):
    examined_item = -1
    thing = select_comm("SELECT id FROM object WHERE object.holder == " + str(sr) + ";")
    if not thing:
        return -1
    for row in thing:
        n = select_comm("SELECT name FROM object WHERE object.id == " + str(row[0]) + ";")[0][0]
        n = n.lower()
        ans = ans.lower()
        if re.search(" " + n + " ", " " + ans + " ") is not None and \
                select_comm("SELECT COUNT(name) FROM object WHERE object.name == '" + n + "';")[0][0] == 1:
            examined_item = row[0]
            break
        elif re.search(" " + n + " "," " +  ans + " ") is not None and \
                select_comm("SELECT COUNT(id) FROM object WHERE object.name == '" + str(n) + "';")[0][0] > 1:
            ans = re.sub(n, " ", ans)
            for short_desc in select_comm("SELECT short_desc, id FROM object WHERE object.name == '" + str(n) + "';"):
                if short_desc[0] and re.search(" " + short_desc[0].lower() + " ", " " + ans + " ") is not None:
                    if examined_item == -1 \
                        or len(short_desc[0]) > \
                            len(select_comm("SELECT short_desc FROM object WHERE object.id == " + str(examined_item) + ";")[0][0]):
                            examined_item = short_desc[1]
            if examined_item == -1:
                print("\nYou need to state which one:")
                for x in select_comm("SELECT short_desc FROM object WHERE object.name == '" + str(n) + "';"):
                    print(re.sub(r" {2,}", " ", x[0] + " " + n))
                return -2
        else:
            examined_item = item_chosen(row[0], ans)
        if examined_item != -1:
            break
    return examined_item


def look(it_id):
    n = select_comm("SELECT name, is_viewed, desc, short_desc FROM object WHERE object.id == " + str(it_id) + ";")[0]
    if n[1] == 0:
        return examine(it_id)
    if n[3]:
        print(re.sub(r" {2,}", " ", "\n(" + n[3].upper() + ") " + n[0].upper()))
    else:
        print(re.sub(r" {2,}", " ", "\n" + n[0].upper()))
    if n[2]:
        print(re.sub(r" {2,}", " ", n[2]))
    else:
        print("No description given.")
    return True


def examine(item_id):
    n = select_comm("SELECT name, is_viewed, first_time_desc, short_desc FROM object WHERE object.id == " + str(item_id) + ";")[0]
    if n[1] == 0:
        select_comm("UPDATE object SET is_viewed = 1 WHERE object.id == " + str(item_id) + ";")
    if n[3]:
        print(re.sub(r" {2,}", " ", "\n(" + n[3].upper() + ") " + n[0].upper()))
    else:
        print(re.sub(r" {2,}", " ", "\n" + n[0].upper()))
    if n[2]:
        print(re.sub(r" {2,}", " ", n[2]))
    else:
        print("No description given.")
    return True


def move(ans, sr):
    for x in {"n", "s", "e", "w", "u", "d"}:
        if re.search(" " + x + " ", " " + ans + " "):
            chosen_dir = x
            next_room = select_comm("SELECT " + str(chosen_dir) + " FROM object WHERE object.id == " + str(sr) + ";")[0][0]
            if next_room is not None:
                select_comm("UPDATE object SET holder = " + str(next_room) + " WHERE object.id == 1;")
                look(next_room)
            else:
                print("\nThat's not a valid exit!")
            return True
    return False


def get(item_id, cr):
    n = select_comm("SELECT name, is_getable FROM object WHERE object.id == " + str(item_id) + ";")[0]
    if n[1] == 0:    # possible lock check: if is_movable(item_id, cr) is False:
        print("\nYou cannot get that.")
        return False
    for row in select_comm("SELECT id FROM object WHERE object.holder == 1;"):
        if row[0] == item_id:
            print("\nYou already have that!")
            return False
    print(re.sub(r" {2,}", " ", "\nGot " + n[0] + get_chain(item_id, cr) + "."))
    select_comm("UPDATE object SET holder = 1 WHERE object.id == " + str(item_id) + ";")
    return True


def drop(item_id, ans, cr):
    n = select_comm("SELECT name, is_getable FROM object WHERE object.id == " + str(item_id) + ";")[0]
    inv_item = item_chosen(1, ans)
    if inv_item < 0:
        print("\nYou don't have that item in your inventory.")
        return False
    if n[1] == 0:    # Possible lock check: if is_movable(item_id, cr) is False:
        print("\nYou cannot drop this.")
        return False
    print("\nDropped " + n[0] + get_chain(item_id, cr) + ".")
    select_comm("UPDATE object SET holder = " + str(cr) + " WHERE object.id == " + str(item_id) + ";")
    return True


def get_chain(item_id, cr):
    n = select_comm("SELECT holder FROM object WHERE object.id == " + str(item_id) + ";")[0][0]
    n2 = select_comm("SELECT name, holder FROM object WHERE object.id == " + str(n) + ";")[0]
    if n == 1 or n == cr:
        return ""
    if n2[1] == cr or n2[1] == 1:
        return str("(from " + n2[0] + ")")
    return str("(from " + n2[0] + ")") + get_chain(n, cr)


# def  is_movable(item_id, cr):
#    # TODO: general thought was that you can't get something from something that can't be taken
#    # TODO: but its more like you can't take something that has a lock so maybe this code can be
#    # TODO: used for the lock command.
#     if item_id == cr or item_id == 1:
#        return True
#     n = select_comm("SELECT holder, is_getable FROM object WHERE object.id == " + str(item_id) + ";")[0]
#     if n[1] == 0:
#         return False
#     return is_movable(n[0], cr)


if __name__ == '__main__':
    i = 0
    # starting resources
    print("quit to exit the game. Inventory shortcut is inv.")
    print(select_comm("SELECT desc FROM object WHERE object.id == 0;")[0][0] + "\n")
    starting_room = select_comm("SELECT holder FROM object WHERE object.id == 1;")[0][0]
    look(starting_room)
    answer = ""
    # while room isn't the hidden default room and while the player doesn't want to quit
    while starting_room != 0 and answer != "quit":
        starting_room = select_comm("SELECT holder FROM object WHERE object.id == 1;")[0][0]
        #print("room items:\n" + getRoomItems(starting_room, answer, ""))
        #directions = ["N", "E", "S", "W", "U", "D"]
        #for xx in directions:
        #    x = select_comm("SELECT " + str(xx) + " FROM object WHERE object.id == " + str(starting_room) + ";")[0][0]
        #    if x is not None:
        #        print(xx + ": " + select_comm("SELECT name FROM object WHERE object.id == " + str(x) + ";")[0][0])
        answer = input(">")
        answer = re.sub(r" {2,}", " ", answer.lower())
        if answer == "quit":
            print("Quitting the game.")
            continue
        elif re.search(" inventory ", " " + answer + " ") is not None or re.search(" inv ", " " + answer + " ") is not None:
            print("\nINVENTORY:")
            for row in select_comm("SELECT name FROM object WHERE object.holder == 1;"):
                print(row[0])
            continue
        # gets the verb in the str
        verb_chosen = None
        for row in select_comm("SELECT verb, verb_id FROM verbs;"):
            if re.search(" " + row[0] + " ", " " + answer + " ") is not None:
                if not verb_chosen or len(row[0]) > len(verb_chosen[0]):
                    verb_chosen = row
        if verb_chosen is not None:
            answer = re.sub(verb_chosen[0], " ", answer)  # TODO: remove this line if you don't care about partitions.
        else:
            answer = ""
        # gets the item in the string
        it = item_chosen(starting_room, answer)
        # checks to see if the command is valid
        if not verb_chosen:
            print("\nI could not understand that.")
            continue
        if it == -2:
            ans = input(">")
            ans = re.sub(r" {2,}", " ", ans.lower())
            it = item_chosen(starting_room, ans)
        if it == -1 and verb_chosen[1] == 1:
            look(starting_room)
        elif it == -1 and verb_chosen[1] == 2:
            examine(starting_room)
        elif (3 < verb_chosen[1]) and (verb_chosen[1] < 10):
            move(select_comm("SELECT verb FROM verbs WHERE verbs.id == " + str(verb_chosen[1]) + ";")[0][0], starting_room)
        elif it == -1:
            print("\nI could not read past '" + verb_chosen[0] + "'.")
        elif verb_chosen[1] == 0:
            get(it, starting_room)
        elif verb_chosen[1] == 1:
            look(it)
        elif verb_chosen[1] == 2:
            examine(it)
        elif verb_chosen[1] == 3:
            drop(it, answer, starting_room)
        else:
            print("\nCommands aren't set for this yet.")
    conn.close()
