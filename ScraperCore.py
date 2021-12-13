# -*- coding: utf-8 -*-


import time, json
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from multiprocessing.pool import ThreadPool


# Main crawler class
class ImageCrawler():
    
    def __init__(self, job_id, urls, workers=1):       
        
        self.links = set()
        self.image_links = set()
        self.id = job_id
        self.initial_url = list(set(urls))
        self.workers = workers
        self.results = {}
        self.dones = 0
        self.writePath = "job_info/"+ job_id
        self.status = {'completed': self.dones, 'in_progress': len(self.initial_url)-self.dones}
        self.validFormats = ('.png', '.gif', '.jpg', '.jpeg', '.PNG', '.GIF', '.JPG', '.JPEG')
        
        # self.levels = level
        # self.max_links_per_level = max_links_per_level
    
    
    # First collect set of all valid webpage urls from parent and child urls for each given parent url.
    # Then scrape all valid image links from the collected urls.
    def scrape_site(self):
        
        with ThreadPool(self.workers) as tp:
            links_previous_level = tp.map(self.get_links, self.initial_url)
        
        # Add parent url to set of child urls for each parent url.
        for i in range(len(self.initial_url)):
            links_previous_level[i].add(self.initial_url[i])
        
        # Scrape all valid image urls from set of collected urls for each parent.
        for base in links_previous_level:
            with ThreadPool(self.workers) as tp:
                images_in_link = tp.map(self.fetch_image_urls, base)
            
            self.results[self.initial_url[self.dones]] = list(frozenset().union(*images_in_link))
            self.dones += 1            
            
            # Update job status.
            self.status['completed']= self.dones
            self.status['in_progress']= len(self.initial_url)-self.dones
    
            with open(self.writePath+'/status.txt', 'w') as outfile:
                json.dump(self.status, outfile)
        
        # Write results.
        with open(self.writePath+'/results.txt', 'w') as outfile:
            json.dump(self.results, outfile)
        
        
 
        # for i in range (self.levels):
        #     links_this_level = set()
        #     for link in links_previous_level:
        #         link_to_visit = link[0]
 
        #         new_set = self.get_links(link_to_visit, i) or set()
        #         links_this_level = links_this_level.union(new_set)
 
        #     links_previous_level = links_this_level.copy()
        #     self.links = self.links.union(links_this_level)
        
        # total_links = len(self.links)
        # done_links = 0
    
    
    # Function for scraping valid webpage urls.
    def get_links(self, url):
        try:
            resp = urllib.request.urlopen(url)
            soup = BeautifulSoup(resp, from_encoding=resp.info().get_param('charset'), features="html.parser")
            hrefs = soup.find_all('a', href=True)
            links = set()
            for href in hrefs:
                href_to_append = href['href']
                if (href_to_append[:4] == "http"):
                    links.add(href_to_append)
            
            return links
        except Exception:
            pass
            
    # Function for scraping valid image urls.
    def fetch_image_urls(self, url:str, sleep_between_interactions:int=3):
        def scroll_to_end(wd):
            wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(sleep_between_interactions)
        
        # Multiple options for chromedriver to avoid known issues in Docker.
        DRIVER_PATH = 'chromedriver.exe'    
        
        options = Options()
        # options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument("window-size=1920x1080")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-extensions")
        options.add_argument('--ignore-certificate-errors')
        
        options.add_argument('--disable-dev-shm-usage') # Not used but can be an option
        
        prefs = {
        "download_restrictions": 3,
        }
        options.add_experimental_option(
            "prefs", prefs
        )
        
        # wd = webdriver.Chrome(executable_path= DRIVER_PATH, options=options)
        
        # Each thread is allocated its own webdriver.
        wd = webdriver.Chrome(options=options)

        wd.get(url)
    
        image_urls = set()
        results_start = 0
        scroll_to_end(wd)

        # Get all image thumbnail results.
        thumbnail_results = wd.find_elements_by_css_selector("img")
        
        number_results = len(thumbnail_results)
                
        for img in thumbnail_results[results_start:number_results]:
            # Try to click every thumbnail so that we can get the real image associatd with it.
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # Extract image urls.
            actual_images = wd.find_elements_by_css_selector('img')
            
            for actual_image in actual_images:
                try:
                    if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src') and any([s in actual_image.get_attribute('src') for s in self.validFormats]):
                        image_urls.add(actual_image.get_attribute('src'))
                except Exception:
                    continue

            # image_count = len(image_urls)

            # if len(image_urls) >= self.max_links_per_level:
            #     print(f"Found: {len(image_urls)} image links, done!")
            #     break
            # else:
            #     print("Found:", len(image_urls), "image links, looking for more ...")
            #     time.sleep(30)
            #     return
        
        # load_more_button = wd.find_element_by_css_selector(".mye4qd")
        # if load_more_button:
        #     wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        # results_start = len(thumbnail_results)
        
        wd.close()
        wd.quit()
    
        return image_urls
    
    
    # def save_urls_to_csv(self):
    #    # print('URL', image_urls)
    #    df = pd.DataFrame({"links": list(self.image_links)})
    #    df.drop_duplicates()
    #    df.to_csv("links.csv", index=False, encoding="utf-8")
    
    
    
    
        
        







