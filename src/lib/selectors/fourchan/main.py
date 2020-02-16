import json, requests, re, os
import html2text
from urllib.request import urlretrieve
from lib.common.selector import Selector
from lib.common.etypes import Etype


class FourChanSelector(Selector):
    """ A selector that leverages the native 4chan API.

    https://github.com/4chan/4chan-API
    """

    def index(self, config):   
        results = []
        board = config["board"]
        max_posts = config["max_posts"]
        # Create a HTML parser for parsing comments
        h = html2text.HTML2Text()
        h.ignore_links = False
        
        req = f"https://a.4cdn.org/{board}/threads.json"

        content = json.loads(
            requests.get(req).content
        )
        page_count = 0
        for page_index, page in enumerate(content):
            if page_index < max_posts:
                self.logger(f"Scraping page number: {page_index+1}")
                for thread_index, threads in enumerate(page["threads"]):
                    self.logger(f"Extracting posts from thread number: {thread_index+1}")
                    thread_id = threads["no"]
                    req = f"https://a.4cdn.org/{board}/thread/{thread_id}.json"
                    thread_content = json.loads(requests.get(req).content)["posts"] # thread content is a list of posts
                    for post_index, post in enumerate(thread_content):
                        self.logger(f"Extracting media and comments from post number: {post_index+1}")
                        post_row = []
                        post_row.append(post['no'])
                        post_row.append(thread_id)
                        post_row.append(post['time'])
                        
                        try: comment = post['com']
                        except KeyError: comment = "..."
                        else:
                            comment = h.handle(comment)
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
        self.logger('Scraping metadata complete')
        results.insert(0, ["id", "thread_id", "datetime", "comment", "filename", "ext", "url"])
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