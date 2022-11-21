from functions.manage import addMovie, addSeries, removeMovie, removeSeries
from config import db_url


def add():
    id = input("enter imdb id: ")
    stream = input("enter stream link: ")
    type = int(input("enter type: 1: movie, 2: series : "))
    if type not in [1, 2]:
        print("enter 1 or 2")
        return

    if type == 1:
        addMovie(id, stream, db_url)
    if type == 2:
        ses = input("season (enter 0 if you're adding collection): ")
        ep = input("episode (enter 0 if you're adding collection): ")

        if int(ses) != 0:
            if int(ep) != 0:
                id = id + ":" + ses + ":" + ep
            else:
                print("episode cannot be zero")

        addSeries(id, stream, db_url)


def remove():
    id = input("enter imdb id: ")
    type = int(input("enter type: 1: movie, 2: series: "))
    if type not in [1, 2]:
        print("enter 1 or 2")
        return

    if type == 1:
        removeMovie(id, db_url)
    if type == 2:
        removeSeries(id, db_url)


def main():
    try:
        a = int(input("Select what you want to do\n1: add\n2: remove\n\nans: "))
        if a not in [1, 2]:
            print("enter 1 or 2")
            return

        if a == 1:
            add()
        if a == 2:
            remove()

        print("\nSuccess")
    except ValueError:
        print("enter numbers only")
    except Exception as e:
        print(f"ERROR: {str(e)}\nHave you set valid db url in config.py?")


if __name__ == "__main__":
    main()
