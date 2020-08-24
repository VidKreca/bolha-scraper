from bs4 import BeautifulSoup
import urllib.request
import time
import json


def get_all_ads(url, filter=None):
	req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	html_page = urllib.request.urlopen(req).read()
	soup = BeautifulSoup(html_page, 'html.parser').select(".EntityList-items .EntityList-item")

	# DATA
	ads = []

	for ad in soup:
		# TITLE
		title = ad.select(".entity-title")

		if len(title) > 0:
			if filter is not None and isinstance(filter, list) and len(filter) > 0:
				if any(term in title[0].text.lower() for term in filter):
					title = title[0].text
				else: continue
			else:
				title = title[0].text
		else: continue
		# PRICE
		price = ad.select("strong, .price")
		if len(price) > 0:
			price = price[0].text.strip()
		else: continue
		# LINK
		link = "bolha.com"+ad.get("data-href")

		def decode(x):
			return x.replace("\u00a0\u20ac", "eur").replace("\u0161", "s").replace("\u0160", "s").replace("\u010d", "c").replace("\u017e", "z")

		ads.append({
			"title": decode(title),
			"price": decode(price),
			"link": link
			})

	return ads


def get_new_ads(ads, refresh):
	old_links = [ad.get("link") for ad in ads]
	new = []
	
	for ad in refresh:
		if ad.get("link") not in old_links:
			new.append(ad)

	return new



def print_ads(ads):
	for ad in ads:
		try:
			print("Title: "+ad.get("title"))
			print("Price: "+ad.get("price"))
			print("Link:  "+ad.get("link"))
			print("\n")
		except: 
			pass


def set_default(obj):
	if isinstance(obj, set):
		return list(obj)



if __name__ == "__main__":
	url = "https://www.bolha.com/index.php?ctl=search_ads&keywords=Soba+maribor&price%5Bmin%5D=0&price%5Bmax%5D=250&sort=new"
	filter = ["soba", "sobe", "sobo", "stanovanje"]
	interval = 30

	# Initial ads
	ads = get_all_ads(url, filter=filter)

	print("Number of initial ads: "+str(len(ads)))
	print("New ads since start: \n")
	
	try:
		while True:
			refresh_ads = get_all_ads(url, filter=filter)
			new_ads = get_new_ads(ads, refresh_ads)

			if len(new_ads) > 0:
				ads = refresh_ads
				print_ads(new_ads)

			time.sleep(interval)

	except KeyboardInterrupt:
		print("Exited loop\n\n")
		print("All ads collected: \n")
		print(json.dumps(ads, indent=4, sort_keys=False, default=set_default))
	except Exception as e:
		print("Unknown exception: ")
		print(e)
