import os
import requests
import time

SRC_FILE_ENDINGS= {
        "png",
        "jpg",
        "pdf",
        "gif",
        }

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
}


def get_domain_list():
    with open("input.csv", "r") as f:
        content = f.read().splitlines()
    f.close()
    return content


def execute(home, schema_ref, domain, url_cache = set(), domain_dict=set(), visited=set()):
    
    # if we have already visited this page, return and go next
    if domain in visited:
        return url_cache, domain_dict, visited
    visited.add(domain)

    # make the request - this will be written to write location
    try:
        page = requests.get(schema_ref + domain, headers=HEADERS, allow_redirects=True, timeout=5).content
    except requests.exceptions.ConnectionError:
        print("Connection refused by the server..")
        print("Maybe try adjusting throttle - Skipping this page")
        return url_cache, domain_dict, visited

    # initialise the write location for the url resource
    file_write_path = os.path.join(home.upper(), domain)
    
    full_dir_path = file_write_path.split("/")[:-1] if is_source_file(domain) else file_write_path.split("/")
    full_path = ""
    for dir_path in full_dir_path:
        full_path += dir_path + "/"
        if not os.path.exists(full_path):
            os.makedirs(full_path)

    # if its a traditional content file (see FILE ENDINGS) then write as is, and return
    if is_source_file(domain):
        with open(str(file_write_path), "wb+") as f:
            f.write(page)
        f.close()
        return url_cache, domain_dict, visited

    # otherwise, assume it is an html
    file_write_path = file_write_path.strip("/") + ".html"
    with open(file_write_path, "wb") as f:
        f.write(page)
    f.close()

    with open(file_write_path, "r") as f:
        page = f.readlines()
    f.close()
    
    for line in page:
        while (
                ("href" in line or "src" in line)
            and (
                len(line.split("href")) > 1
                 or len(line.split("src")) > 1
                )
        ):
            if "href" in line:
                try:
                    stuff = line.split('href="')[1].split('"')
                except IndexError:
                    stuff = line.split("href='")[1].split("'")
                link = stuff[0]
                rest = stuff[1:]
                line = "".join(rest)
                if link[0]=="/":
                    link = home + link
                print("\t\t", link)
                if link not in visited:
                    url_cache.add(link)

            elif "src='" in line or 'src="' in line:
                try:
                    stuff = line.split('src="')[1].split('"')
                except IndexError:
                    import pdb; pdb.set_trace()
                    stuff = line.split("src='")[1].split("'")
                link = stuff[0]
                rest = stuff[1:]
                line = "".join(rest)
                if link[0]=="/":
                    link = home + link
                print("\t\t", link)
                url_cache.add(link)
            
            else:
                break

    return url_cache, domain_dict, visited

def reformat(d):
    d = d.strip()
    if d[-1] == ",":
        d = d[:-1]
    return d.split('://')[1]

def fetch_schema_ref(d):
    return d.split('://')[0] + '://'


def is_source_file(d):
    return d.split(".")[-1] in SRC_FILE_ENDINGS

def main():
    # read list of csv inputs - turn into list of home domains
    # loop through domains:
        # create home directory> for home domain - base of internal file structure
        # instantiate structure dictionary
        # for all pages (starting from home), continuing through cache set:
            # scrape all hrefs on homepage into cache set LIMITED have to contain home domain
            # add page to dictionary structure
            # scrape all non html (i.e. resource files) into resources dict

    domain_list = get_domain_list()
    for d in domain_list:
        schema_ref = fetch_schema_ref(d)
        home = reformat(d)
        print(home)
        os.makedirs(home.upper())
        url_cache = {}
        visited = {}
        domain_dict={}
        url_cache, domain_dict, visited = execute(home, schema_ref, home)
        while len(url_cache):
            # time.sleep(1)
            d = url_cache.pop()
            if home in d:
                print(d)
                execute(home, schema_ref, d, url_cache, domain_dict, visited)
 
