import requests
from bs4 import BeautifulSoup

def get_twitter_trends():
    url = "https://trends24.in/colombia"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        trends_list_container = soup.select_one('#timeline-container > div.px-2.scroll-smooth.flex.gap-x-4.w-fit.pt-8 > div:nth-child(1) > ol')
        if trends_list_container:
            trends = []
            for li in trends_list_container.find_all('li'):
                trend_name = li.find('span', {'class': 'trend-name'}).text.strip()
                trend_link = li.find('a', {'class': 'trend-link'})['href']
                tweet_count = li.find('span', {'class': 'tweet-count'}).text.strip()
                trends.append({
                    'name': trend_name,
                    'link': trend_link,
                    'count': tweet_count
                })
            return trends
        else:
            return None
    else:
        return None

def print_twitter_trends(trends):
    if trends:
        for trend in trends:
            print(f"{trend['name']} - {trend['count']}")
    else:
        print("No trends found.")