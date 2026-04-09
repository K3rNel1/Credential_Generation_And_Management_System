# Project: Credential Generation and Management System
# Author: Ali Zubair Shah
# GitHub: https://github.com/K3rNel1 
# CUI version
def main():
    import random
    import sqlite3
    import os
    
    os.system('attrib +h passwords.db')

    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS passwords (key TEXT PRIMARY KEY, password TEXT)")

    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890@#!$&"

    print("----------------------------------------------------------------------------")
    print("\n Welcome to Password Manager!\n")
    print("1 : Generate password")
    print("2 : Save your own password")
    print("3 : Saved passwords")
    print("4 : Update saved passwords")

    option = int(input("\n [1/2/3/4] : "))

    if option == 3:
        cursor.execute("SELECT * FROM passwords")
        rows = cursor.fetchall()
        if rows:
            print("\n Saved passwords:")
            for key, pwd in rows:
                print(f"\n Key: {key}, Password: {pwd}")

            opt = input("\n Do you want to delete any password? [y/n] : ").lower()
            if opt == "n":
                print("\n Task Completed \n")
            elif opt == "y":
                key = input("\n Enter the key of the password to delete: ")
                cursor.execute("DELETE FROM passwords WHERE key = ?", (key,))
                conn.commit()
                print("\n password for", key, "deleted.")
            else:
                print("\n Invalid option\n")
        else:
            print("\n No passwords saved\n")

    if option == 1:
        password = ""
        length = int(input("\n Enter the length of required password : "))
        for i in range(length):
            password += random.choice(chars)

        print("\n Generated password : ", password)
        sav = input("\n Do you want to save this password [y/n] : ").lower()

        if sav == "n":
            print("\n Task Completed\n")
        elif sav == "y":
            key = input("\n Enter a key for the password : ")
            cursor.execute(
                "INSERT OR REPLACE INTO passwords (key, password) VALUES (?, ?)",
                (key, password),
            )
            conn.commit()
            print("\n Password for", key, "saved")
        else:
            print("\n Invalid Option\n")

    if option == 2:
        key = input("\n Enter a key for the password : ")
        password = input("\n Enter the password : ")
        cursor.execute(
            "INSERT OR REPLACE INTO passwords (key, password) VALUES (?, ?)",
            (key, password),
        )
        conn.commit()
        print("\n Password for", key, "saved")

    if option == 4:
        cursor.execute("SELECT * FROM passwords")
        rows = cursor.fetchall()
        if rows:
            for key, pwd in rows:
                print(f"\n Key: {key}, Password: {pwd}")

            key = input("\n Enter the key of the password : ")
            password = input("\n Enter the updated password : ")
            cursor.execute(
                "REPLACE INTO passwords (key, password) VALUES (?, ?)",
                (key, password),
            )
            conn.commit()
            print("\n Password for", key, "updated to", password)
        else:
            print("\n No passwords saved\n")
    conn.close()

while True:
    main()
