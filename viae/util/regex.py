import re

# regex
def remove_prefix(img_url):
    return re.sub(r'.*\/([^\/]+)',r"\1", img_url)

def to_json(file_name):
    return re.sub(r'(\.[^.]*)$', '.json', file_name)
    