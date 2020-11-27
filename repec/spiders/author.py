import scrapy


class AuthorSpider(scrapy.Spider):
    name = 'author'
    allowed_domains = ['econpapers.repec.org']
    start_urls = [
            'https://econpapers.repec.org/RAS/',
            'https://econpapers.repec.org/RAS/defaultB.htm',
            'https://econpapers.repec.org/RAS/defaultC.htm',
            'https://econpapers.repec.org/RAS/defaultD.htm',
            'https://econpapers.repec.org/RAS/defaultE.htm',
            'https://econpapers.repec.org/RAS/defaultF.htm',
            'https://econpapers.repec.org/RAS/defaultG.htm',
            'https://econpapers.repec.org/RAS/defaultH.htm',
            'https://econpapers.repec.org/RAS/defaultI.htm',
            'https://econpapers.repec.org/RAS/defaultJ.htm',
            'https://econpapers.repec.org/RAS/defaultK.htm',
            'https://econpapers.repec.org/RAS/defaultL.htm',
            'https://econpapers.repec.org/RAS/defaultM.htm',
            'https://econpapers.repec.org/RAS/defaultN.htm',
            'https://econpapers.repec.org/RAS/defaultO.htm',
            'https://econpapers.repec.org/RAS/defaultP.htm',
            'https://econpapers.repec.org/RAS/defaultQ.htm',
            'https://econpapers.repec.org/RAS/defaultS.htm',
            'https://econpapers.repec.org/RAS/defaultT.htm',
            'https://econpapers.repec.org/RAS/defaultU.htm',
            'https://econpapers.repec.org/RAS/defaultW.htm',
            'https://econpapers.repec.org/RAS/defaultX.htm',
            'https://econpapers.repec.org/RAS/defaultZ.htm',
            'https://econpapers.repec.org/RAS/default0218.htm',
            'https://econpapers.repec.org/RAS/defaultother.htm',
            'https://econpapers.repec.org/RAS/defaultotherB.htm',
            'https://econpapers.repec.org/RAS/defaultotherC.htm',
            'https://econpapers.repec.org/RAS/defaultotherD.htm',
            'https://econpapers.repec.org/RAS/defaultotherE.htm',
            'https://econpapers.repec.org/RAS/defaultotherG.htm',
            'https://econpapers.repec.org/RAS/defaultotherH.htm',
            'https://econpapers.repec.org/RAS/defaultotherI.htm',
            'https://econpapers.repec.org/RAS/defaultotherK.htm',
            'https://econpapers.repec.org/RAS/defaultotherL.htm',
            'https://econpapers.repec.org/RAS/defaultotherM.htm',
            'https://econpapers.repec.org/RAS/defaultotherN.htm',
            'https://econpapers.repec.org/RAS/defaultotherP.htm',
            'https://econpapers.repec.org/RAS/defaultotherQ.htm',
            'https://econpapers.repec.org/RAS/defaultotherS.htm',
            'https://econpapers.repec.org/RAS/defaultotherT.htm',
            'https://econpapers.repec.org/RAS/defaultotherU.htm',
            'https://econpapers.repec.org/RAS/defaultotherX.htm',
            'https://econpapers.repec.org/RAS/defaultother0218.htm',
    ]


    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f'html/author-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')

        for link in response.css('div.bodytext table td a:not(.letter)'):
            author_path = link.css('::attr(href)').get()
            author_id = author_path.split('/')[-1].split('.')[0]
            yield {
                'author_id': author_id,
                'author_name': link.css('::text').get(),
                'author_url': 'https://econpapers.repec.org' + author_path,
            }
