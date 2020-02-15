import json, requests, re, os
from html.parser import HTMLParser
from urllib.request import urlretrieve
from lib.common.selector import Selector
from lib.common.etypes import Etype


class fourchan(Selector):
    """ A selector that leverages the native 4chan API.

    https://github.com/4chan/4chan-API
    """

    def index(self, config):   
        results = []
        board = config["board"]
        max_posts = config["max_posts"]
        #TODO: add thread id
        
        req = f"https://a.4cdn.org/{board}/threads.json"

        #-- Various requests --#
        # Boards
        content = json.loads(
            requests.get(req).content
        )
        post_count = 0
        for page in content:
            if post_count < max_posts:
                post_count += 1
                for threads in page["threads"]:
                    thread_id = threads["no"]
                    req = f"https://a.4cdn.org/{board}/thread/{thread_id}.json"
                    thread_content = json.loads(requests.get(req).content)["posts"] # thread content is a list of posts
                    for post in thread_content:
                        post_row = []

                        post_row.append(post['no'])
                        post_row.append(post['time'])
                        
                        # Comment
                        try: comment = re.sub('<[^<]+?>', '', post['com']) # TODO: regex removes _some_ HTML. A better solution is required
                        except KeyError: comment = "..."
                        post_row.append(comment)

                        # Filename
                        try: filename = post['filename']
                        except KeyError: filename = ""

                        if filename != "":
                            time_id = post['tim']
                            extension = post['ext']
                            full_file = f"{filename}{extension}"
                            file_url = f"https://i.4cdn.org/{board}/{time_id}{extension}"
                            post_row.append(full_file)
                            post_row.append(extension)
                            post_row.append(file_url)
                        elif filename == "":
                            post_row.append("")
                            post_row.append("")
                            post_row.append("")
                        
                        results.append(post_row)
        results.insert(0, ["id", "datetime", "comment", "filename", "ext", "url"])
        return results

    def retrieve_element(self, element, config):
        fn = element["filename"]
        identifier = element["id"]
        comment = element["comment"]
        dest = element["base"]
        url = element["url"]
        
        with open(os.path.join(dest, f'{identifier}_comment.txt'), "w+") as f:
            f.write(comment)
        
        if url != "":
            urlretrieve(
                url,
                os.path.join(dest, fn)
            )