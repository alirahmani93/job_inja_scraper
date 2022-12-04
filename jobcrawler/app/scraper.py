import json
import re

from bs4 import BeautifulSoup
import requests
from django.db.transaction import atomic

from .models import Job, Company

__all__ = ['job_inja', ]


def bs4_print(content, t=None):
    if t == 'l':
        return print(len(content))
    return print(content.text)


def bs4_return(content, cat=None):
    content: str = content.text
    content_ = content
    if cat == 'title':
        content_ = re.sub("(\(d*.*)", '', content)
    content_ = content_.replace('  ', '').replace('\n', '')
    if content_ == '':
        content_ = content

    return content_


location_option = [
    "تهران", "خراسان رضوی", "اصفهان", "البرز", "فارس", "قم", "آذربایجان شرقی", "مازندران", "گیلان", "کرمان", "خوزستان",
    "یزد", "هرمزگان", "قزوین", "گلستان", "مرکزی", "بوشهر", "سمنان", "آذربایجان غربی", "اردبیل", "همدان",
    "سیستان و بلوچستان", "کردستان", "زنجان", "کرمانشاه", "لرستان", "خراسان جنوبی", "چهارمحال بختیاری", "خراسان شمالی",
    "ایلام", "کهکیلویه و بویراحمد",
]


class JobInjaScaper(object):
    _job_inja = None

    def __init__(self):
        super(JobInjaScaper, self).__init__()
        self.session = requests.session()

        self.base_url: str = 'https://jobinja.ir/'
        self.filter_url: str = "jobs?"

        self.page_number = 0
        self.locations: list = location_option
        self.html_text = None
        self.soup: [BeautifulSoup | None] = None
        self.all_soup_pages: list = []
        self.temp_file: list = []

    def clean_data(self):
        self.page_number = 0
        self.html_text = None
        self.soup = None
        self.all_soup_pages.clear()
        self.temp_file.clear()
        return

    @staticmethod
    def job_inja():  # singleton
        if not JobInjaScaper._job_inja:
            JobInjaScaper._job_inja = JobInjaScaper()
        return JobInjaScaper._job_inja

    def _prepare_url(self, title: str = '', location: str = '', job_category: str = ''):
        t_ = self.base_url + self.filter_url
        t1 = f"filters[keywords][]={title}&"
        t2 = f"filters[locations][]={location}&"
        t3 = f"filters[job_categories][]={job_category}&"

        return t_ + t1 + t2 + t3 + "b="

    @staticmethod
    def _soup_object(html):
        return BeautifulSoup(html, 'lxml')

    def send_first_request(self, title: str = '', location: str = '', job_category: str = ''):
        self.html_text = self.session.get(
            self._prepare_url(title=title, location=location, job_category=job_category)).content
        self.soup = self._soup_object(html=self.html_text)
        self._iterate_pages()
        return True

    def _paginator(self) -> list:
        paginate = self.soup.find('div', class_='paginator')
        pages = []
        for l in paginate.ul:
            tag_a = l.find('a')
            if not (not tag_a or tag_a == -1):
                pages.append(tag_a['href'])
        page_link_sample = pages[0].split('page=')[0]
        temp_page_number = [int(i.split('page=')[-1]) for i in sorted(pages)]

        ma, mi = max(temp_page_number), min(temp_page_number)
        return [page_link_sample + 'page=' + str(i) for i in range(mi, ma + 1)]

    @atomic
    def _iterate_pages(self):
        pages: list = self._paginator()
        print("page number: ", end=' ')

        self._calculate_job_list_page(sp=self.soup)

        for p in pages:
            self.all_soup_pages.append(self._soup_object(html=self.session.get(url=p, timeout=30).content))
        for html_bs4 in self.all_soup_pages:
            self._calculate_job_list_page(sp=html_bs4)
        # self._write_to_file(self.temp_file)
        self._to_db()
        self.clean_data()

    def _calculate_job_list_page(self, sp: BeautifulSoup):
        print(self.page_number, end=' // ')
        jobs = sp.find_all('div', class_='o-listView__itemWrap c-jobListView__itemWrap u-clearFix')
        jobs_info: [list | dict] = []
        for index, job in enumerate(jobs):
            info: dict = {}

            job_title_element = job.h3
            job_title_a = job_title_element.a
            job_title_link = job_title_a['href']
            publish_time = job_title_element.span

            info.update(
                {
                    'link': job_title_link,
                    'title': bs4_return(job_title_element, cat='title'),
                    'publish_time': bs4_return(publish_time),
                    'code': job_title_link.split('jobs/')[1].split('/')[0],
                    'company_name_en': job_title_link.split('companies/')[1].split('/')[0]

                })

            # job info
            li_tag = job.find_all('li', class_='c-jobListView__metaItem')

            for j, il in enumerate(li_tag):
                z = il.find('span')
                if j == 0:
                    info.update({'company': bs4_return(z)})
                elif j == 1:
                    info.update({'location': bs4_return(z)})
                elif j == 2:
                    info.update({'salary': bs4_return(z)})

            jobs_info.append(info)
        self.page_number += 1
        self.temp_file.append(jobs_info)

    @staticmethod
    def _write_to_file(content: list[dict]):
        print('====' * 5)
        print(len(content))
        with open('./my_file.json', mode='a', encoding='utf8') as f:
            json.dump(content, f, indent=3, ensure_ascii=False)

    def _to_db(self):
        job_list = []
        jobs = Job.objects.all()

        for page in self.temp_file:
            for job in page:
                c = job['company']
                job_code = job['code']
                company_name_en = job['company_name_en']
                company, _ = Company.objects.get_or_create(name=c, **{'title': company_name_en})

                if not jobs.filter(code=job_code, company=company).exists():
                    job_list.append(
                        Job(
                            title=job['title'],
                            location=job['location'],
                            company=company,
                            salary=job['salary'],
                            publish_time=job['publish_time'],
                            link=job['link'],
                            code=job_code
                        )
                    )
        Job.objects.bulk_create(job_list, batch_size=10)

    def get_detail_page(self):
        def req(link_):
            return self.session.get(link_)

        jobs = Job.objects.all()
        links = jobs.values_list('link', flat=True)[:2]

        result = list(map(lambda link_: self.session.get(link_).content.decode(), links))

        for html in result:
            sp = BeautifulSoup(html, 'lxml')
            main_div = sp.find('div', class_='col-md-8 col-sm-12 js-fixedWidgetSide')
            ul_tag = main_div.find('ul', class_='c-jobView__firstInfoBox c-infoBox')
            description_tag = main_div.find_all('div', class_='o-box__text s-jobDesc c-pr40p')
            print(description_tag)
            for tag in description_tag:
                print(tag)
            break
            # x = []
            # li_tags = ul_tag.find_all('li', class_='c-infoBox__item')
            # items: list[tuple] = []
            # for l in li_tags:
            #     items.append((l.h4.text, re.sub(r'\s+', "", l.div.text).replace('\u200c', ' ')))
            # # print(items)
            # text_box = main_div.find('div', class_='o-box__text s-jobDesc c-pr40p')
            # print(main_div.selection)
            # # info_box_li = text_box.find_all('li', class_='c-infoBox')



job_inja = JobInjaScaper.job_inja()
