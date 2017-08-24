import urllib.request
import http.cookiejar
import re
import os
import execjs
import codecs


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


def str_mid(string: str, left: str, right: str, start=None, end=None):
    pos1 = string.find(left, start, end)
    if pos1 > -1:
        pos2 = string.find(right, pos1 + len(left), end)
        if pos2 > -1:
            return string[pos1 + len(left): pos2]
    return None

os.environ["NODE_PATH"] = os.getcwd() + "/node_modules"
Decrypt_js = execjs.compile(open(os.getcwd() + '/Decrypt.js').read())


def decrypt(_chapter_content, _encryt_keys, _chapter_access_key):
    ret = str(Decrypt_js.call('decrypt', _chapter_content, _encryt_keys, _chapter_access_key))
    ret = ret.replace("<p class='chapter'>", '')
    ret = ret.replace('</p>', '')
    return ret



print("请先登录你的欢乐书客帐号，之后得到一些Cookies并输入程序。")
print("若不登录则直接留空所有Cookies。")

# while True:
#     login_token = input("Cookie: login_token=")
#     if login_token:
#         break
# while True:
#     reader_id = input("Cookie: reader_id=")
#     if reader_id:
#         break
# user_id = input("Cookie: user_id=(为空则与 reader_id 相同)") or reader_id
login_token = ""
reader_id = ""
user_id = ""

cj = http.cookiejar.CookieJar()

cj.set_cookie(make_cookie("login_token", login_token))
cj.set_cookie(make_cookie("reader_id", reader_id))
cj.set_cookie(make_cookie("user_id", user_id))

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def get_content(_chapter_id: str):
    _content = '$$$[章节链接:http://www.hbooker.com/chapter/' + _chapter_id + ']$$$'
    opener.addheaders = headers_chapter_session_code
    post_data = str('chapter_id=' + _chapter_id).encode()
    ajax_get_session_code_str = bytes(opener.open(
        "http://www.hbooker.com/chapter/ajax_get_session_code", post_data
    ).read()).decode('unicode_escape')
    code = str_mid(ajax_get_session_code_str, '"code":', ',')
    chapter_access_key = str_mid(ajax_get_session_code_str, '"chapter_access_key":"', '"')
    if code == "100000":
        opener.addheaders = headers_chapter_detail
        post_data = str('chapter_id=' + _chapter_id +
                        '&chapter_access_key=' + chapter_access_key).encode()
        get_book_chapter_detail_info_str = bytes(opener.open(
            "http://www.hbooker.com/chapter/get_book_chapter_detail_info", post_data
        ).read()).decode('unicode_escape')
        code = str_mid(get_book_chapter_detail_info_str, '"code":', ',')
        if code == "100000":
            encryt_keys = str_mid(get_book_chapter_detail_info_str, '"encryt_keys":[', ']')
            chapter_content = str_mid(get_book_chapter_detail_info_str, '"chapter_content":"', '"')
            encryt_keys = encryt_keys.replace('"', '').replace('\\', '')
            chapter_content = chapter_content.replace('\\', '')
            _content = decrypt(chapter_content, encryt_keys, chapter_access_key)
            _content.replace('\n', '\n\n')
        else:
            tip = str_mid(get_book_chapter_detail_info_str, '"tip":"', '"')
            print("[ERROR]", "code:", code, "tip:", tip)
    else:
        tip = str_mid(ajax_get_session_code_str, '"tip":"', '"')
        print("[ERROR]", "code:", code, "tip:", tip)
    return '\n' + _content + '\n'


opener.addheaders = headers_default
bookshelf_str = ''
if login_token and reader_id and user_id:
    print("正在获取书架信息...")
    bookshelf_str = bytes(opener.open("http://www.hbooker.com/bookshelf/my_book_shelf/").read()).decode()
    nickname = str_mid(bookshelf_str, '<span class="J_Nickname">', '</span>')
else:
    nickname = '${NoName}'
if nickname or nickname == '${NoName}':
    bookshelf = []
    book_index = 0
    if nickname != '${NoName}':
        print("你的昵称: " + nickname)
        print("书架列表:")
        for str_ in re.findall('<div class="tit">[\S\s]+?</div>', bookshelf_str):
            book_index += 1
            book_info = (book_index,
                         str_mid(str_, 'data-book-id="', '"'),
                         str_mid(str_, 'target="_blank">', '</a>'))
            bookshelf.append(book_info)
            print(book_info[0], ": id:", book_info[1], "书名:", book_info[2])
    while True:
        if nickname != '${NoName}':
            while True:
                book_id = input("输入书籍序号或id(输入q退出):")
                if not book_id:
                    continue
                if book_id[0] == 'q':
                    break
                try:
                    if 0 < int(book_id) <= book_index:
                        book_id = bookshelf[int(book_id) - 1][1]
                        break
                except ValueError:
                    pass
        else:
            while True:
                book_id = input("输入书籍id(输入q退出):")
                if book_id:
                    break
        if book_id[0] == 'q':
            break
        print("正在获取书籍信息...")
        opener.addheaders = headers_default
        book_chapter_str = bytes(opener.open("http://www.hbooker.com/book/" + book_id).read()).decode()
        book_title_str = str_mid(book_chapter_str, '<div class="book-title">', '</div>')
        book_title = str_mid(book_title_str, '<h1>', '</h1>')
        book_author = str_mid(book_title_str, 'target="_blank" class="">', '</a>')
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
        print("正在检查文件...")#100012892
        if not os.path.isdir(os.getcwd() + "\\..\\books"):
            os.mkdir(os.getcwd() + "\\..\\books")
        fixed_chapter = list()
        file_data = ''
        cnt_success = 0
        cnt_fail = 0
        if os.path.isfile(os.getcwd() + "\\..\\books\\" + book_title + ".txt"):
            file = codecs.open(os.getcwd() + "\\..\\books\\" + book_title + ".txt", 'r+', 'utf-8')
            file_data = file.read()
            for line in file:
                print(line)
                if line[0:3] == '$$$':
                    chapter_id = str_mid(line, '$$$[章节链接:http://www.hbooker.com/chapter/', ']$$$')
                    print("尝试修复章节:", "chapter_id:", chapter_id)
                    before_str = '\n$$$[章节链接:http://www.hbooker.com/chapter/' + chapter_id + ']$$$\n'
                    content = get_content(chapter_id)
                    fixed_chapter.append((before_str, content))
                    if content.find('$$$') == -1:
                        cnt_success += 1
                    else:
                        cnt_fail += 1
            file.close()
        file = codecs.open(os.getcwd() + "\\..\\books\\" + book_title + ".txt", 'w+', 'utf-8')
        for fix in fixed_chapter:
            file_data.replace(fix[0], fix[1])
        file.write(file_data)
        file.flush()
        del file_data
        if len(fixed_chapter):
            print("章节修复完成，修复成功", cnt_success, "章，修复失败", cnt_fail, "章")
        print("正在获取书籍内容...")
        chapter_start = input("输入开始章节:") or 0
        chapter_end = input("输入结束章节:") or book_chapter_index
        if chapter_start == 0:
            if file_data.rfind('No.') > -1:
                chapter_start = str_mid(file_data, 'No.', ' ', file_data.rfind('No.'))
            else:
                
        print(chapter_start, chapter_end)
        for chapter_index in range(int(chapter_start) - 1, int(chapter_end)):
            chapter_id = book_chapter[chapter_index][1]
            title = book_chapter[chapter_index][2]
            print("当前章节", book_chapter[chapter_index][0], ":",
                  "chapter_id:", chapter_id,
                  "标题:", title)
            content = get_content(chapter_id)
            if content.find('$$$') == -1:
                cnt_success += 1
            else:
                cnt_fail += 1
            chapter_data = '\nNo.' + str(chapter_index + 1) + ': ' + title + '\n' + content
            file.write(chapter_data)
            file.flush()
        file.close()
        print("小说下载已完成，下载成功", cnt_success, "章，下载失败", cnt_fail, "章")
else:
    print("获取书架信息失败")
