import urllib.request
import http.cookiejar
import re
import myEncrypt

headers_default = [('Accept', 'text/html, application/xhtml+xml, application/xml; q=0.9, image/webp, */*; q=0.8'),
                   ('Accept-Encoding', 'deflate'),
                   ('Accept-Language', 'zh-CN, zh; q=0.8'),
                   ('Connection', 'keep-alive'),
                   ('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'),
                   ('Host', 'www.hbooker.com')]
headers_chapter_session_code = [('Accept', 'application/json, text/javascript, */*; q=0.01'),
                                ('Accept-Encoding', 'deflate'),
                                ('Accept-Language', 'zh-CN, zh; q=0.8'),
                                ('Connection', 'keep-alive'),
                                ('Content-Length', '20'),
                                ('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'),
                                ('Host', 'www.hbooker.com'),
                                ('Origin', 'http://www.hbooker.com'),
                                ('Pragma', 'no-cache'),
                                ('Referer', 'http://www.hbooker.com/chapter/book_chapter_detail/100287294/music'),
                                ('X-Requested-With', 'XMLHttpRequest')]
headers_chapter_detail = [('Accept', 'application/json, text/javascript, */*; q=0.01'),
                          ('Accept-Encoding', 'deflate'),
                          ('Accept-Language', 'zh-CN, zh; q=0.8'),
                          ('Connection', 'keep-alive'),
                          ('Content-Length', '48'),
                          ('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'),
                          ('Host', 'www.hbooker.com'),
                          ('Origin', 'http://www.hbooker.com'),
                          ('Pragma', 'no-cache'),
                          ('Referer', 'http://www.hbooker.com/chapter/book_chapter_detail/100287294/music'),
                          ('X-Requested-With', 'XMLHttpRequest')]


def make_cookie(name, value):
    return http.cookiejar.Cookie(
        version=0, name=name, value=value, port=None, port_specified=False, domain="hbooker.com", domain_specified=True,
        domain_initial_dot=False, path="/", path_specified=True, secure=False, expires=None, discard=False,
        comment=None, comment_url=None, rest=None
    )


def str_mid(string, left, right, start=None, end=None):
    pos1 = string.find(left, start, end)
    if pos1 > -1:
        pos2 = string.find(right, pos1 + len(left), end)
        if pos2 > -1:
            return string[pos1 + len(left): pos2]
    return None


file_data = str(open('chapter_detail.json').read())
chapter_content = str_mid(file_data, '"chapter_content":"', '"')
encryt_keys = str_mid(file_data, '"encryt_keys":', ',')
chapter_access_key = str_mid(file_data, '"chapter_access_key":"', '"')


print("请先登录你的欢乐书客帐号，之后得到一些Cookie并输入程序。")

# while True:
#     ci_session = input("Cookie: ci_session=")
#     if ci_session:
#         break
# while True:
#     login_token = input("Cookie: login_token=")
#     if login_token:
#         break
# while True:
#     reader_id = input("Cookie: reader_id=")
#     if reader_id:
#         break
# user_id = input("Cookie: user_id=(为空则与 reader_id 相同)") or reader_id
login_token = "0b0d5d817af765d3515ac1912a0921e9"
reader_id = "1587745"
user_id = "1587745"

cj = http.cookiejar.CookieJar()

# cj.set_cookie(make_cookie("ci_session", ci_session))
cj.set_cookie(make_cookie("login_token", login_token))
cj.set_cookie(make_cookie("reader_id", reader_id))
cj.set_cookie(make_cookie("user_id", user_id))
# cj.set_cookie(make_cookie("get_task_type_sign", "1"))
# cj.set_cookie(make_cookie("qdgd", "1"))

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

opener.addheaders = headers_default
print("正在获取书架信息...")
bookshelf_str = bytes(opener.open("http://www.hbooker.com/bookshelf/my_book_shelf/").read()).decode()
nickname = str_mid(bookshelf_str, '<span class="J_Nickname">', '</span>')
if nickname:
    print("你的昵称: " + nickname)
    print("书架列表:")
    bookshelf = []
    book_index = 0
    for str_ in re.findall('<div class="tit">[\S\s]+?</div>', bookshelf_str):
        book_index += 1
        book_info = (book_index,
                     str_mid(str_, 'data-book-id="', '"'),
                     str_mid(str_, 'target="_blank">', '</a>'))
        bookshelf.append(book_info)
        print(book_info[0], ": id:", book_info[1], "书名:", book_info[2])
    while True:
        while True:
            book_id = input("输入书籍序号或id:")
            if book_id:
                break
        if 0 < int(book_id) <= book_index:
            book_id = bookshelf[int(book_id) - 1][1]
        # 获取书籍信息
        print("正在获取书籍信息...")
        opener.addheaders = headers_default
        book_chapter_str = bytes(opener.open("http://www.hbooker.com/book/" + book_id).read()).decode()
        book_chapter = []
        book_chapter_index = 0
        for str_ in re.findall('<li><a target="_blank"[\S\s]+?</a>',
                               book_chapter_str):
            book_chapter_index += 1
            book_chapter_info = (book_chapter_index,
                                 str_mid(str_, 'href="http://www.hbooker.com/chapter/book_chapter_detail/', '"'),
                                 str_mid(str_, '</i>', '</a>'))
            book_chapter.append(book_chapter_info)
        print("共", book_chapter_index, "章", "最新章节:", str_mid(book_chapter_str, '<div class="tit">', '</div>'))
        while True:
            chapter_start = input("输入开始章节:")
            if chapter_start and int(chapter_start) > 0:
                break
        while True:
            chapter_end = input("输入结束章节:")
            if chapter_end and int(chapter_end) >= int(chapter_start):
                break
        print("正在获取书籍内容...")
        opener.addheaders = headers_chapter_session_code
        cnt_success = 0
        cnt_fail = 0
        for chapter_index in range(int(chapter_start) - 1, int(chapter_end)):
            print("当前章节", book_chapter[chapter_index][0] + 1, ":",
                  "chapter_id:", book_chapter[chapter_index][1],
                  "标题:", book_chapter[chapter_index][2])
            postData = str('chapter_id=' + book_chapter[chapter_index][1]).encode()
            ajax_get_session_code_str = bytes(opener.open(
                "http://www.hbooker.com/chapter/ajax_get_session_code", postData
            ).read()).decode('unicode_escape')
            code = str_mid(ajax_get_session_code_str, '"code":', ',')
            chapter_access_key = str_mid(ajax_get_session_code_str, '"chapter_access_key":"', '"')
            if code == "100000":
                opener.addheaders = headers_chapter_detail
                postData = str('chapter_id=' + book_chapter[chapter_index][1] +
                               '&chapter_access_key=' + chapter_access_key).encode()
                get_book_chapter_detail_info_str = bytes(opener.open(
                    "http://www.hbooker.com/chapter/get_book_chapter_detail_info", postData
                ).read()).decode('unicode_escape')
                code = str_mid(get_book_chapter_detail_info_str, '"code":', ',')
                if code == "100000":
                    print(get_book_chapter_detail_info_str)
                    rad = str_mid(get_book_chapter_detail_info_str, '"rad":', ',')
                    rad = book_chapter[chapter_index][1] + "100000" + rad
                    encryt_keys = str_mid(get_book_chapter_detail_info_str, '"encryt_keys":', ',')
                    chapter_content = str_mid(get_book_chapter_detail_info_str, '"chapter_content":"', '"')
                    # myEncrypt

                    cnt_success += 1
                else:
                    tip = str_mid(get_book_chapter_detail_info_str, '"tip":"', '"')
                    print("[INFO]", "code:", code, "tip:", tip)
                    cnt_fail += 1
            else:
                tip = str_mid(ajax_get_session_code_str, '"tip":"', '"')
                print("[INFO]", "code:", code, "tip:", tip)
                cnt_fail += 1
        print("小说下载已完成，下载成功", cnt_success, "章，下载失败", cnt_fail, "章")
else:
    print("获取书架信息失败")
