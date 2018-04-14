import json
import sys
import itertools


def fix(s):
    if '"' in s:
        s = s.replace('"', "_")
    if ',' in s:
        s = s.replace(',', "_")
    return s


def create_authors_csv():
    print("Getting author names")
    authors = set()
    for i in range(1, len(sys.argv)):
        with open(sys.argv[i]) as FileObj:
            for line in FileObj:
                j = json.loads(line)
                if 'authors' not in j:
                    continue
                for auth in j['authors']:
                    auth = fix(auth)
                    authors.add(auth)
                    # break

    print("Dumping author names")
    f = open("csv_data/authors.csv", "w")
    f.write("name:ID(author)\n")
    for auth in authors:
        f.write('"%s"\n' % auth)
    f.close()
    print("authors - done!")


def create_publications_csv():
    print("Getting publication data")
    publications = []
    for i in range(1, len(sys.argv)):
        with open(sys.argv[i]) as FileObj:
            for line in FileObj:
                j = json.loads(line)
                j['title'] = fix(j['title'])
                publications.append({k: j[k] for k in ('title', 'year', 'id')})
                # break
    print("Dumping publications")
    f = open("csv_data/publications.csv", "w")
    f.write("pubId:ID(publication),year:INT,title\n")
    for pub in publications:
        f.write('"%s",%d,"%s"\n' % (pub['id'], int(pub['year']), pub['title']))
    f.close()
    print("publications - done!")


def create_publication_author_relationships():
    print("Getting publication-author data")
    relationships = []
    for i in range(1, len(sys.argv)):
        with open(sys.argv[i]) as FileObj:
            for line in FileObj:
                j = json.loads(line)
                if 'authors' not in j:
                    continue
                for auth in j['authors']:
                    auth = fix(auth)
                    relationships.append((j['id'], auth))
                    # break

    print("Dumping publication-author data")
    f = open("csv_data/pub_auth.csv", "w")
    f.write(":START_ID(publication),:END_ID(author)\n")
    for rel in relationships:
        f.write('"%s","%s"\n' % (rel[0], rel[1]))
    f.close()
    print("publication-author relationships - done!")


def create_coauthorship_relationships():
    print("Getting co-authorship data")
    relationships = []
    for i in range(1, len(sys.argv)):
        with open(sys.argv[i]) as FileObj:
            for line in FileObj:
                j = json.loads(line)
                if 'authors' not in j:
                    continue
                authors = []
                for auth in j['authors']:
                    auth = fix(auth)
                    authors.append(auth)
                for pair in itertools.combinations(authors, r=2):
                    relationships.append((pair[0], pair[1], j['year']))
                # break

    print("Dumping co-authorship data")
    f = open("csv_data/coauthorship.csv", "w")
    f.write(":START_ID(author),:END_ID(author),year:INT\n")
    for rel in relationships:
        f.write('"%s","%s",%d\n' % (rel[0], rel[1], rel[2]))
    f.close()
    print("co-authorship relationships - done!")


def create_citation_relationship():
    print("Getting citation data")
    relationships = []
    for i in range(1, len(sys.argv)):
        with open(sys.argv[i]) as FileObj:
            for line in FileObj:
                j = json.loads(line)
                if 'references' not in j:
                    continue
                for ref in j['references']:
                    relationships.append((j['id'], ref))
                # break

    print("Dumping citation data")
    f = open("csv_data/citation.csv", "w")
    f.write(":START_ID(publication),:END_ID(publication)\n")
    for rel in relationships:
        f.write('"%s","%s"\n' % (rel[0], rel[1]))
    f.close()
    print("citation relationships - done!")


create_authors_csv()
create_publications_csv()
create_publication_author_relationships()
create_coauthorship_relationships()
create_citation_relationship()
