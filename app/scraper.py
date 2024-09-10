import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
from random import uniform

# Delay between requests to throttle scraping
MIN_DELAY = 1.0  # Minimum delay in seconds
MAX_DELAY = 3.0  # Maximum delay in seconds

async def fetch_page(url: str) -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            return ""
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
            return ""

def parse_product_data_amazon(html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, 'html.parser')
    products = []
    try:
        for product in soup.select('.s-main-slot .s-result-item'):
            name = product.select_one('h2 .a-text-normal').text.strip()
            image = product.select_one('img.s-image')['src']
            price = product.select_one('.a-price-whole')
            price = price.text.strip() if price else "N/A"
            link = 'https://www.amazon.com' + product.select_one('a.a-link-normal')['href']
            rating = product.select_one('.a-icon-alt')
            rating = rating.text.strip() if rating else "N/A"
            
            products.append({
                'name': name,
                'image': image,
                'price': price,
                'link': link,
                'rating': rating
            })
    except Exception as e:
        print(f"Error parsing Amazon data: {e}")
    return products

def parse_product_data_ebay(html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, 'html.parser')
    products = []
    try:
        for product in soup.select('.s-item'):
            name = product.select_one('.s-item__title').text.strip()
            image = product.select_one('.s-item__image-img')['src']
            price = product.select_one('.s-item__price').text.strip()
            link = product.select_one('.s-item__link')['href']
            rating = product.select_one('.b-starrating')
            rating = rating.text.strip() if rating else "N/A"
            
            products.append({
                'name': name,
                'image': image,
                'price': price,
                'link': link,
                'rating': rating
            })
    except Exception as e:
        print(f"Error parsing eBay data: {e}")
    return products

def parse_product_data_aliexpress(html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, 'html.parser')
    products = []
    try:
        for product in soup.select('.item'):
            name = product.select_one('.item-title').text.strip()
            image = product.select_one('.item-img')['src']
            price = product.select_one('.price').text.strip()
            link = product.select_one('a')['href']
            rating = product.select_one('.rating')
            rating = rating.text.strip() if rating else "N/A"
            
            products.append({
                'name': name,
                'image': image,
                'price': price,
                'link': link,
                'rating': rating
            })
    except Exception as e:
        print(f"Error parsing AliExpress data: {e}")
    return products

def parse_product_data_jumia(html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, 'html.parser')
    products = []
    try:
        for product in soup.select('.prd'):
            name = product.select_one('.name').text.strip()
            image = product.select_one('img')['data-src']
            price = product.select_one('.price').text.strip()
            link = product.select_one('a')['href']
            rating = product.select_one('.rating')
            rating = rating.text.strip() if rating else "N/A"
            
            products.append({
                'name': name,
                'image': image,
                'price': price,
                'link': link,
                'rating': rating
            })
    except Exception as e:
        print(f"Error parsing Jumia data: {e}")
    return products

def parse_product_data_konga(html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, 'html.parser')
    products = []
    try:
        for product in soup.select('.product-item'):
            name = product.select_one('.product-title').text.strip()
            image = product.select_one('img')['src']
            price = product.select_one('.product-price').text.strip()
            link = product.select_one('a')['href']
            rating = product.select_one('.rating')
            rating = rating.text.strip() if rating else "N/A"
            
            products.append({
                'name': name,
                'image': image,
                'price': price,
                'link': link,
                'rating': rating
            })
    except Exception as e:
        print(f"Error parsing Konga data: {e}")
    return products

async def scrape_amazon(url: str) -> List[Dict[str, str]]:
    html = await fetch_page(url)
    if html:
        return parse_product_data_amazon(html)
    return []

async def scrape_ebay(url: str) -> List[Dict[str, str]]:
    html = await fetch_page(url)
    if html:
        return parse_product_data_ebay(html)
    return []

async def scrape_aliexpress(url: str) -> List[Dict[str, str]]:
    html = await fetch_page(url)
    if html:
        return parse_product_data_aliexpress(html)
    return []

async def scrape_jumia(url: str) -> List[Dict[str, str]]:
    html = await fetch_page(url)
    if html:
        return parse_product_data_jumia(html)
    return []

async def scrape_konga(url: str) -> List[Dict[str, str]]:
    html = await fetch_page(url)
    if html:
        return parse_product_data_konga(html)
    return []

async def scrape_all(product_name: str) -> List[Dict[str, str]]:
    amazon_url = f"https://www.amazon.com/s?k={product_name}"
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={product_name}"
    aliexpress_url = f"https://www.aliexpress.com/wholesale?SearchText={product_name}"
    jumia_url = f"https://www.jumia.com.ng/catalog/?q={product_name}"
    konga_url = f"https://www.konga.com/search?search={product_name}"

    tasks = [
        scrape_amazon(amazon_url),
        scrape_ebay(ebay_url),
        scrape_aliexpress(aliexpress_url),
        scrape_jumia(jumia_url),
        scrape_konga(konga_url)
    ]

    results = await asyncio.gather(*tasks)

    # Introduce a delay between requests
    await asyncio.sleep(uniform(MIN_DELAY, MAX_DELAY))

    all_products = []
    for result in results:
        all_products.extend(result)

    return all_products
