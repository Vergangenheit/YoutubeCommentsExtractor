import csv
import codecs


def write_to_csv(comments: list):
    with codecs.open('comments.csv', 'w', encoding='utf-8', errors='ignore') as comments_file:
        comments_writer = csv.writer(comments_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        comments_writer.writerow(['Video ID', 'Title', 'Comment'])
        for row in comments:
            comments_writer.writerow(list(row))
