import sys
from typing import Dict

from PassHub_sync.clipboard import copy
from PassHub_sync.password import generate_password
from PassHub_sync.profile import create_profile
from PassHub_sync.security import get_master_password
from PassHub_sync.storage import load_profiles, delete_profile, update_profile_counter
from PassHub_sync.ui import _Table, get_mode, set_table_prompts


def _list_profiles() -> None:
    table = _Table()
    profiles = load_profiles().items()

    for _id, profile in profiles: table.add_row(_id, profile)

    if len(profiles) == 0:
        table.tabulate()
        sys.exit(0)

    table.tabulate()


def _select_profile(only_id: bool = False) -> Dict[str, str] | str | None:
    ask = input(f"\n{get_mode()} > ")

    if ask == "q" or ask == "quit" or ask == "exit":
        sys.exit(0)

    if only_id:
        return ask

    if ask == "v" or ask == "view":
        _list_profiles()
        return None

    try:
        return load_profiles()[ask]
    except KeyError:
        print("Invalid Input!")
        return None


def add_profile() -> None:
    site, username, counter, length = input("Site: "), input("Username / E-Mail: "), \
                                      input("Counter (1): ").strip(" "), input("Length (16): ").strip(" ")
    if site == "": site = "None"
    if username == "": counter = "None@None.None"
    if counter == "" or counter.isdigit() is False: counter = "1"
    if length == "" or length.isdigit() is False: length = "16"
    create_profile(site, username, counter, length)


def add_profiles() -> None:
    set_table_prompts(v=False, q=False)
    while True:
        add_profile()
        print("")
        ask = input("Continue (Y/n): ").lower().strip()
        print("")

        if ask == "n" or ask not in ["y", "n", ""]:
            _list_profiles()
            break


def remove_profile() -> None:
    set_table_prompts(q=True)
    _list_profiles()
    _id = _select_profile(only_id=True)
    delete_profile(_id)
    set_table_prompts(v=False, q=False)
    _list_profiles()


def remove_profiles() -> None:
    set_table_prompts(v=False, q=False)
    _list_profiles()
    print("\nEnter S.No. Of All Profiles You Want To Remove Seperated By Coma ','")
    print("For Example: > 1, 2, 3, 4")
    print("NOTE: Any Non-Numeric Value Will Terminate The Process")

    ids = []
    try:
        ids = [i if i.isdigit() else int(i) for i in input(f"{get_mode()} > ").replace(" ", "").split(",")]
    except ValueError as e:
        print("\nInvalid Input: ", e)
        exit(1)

    for _id in ids:
        delete_profile(_id)
    _list_profiles()


def get_password() -> None:
    set_table_prompts(v=True, q=True)
    mp_hash = get_master_password()
    _list_profiles()
    while True:
        profile = _select_profile()
        if profile is None: continue
        passwd = generate_password(profile, mp_hash)
        copy(passwd)
        print("Copied To Clipboard")


def update_password() -> None:
    set_table_prompts(q=True)
    _list_profiles()
    _id = _select_profile(only_id=True)
    if _id == "" or _id.isdigit() is False: sys.exit(2)
    counter = input("Counter: ")
    if counter == "" or counter.isdigit() is False: counter = "1"

    update_profile_counter(_id, counter)
    set_table_prompts(v=False, q=False)
    _list_profiles()


def usage() -> None:
    print("""
USAGE: PassHub_sync [Options] (add, remove, help)

Optional Arguments:
    add            add new profile
    add c          add multiple profiles at once
     
    remove         remove new profile
    remove c       remove multiple profiles at once
   
    update         change profile counter to update password
    
    help           Show this help menu
    """)
