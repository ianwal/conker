import csv


def sort_csv_by_length(input_file, output_file):
    with open(input_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        sorted_rows = sorted(reader, key=lambda row: int(row["length"]))

    with open(output_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(sorted_rows)


if __name__ == "__main__":
    sort_csv_by_length("progress.game.csv", "sorted.progress.game.csv")
