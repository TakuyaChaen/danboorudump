#!/usr/bin/env python
#    Copyright (C) 2018  Takuya Chaen
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib.request
import sys
import re
import time

class Danbooru():

    posts_prefix ="posts?&tags="
    page_prefix = "&page="
    post_regex = 'href=\"/posts/(.[0-9]+?)\"'
    postdir = "posts/"
    headers = { "User-Agent" :  "Mozilla/4.0" }
    http = "http://"
    image_regex = 'data-file-url=\"(.+?)\"'
    tag_regex = 'data-tags=\"(.+)\"'
    exclude_list = ["!?","...","/\\/\\/\\"]

    def __init__(self,site,page,tag):
        self.tag = tag
        self.page = page
        self.site = site

    def get_post_url(self):
        return_list = []
        get_url = self.http +  self.site + "/" + self.posts_prefix
        get_url += self.tag + self.page_prefix + str(self.page)
        req = urllib.request.Request(get_url, None, self.headers)
        response = urllib.request.urlopen(req)
        charset = response.headers.get_content_charset()
        if charset==None:
            charset = "utf-8"
        html = response.read().decode('utf-8')
        post_url_list = re.findall(self.post_regex,html)
        post_url_prefix = self.site + "/" + self.postdir
        for posts in post_url_list:
            post_url = self.http +  self.site + "/" + self.postdir + posts
            return_list.append(post_url)
        return return_list

    def get_image_link_and_tag(self,get_url):
        return_url_list = []
        return_tag_list = []
        req = urllib.request.Request(get_url, None, self.headers)
        response = urllib.request.urlopen(req)
        html = response.read().decode('utf-8')
        image_url_list = re.findall(self.image_regex,html)
        for image_url in image_url_list:
            if image_url.find('https') != -1:
                return_url_list.append(image_url)
            else:
                return_url_list.append(self.http +  self.site + image_url)
        tag_list = re.findall(self.tag_regex,html)
        for tag_text in tag_list:
            delete_pos = tag_text.find('"')
            if delete_pos > -1:
                tag_text = tag_text[:delete_pos]
            splited_tag = tag_text.split(' ')
            for add_tag in splited_tag:
                add_ok = True
                for excludes in self.exclude_list:
                    if add_tag == excludes:
                        add_ok = False
                        break
                if add_ok == True:
                    return_tag_list.append(add_tag)
        return_tag_list = list(set(return_tag_list))
        return [return_url_list, return_tag_list]

if __name__ == '__main__':
    args = sys.argv
    if len(args) > 4:
        get_domain = str(args[1])
        get_tag = str(args[2])
        start_num = args[3]
        end_num = args[4]
        start_num = int(start_num)
        end_num = int(end_num)
        for number in range(start_num,end_num):
            time.sleep(1)
            danbooru = Danbooru(get_domain,number,get_tag)
            ret_list = danbooru.get_post_url()
            if len(ret_list) == 0:
                exit()
            for post_url in ret_list:
                image_url_list,tag_lists = danbooru.get_image_link_and_tag(post_url)
                for urls in image_url_list:
                    print(urls)
    else:
        print("usage: python3 danboorudump.py url tag start end ")
        print("   ex: python3 danboorudump.py danbooru.donmai.us 2girl 1 3 ")
        print("   ex: python3 danboorudump.py danbooru.donmai.us 2girl 1 3 > url.txt")
