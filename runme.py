import analyze
import venues
import wells


def main():
    hugo = venues.City('2394440')
    db = wells.Database()
    %debug analyze.by_venue(hugo, db)


if __name__ == "__main__":
    main()
