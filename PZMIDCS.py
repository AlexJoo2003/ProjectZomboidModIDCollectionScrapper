import requests
from bs4 import BeautifulSoup
import re

# Request the collection page
user_is_choosing = True
while user_is_choosing:
    ans = input("Input the link to the steam mod collection >>> ")
    print("Requesting the mod collection page...")
    response = requests.get(ans)
    if response.status_code >= 200 and response.status_code < 300:
        user_is_choosing = False
        break
    else:
        print("This page doesn't exist, try again")
        continue

soup = BeautifulSoup(response.content, "html.parser")
print("Page recieved!")

# Get urls to each individual mod in said collection
print("Getting urls for each mod...")
itemURLs = []
for item in soup.find_all("div", {"class":"workshopItem"}):
    itemURLs.append(item.find("a").get("href"))
print(f"{len(itemURLs)} links gathered!")

print("Getting the Mod Ids and the WorkshopId...")
mods = {}
mod_id_regex = re.compile(r"mod\s*id\s*:\s*(.+)", re.IGNORECASE)
i = 0
for url in itemURLs:
    # Get Workshop Id
    workshop_id = url.split('=')[-1]
    # Request each mod page
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    # Gets the description in text includes tags
    description = soup.find("div", {"class": "workshopItemDescription"}).prettify()
    # Extract one or more Mod_id values
    mod_id_values = []
    mod_id_matches = mod_id_regex.findall(description)
    for match in mod_id_matches:
        mod_id_value = match.split(":")[-1].strip()
        mod_id_values.append(mod_id_value)

    # Get all of the mod IDs and WorkshopIDs in a list
    if mod_id_values and workshop_id:
        mods.setdefault(workshop_id, mod_id_values)
        i += 1
        print(f"{i}/{len(itemURLs)} mods gathered.\r", end='')
    else:
        print("Couldn't get the data from this url: ", url)
print("\nDone!")

print("Select one or more options when multiple are available.")
for workshop_id in mods:
    mod_id_values = mods[workshop_id]
    if len(mod_id_values) > 1:
        url = "https://steamcommunity.com/sharedfiles/filedetails/?id="+workshop_id
        # Manage user input of multiple options
        user_is_choosing = True
        while user_is_choosing:
            print()
            print(url)
            print("This mod has several options to pick from:")
            i = 0
            for id in mod_id_values:
                print(f"\t{i}. {mod_id_values[i]}")
                i += 1
            ans = input("Write only the numbers of the options you want to choose >>> ")
            for letter in ans:
                user_is_choosing = False
                if not letter.isdigit():
                    print("Please use only digits.")
                    user_is_choosing = True
                    break
                elif int(letter) >= len(mod_id_values):
                    print("Please only use provided digits")
                    user_is_choosing = True
                    break
            if user_is_choosing:
                continue
            else:
                print("You chose: ", end='')
                for digit in ans:
                    print("\t"+mod_id_values[int(digit)], end='')
                print()
                confirm = input("Is that correct? [Y/n] >>> ")
                if confirm == "" or confirm.lower() == "yes" or confirm.lower() == 'y':
                    # Once choise is confirmed, remove the unnesesary mod_id values
                    new_mod_id_values = []
                    for digit in ans:
                        digit = int(digit)
                        new_mod_id_values.append(mod_id_values[digit])
                    mods[workshop_id] = new_mod_id_values
                    print("Choise is saved")
                    print("====================================================")
                    break
                else:
                    print("Please choose again.")
                    user_is_choosing = True
                    continue
print("All options have been selected!")
print("Generating the strings...")
workshop_id_string = "WorkshopItems="
mod_id_string = "Mods="
for workshop_id in mods:
    workshop_id_string += workshop_id+';'
    for mod in mods[workshop_id]:
        mod_id_string += mod+';'
workshop_id_string = workshop_id_string[:-1]
mod_id_string = mod_id_string[:-1]
print()
print(workshop_id_string)
print()
print(mod_id_string)
print()
print("Replace the values in your servertest.ini with these in your Server folder")


