from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime
import json

class Crawler:
    def __init__(self, url, page_num, page_len):
        self.url = url
        self.page_num = page_num
        self.page_len = page_len
        self.data = []

    def execute_crawling(self, driver):
        # execute_crawling 메서드는 서브클래스에서 반드시 구현되어야 합니다.
        raise NotImplementedError("서브클래스에서 execute_crawling 메서드를 구현해야 합니다.")

class NormalCrawler(Crawler):
    def execute_crawling(self, driver):
        # 기존에 크롤링한 데이터를 저장하는 집합(set)
        existing_data_titles = set(item['title'] for item in self.data)

        for i in range(self.page_num, self.page_num + self.page_len + 1):
            script = f"goPaging({i})"
            driver.execute_script(script)

            page_content = driver.page_source
            soup = BeautifulSoup(page_content, "html.parser")

            tr_tags = soup.find_all("tr")

            for tr_tag in tr_tags:
                td_tags = tr_tag.find_all("td")
                single_data = {}

                if len(td_tags) == 0:
                    continue
                elif (td_tags[-1].text.strip()).isdigit():
                    single_data['title'] = td_tags[1].text.strip()
                    date_str = td_tags[3].text.strip().replace('.', '')
                else:
                    single_data['title'] = td_tags[2].text.strip()
                    date_str = td_tags[4].text.strip().replace('.', '')

                # '\n'과 '\t'를 제거하고 '새로운 글'을 제거한 깨끗한 텍스트 얻기
                clean_title = single_data['title'].replace('\n', '').replace('\t', '').replace('새로운 글', '').strip()

                # 기존 데이터와 중복되는지 확인 후 중복되지 않으면 추가
                if clean_title not in existing_data_titles:
                    single_data['title'] = clean_title
                    single_data['date'] = int(datetime.strptime(date_str, "%Y%m%d").timestamp())

                    # data_id와 링크를 추가
                    a_tag = tr_tag.find("a", class_="nttInfoBtn")
                    if a_tag:
                        single_data['data_id'] = a_tag.get('data-id')

                        fixed_url=self.url.replace('List','Info')
                        link = f"{fixed_url}&nttSn={single_data['data_id']}"
                        single_data['link'] = link

                    self.data.append(single_data)
                    # 추가한 데이터의 타이틀을 기존 데이터에 추가
                    existing_data_titles.add(clean_title)

    def crawl(self):
        return self.data



class BooksCrawler(Crawler):
    def execute_crawling(self, driver):
        for i in range(self.page_num, self.page_num + self.page_len + 1):
            script = f"pagingSubmit('{i}')"
            driver.execute_script(script)

            # 'board_list' 클래스를 가진 엘리먼트를 찾음
            board_list = driver.find_element(By.CLASS_NAME, 'board_list')
            li_elements = board_list.find_elements(By.TAG_NAME, 'li')

            for li in li_elements:
                single_data = {}
                single_data_rows = li.text.split("\n")

                if len(single_data_rows) > 1:
                    title = single_data_rows[1]
                    if len(title.split('\n')) == 0:
                        single_data['title'] = title
                    else:
                        single_data['title'] = title.split('\n')

                    date_str = single_data_rows[4].replace('.', '')
                    # 날짜 문자열을 타임스탬프로 변환
                    single_data['date'] = int(datetime.strptime(date_str, "%Y%m%d").timestamp())

                    self.data.append(single_data)

    def crawl(self):
        return self.data

class LibCrawler(Crawler):
    def execute_crawling(self, driver):
        # 공지사항 목록 추출
        articles = driver.find_elements(By.CSS_SELECTOR, 'tr.ikc-item[ng-repeat="article in articles"]')
        # 결과를 저장할 리스트 초기화
        data = []
        existing_data_titles = set()  # 중복 데이터를 확인하기 위한 집합(set) 초기화

        for article in articles:
            # 기사 제목 추출
            title_script = "return arguments[0].querySelector('span[ng-bind=\"article.title\"]').innerText"
            title = driver.execute_script(title_script, article)
            # 최종 업데이트 날짜 추출
            date_script = "return arguments[0].querySelector('span[ng-if=\"!isShowLastUpdated\"]').innerText"
            date_str = driver.execute_script(date_script, article)

            # date의 .없앰
            date_str = date_str.replace('.', '')

            # date를 timestamp로 변환
            date_timestamp = int(datetime.strptime(date_str, "%Y%m%d").timestamp())

            # 공지사항 주소를 가져오기위함
            a_tag = article.find_element(By.CLASS_NAME, 'ikc-item-title')
            href = a_tag.get_attribute('href')

            # 링크를 구현
            link = f"https://lib.gnu.ac.kr/index.html{href}"

            # 같은거 있는지 확인
            if title not in existing_data_titles:
                
                existing_data_titles.add(title)

                # 추출된 데이터로 딕셔너리 생성
                single_data = {
                    "title": title,
                    "date": date_timestamp,
                    "link": link  # 링크 추가
                }
                # 결과 데이터 리스트에 현재 항목의 데이터를 추가
                data.append(single_data)

        self.data = data

    def crawl(self):
        return self.data




def crawling_page(url: str, page_num, page_len):
    crawling_data = {}
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(10)

    if url.startswith('https://books'):
        # BooksCrawler 인스턴스 생성
        crawler = BooksCrawler(url, page_num, page_len)
    elif url.startswith('https://www.gnu.ac.kr'):
        # NormalCrawler 인스턴스 생성
        crawler = NormalCrawler(url, page_num, page_len)
    elif url.startswith('https://lib.gnu.ac.kr'):
        # LibCrawler 인스턴스 생성
        crawler = LibCrawler(url, page_num, page_len)
    else:
        raise ValueError("Unsupported URL")

    # execute_crawling 메서드 실행
    crawler.execute_crawling(driver)
    crawling_data["data"] = crawler.crawl()

    driver.quit()

    return json.dumps(crawling_data, indent=4)

if __name__ == "__main__":
    # 예시 URL로 크롤링 실행
    print(json.loads(crawling_page("https://books.gnu.ac.kr/local/board/boardList.do?biserial=101", 1, 1)))
    print(json.loads(crawling_page("https://www.gnu.ac.kr/dorm/na/ntt/selectNttList.do?mi=7360&bbsId=2507", 1, 1)))
    print(json.loads(crawling_page("https://lib.gnu.ac.kr/index.html#/bbs/notice?offset=0&max=20", 1, 1)))
