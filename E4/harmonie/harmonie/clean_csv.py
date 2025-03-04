import csv

csvfile_input = open('musicshop0100.csv', encoding='utf-8')
reader = csv.reader(csvfile_input, delimiter=",")

csvfile_output = open('musicshop0100_clean.csv', 'a', newline='')
writer = csv.writer(csvfile_output)

writer.writerow((''))

for row in reader:
    for i in len(row):
        if row[i]:
            row[i] = row[i].strip()
