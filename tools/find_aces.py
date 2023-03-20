from db_models import *


def print_all_events():
    for event in PlayerDeath.select(PlayerDeath.attacker_name, PlayerDeath.round, PlayerDeath.file):
        print(event.attacker_name.ljust(30), str(event.round).ljust(5), event.file.ljust(20))


def main():
    aces = PlayerDeath.select(PlayerDeath.attacker_name, PlayerDeath.round, PlayerDeath.file,
                              fn.COUNT(PlayerDeath.attacker_name).alias('ct')).group_by(
        PlayerDeath.attacker_name, PlayerDeath.file, PlayerDeath.round).order_by(PlayerDeath.file, PlayerDeath.round,
                                                                                 PlayerDeath.attacker_name)
    print(aces)

    for ace in aces:
        if ace.ct == 4:
            print(ace.attacker_name.ljust(20), str(ace.round).ljust(5), str(ace.ct).ljust(5), ace.file.ljust(20))


if __name__ == "__main__":
    # print_all_events()
    main()
