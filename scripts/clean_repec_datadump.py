import re
import csv
from dataclasses import dataclass, asdict


SKIP_WORDS = ['#metoo', '#MeToo', '&#039', '#FlattenTheCurve', 'Being #1',
        ' Working Paper #10', 'Report #2 in the', 'What Influences Success?#',
        '#ElectionEconomics:', '#GE2017Economists', '#KnocheRocks',
        'Selected Emerging and the Middle Eastern Countries#',
        '#FA9550-09-1-0538 and #FA9530-12-1-0359 and ONR projects #N00014-09-1-0751 and #N0014-12-1-0643.',
        '#Euromaidan', 'ISBN # 0-19',
        '#sthash.lcrcLmhg.dpuf', ' Strategy#', '#Portichiusi', '#AllLivesMatter',
        'Indian Premier League Auction#', '&#8208',
        '#EleNão', '#EleN', 'erblick #1', # TODO: have encoding fixed
        '#Brexit and #USElection', 'superseded by DP #1546',
        'revision of DP#1516',
        'Working paper #1', 'Working paper #2', 'Working paper #3',
        'Working paper #4', 'Working paper #5', 'Working paper #6',
        'Working paper #7',
        '&#64256',
        'Regular Economic Report, Issue #',
        'Evidence from EU Regions#',
        '#Crowdfunding',
        'Discussion Paper #1',
        '#Grexit',
        'Working paper #8',
        'Australian Evidence on Background Risk and Other Factors#',
]


# https://titanwolf.org/Network/Articles/Article?AID=a8397c7c-c7d6-471a-9a63-00432cfe68dc#gsc.tab=0
PIN_YIN_REGEX = "(a[io]?|ou?|e[inr]?|ang?|ng|[bmp](a[io]?|[aei]ng?|ei|ie?|ia[no]|o|u)|pou|me|m[io]u|[fw](a|[ae]ng?|ei|o|u)|fou|wai|[dt](a[io]?|an|e|[aeio]ng|ie?|ia[no]|ou|u[ino]?|uan)|dei|diu|[nl](a[io]?|ei?|[eio]ng|i[eu]?|i?ang?|iao|in|ou|u[eo]?|ve?|uan)|nen|lia|lun|[ghk](a[io]?|[ae]ng?|e|ong|ou|u[aino]?|uai|uang?)|[gh]ei|[jqx](i(ao?|ang?|e|ng?|ong|u)?|u[en]?|uan)|([csz]h?|r)([ae]ng?|ao|e|i|ou|u[ino]?|uan)|[csz](ai?|ong)|[csz]h(ai?|uai|uang)|zei|[sz]hua|([cz]h|r)ong|y(ao?|[ai]ng?|e|i|ong|ou|u[en]?|uan))"


@dataclass
class Paper:
    id: str
    title: str
    author_names: list
    year: int
    cited_by_ids: list
    working_paper: int
    publication: str
    by_top_author: bool


    def has_chinese_author(self):
        last_names = [name[0:name.index(', ')] for name in self.author_names if ', ' in name]
        for name in last_names:
            matched = re.search(PIN_YIN_REGEX, name, re.IGNORECASE)
            if matched and matched.group(1) == name:
                return True
        return False


def process_author_line(line, authors, papers):
    if not line:
        return
    author, authored_papers = get_author_papers(line)
    authors.add(author)
    papers.update(set(authored_papers))


def get_author_papers(line):
    author_papers = line.split()
    assert(len(author_papers) <=2)
    author = author_papers[0]
    papers = []
    if len(author_papers) == 2:
        paperstr = author_papers[1]
        papers = paperstr.split('#')
    return author, papers


def get_replacement_skip_word(skip_word):
    return skip_word.replace('#', '☃')

# sometimes a record may contain \n so we need f to readline when that happens
def process_paper_line(line, f, replaced=None):
    line = line.strip()
    num_fields = len(line.split('#'))
    if num_fields <=1:
        return

    if num_fields > 8:
        for skip_word in SKIP_WORDS:
            if skip_word in line:
                replacement = get_replacement_skip_word(skip_word)
                new_line = line.replace(skip_word, replacement)
                return process_paper_line(new_line, f, replaced=(skip_word, replacement))
        print(f'Malformed line with {num_fields} fields: {line}\n{line.split("#")}\n\n')
        return

    if num_fields < 8:
        line += f.readline()
        return process_paper_line(line, f)

    fields = line.split('#')
    if replaced:
        for i, f in enumerate(fields):
            if replaced[1] in f:
                fields[i] = f.replace(replaced[1], replaced[0])

    assert(fields[-1] == '')
    fields = fields[0:-1]

    id, title, author_names_str, year_str, cited_by_str, working_paper_str, publication = fields
    author_names = author_names_str.split(' ; ')
    year = int(year_str)
    cited_by_ids = cited_by_str.split('|')
    assert(working_paper_str in ['0', '1'])
    working_paper = int(working_paper_str)
    paper = Paper(id, title, author_names, year, cited_by_ids, working_paper, publication, by_top_author=False)
    return paper


def boolean_to_1_0(boo):
    return 1 if boo else 0


def list_to_str(l):
    return '; '.join(l)

def export_cleaned_paper(all_papers_by_id):
    with open('csv/repect_papers_cleaned.csv', 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        header_written = False
        for id, paper in all_papers_by_id.items():
            row = asdict(paper)
            row['by_top_author'] = boolean_to_1_0(paper.by_top_author)
            row['has_chinese_author'] = boolean_to_1_0(paper.has_chinese_author())
            row['author_names'] = list_to_str(paper.author_names)
            row['cited_by_ids'] = list_to_str(paper.cited_by_ids)

            if not header_written:
                writer.writerow(list(row.keys()))
                header_written = True
            writer.writerow(list(row.values()))


# Check that all papers in wei_authors & their citations are present in wei_papers
def check_data_completeness():
    papers = set()
    authors = set()
    with open('csv/wei_authors.csv', encoding='latin-1') as f:
        line = f.readline()
        process_author_line(line, authors, papers)
        while line:
            line = f.readline()
            process_author_line(line, authors, papers)

    print(f'Total top50 authors from datadump: {len(authors)}')
    print(f'Total paper authored by top50 authors from datadump: {len(papers)}')

    expected_paper_ids = set(papers)
    all_papers_by_id = {}
    with open('csv/wei_papers.csv', encoding='latin-1') as f:
        line = f.readline()
        paper = process_paper_line(line, f)
        if paper:
            all_papers_by_id[paper.id] = paper
            if paper.id in papers:
                expected_paper_ids.update(set(paper.cited_by_ids))
        while line:
            line = f.readline()
            paper = process_paper_line(line, f)
            if paper:
                all_papers_by_id[paper.id] = paper
                if paper.id in papers:
                    expected_paper_ids.update(set(paper.cited_by_ids))
                    paper.by_top_author = True


    expected_num_papers = len(expected_paper_ids)
    actual_paper_ids = set(all_papers_by_id.keys())
    actual_num_papers = len(actual_paper_ids)
    print(f'Expect: {expected_num_papers} papers')
    print(f'Got: {actual_num_papers} papers')
    if expected_num_papers > actual_num_papers:
        missing_ids = expected_paper_ids - actual_paper_ids
        with open('csv/missing_repec_paper_ids.csv', 'w') as f:
            f.write('\n'.join(missing_ids))

    top_missing_papers = set(papers) - actual_paper_ids
    print(f'top level missing papers: {top_missing_papers} papers')

    export_cleaned_paper(all_papers_by_id)


if __name__ == '__main__':
    check_data_completeness()
