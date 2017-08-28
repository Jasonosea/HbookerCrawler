import urllib.request
import http.cookiejar
import re
import os
import execjs
import codecs

print("当前JavaScript环境:", execjs.get().name)
if str(execjs.get().name).lower().find('node.js') == -1:
    while True:
        run = str(input("检测到当前JavaScript环境不是Node.js，是否继续运行？(y/n)")).lower()
        if run.startswith('y'):
            break
        elif run.startswith('n'):
            exit()

headers_default = [('Accept', 'text/html, application/xhtml+xml, application/xml; q=0.9, image/webp, */*; q=0.8'),
                   ('Accept-Encoding', 'deflate'),
                   ('Accept-Language', 'zh-CN, zh; q=0.8'),
                   ('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'),
                   ('Host', 'www.hbooker.com')]
headers_chapter_session_code = [('Accept', 'application/json, text/javascript, */*; q=0.01'),
                                ('Accept-Encoding', 'deflate'),
                                ('Accept-Language', 'zh-CN, zh; q=0.8'),
                                ('Content-Length', '20'),
                                ('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'),
                                ('Host', 'www.hbooker.com'),
                                ('Origin', 'http://www.hbooker.com'),
                                ('Referer', 'http://www.hbooker.com/chapter/book_chapter_detail'),
                                ('X-Requested-With', 'XMLHttpRequest')]
headers_chapter_detail = [('Accept', 'application/json, text/javascript, */*; q=0.01'),
                          ('Accept-Encoding', 'deflate'),
                          ('Accept-Language', 'zh-CN, zh; q=0.8'),
                          ('Content-Length', '48'),
                          ('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'),
                          ('Host', 'www.hbooker.com'),
                          ('Origin', 'http://www.hbooker.com'),
                          ('Referer', 'http://www.hbooker.com/chapter/book_chapter_detail'),
                          ('X-Requested-With', 'XMLHttpRequest')]
nl = '\r\n'


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
    return ''

os.environ["NODE_PATH"] = os.getcwd() + "/node_modules"
Decrypt_js = execjs.compile(open(os.getcwd() + '/Decrypt.js').read())


def decrypt(_chapter_content: str, _encryt_keys: str, _chapter_access_key: str):
    _encryt_keys = _encryt_keys.replace('"', '').replace('\\', '')
    _chapter_content = _chapter_content.replace('\\', '')
    return str(Decrypt_js.call('decrypt', _chapter_content, _encryt_keys, _chapter_access_key))

print("下载的书籍文件在/../books目录下。")
print("书籍文件有html和txt格式，使用html格式可加载图片，但确保images文件夹存在。")
print("请先登录你的欢乐书客帐号，之后得到一些Cookies并输入程序。")
print("若不登录则直接留空所有Cookies。")

login_token = ""
reader_id = ""
if not os.path.isdir(os.getcwd() + "\\..\\books"):
    os.makedirs(os.getcwd() + "\\..\\books")
if os.path.isfile(os.getcwd() + "\\..\\books\\hbookercrawler.cfg"):
    cfg_file = codecs.open(os.getcwd() + "\\..\\books\\hbookercrawler.cfg", 'r', 'utf-8')
    for line in cfg_file.readlines():
        if line.startswith("login_token="):
            login_token = str_mid(line, 'login_token="', '"')
        elif line.startswith("reader_id="):
            reader_id = str_mid(line, 'reader_id="', '"')
    cfg_file.close()

login_token = input('Cookie: login_token(默认为"' + login_token + '")=') or login_token
reader_id = input('Cookie: reader_id(默认为"' + reader_id + '")=') or reader_id

cfg_file = codecs.open(os.getcwd() + "\\..\\books\\hbookercrawler.cfg", 'w', 'utf-8')
cfg_file.write('login_token="' + login_token + '"' + nl)
cfg_file.write('reader_id="' + reader_id + '"' + nl)
cfg_file.close()
del cfg_file

cj = http.cookiejar.CookieJar()

cj.set_cookie(make_cookie("login_token", login_token))
cj.set_cookie(make_cookie("reader_id", reader_id))
cj.set_cookie(make_cookie("user_id", reader_id))

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener_chapter_session_code = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener_chapter_detail = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

opener.addheaders = headers_default
opener_chapter_session_code.addheaders = headers_chapter_session_code
opener_chapter_detail.addheaders = headers_chapter_detail


def get_content(_chapter_id: str):
    _content = '<a href="http://www.hbooker.com/chapter/' + _chapter_id + '">章节链接</a>'
    try:
        post_data = str('chapter_id=' + _chapter_id).encode()
        ajax_get_session_code_str = bytes(opener_chapter_session_code.open(
            "http://www.hbooker.com/chapter/ajax_get_session_code", post_data
        ).read()).decode('unicode_escape')
        code = str_mid(ajax_get_session_code_str, '"code":', ',')
        chapter_access_key = str_mid(ajax_get_session_code_str, '"chapter_access_key":"', '"')
        if code == "100000":
            post_data = str('chapter_id=' + _chapter_id +
                            '&chapter_access_key=' + chapter_access_key).encode()
            get_book_chapter_detail_info_str = bytes(opener_chapter_detail.open(
                "http://www.hbooker.com/chapter/get_book_chapter_detail_info", post_data
            ).read()).decode('unicode_escape')
            code = str_mid(get_book_chapter_detail_info_str, '"code":', ',')
            if code == "100000":
                encryt_keys = str_mid(get_book_chapter_detail_info_str, '"encryt_keys":[', ']')
                chapter_content = str_mid(get_book_chapter_detail_info_str, '"chapter_content":"', '"')
                _content = decrypt(chapter_content, encryt_keys, chapter_access_key)
                _content = re.sub("<p.+?>", '<p>', _content)
            else:
                tip = str_mid(get_book_chapter_detail_info_str, '"tip":"', '"')
                print("[INFO]", "code:", code, "tip:", tip)
        else:
            tip = str_mid(ajax_get_session_code_str, '"tip":"', '"')
            print("[INFO]", "code:", code, "tip:", tip)
    except Exception as _e:
        print("[ERROR]", _e)
        print("获取章节内容时出错")
    finally:
        return _content


def download_image(_content: str, _book_dir: str):
    if not os.path.isdir(_book_dir + '\\images'):
        os.makedirs(_book_dir + '\\images')
    for img in re.findall(r'<img src=.*?>', _content):
        try:
            src = str_mid(img, '<img src="', '"')
            if src.rfind('/') == -1:
                continue
            filename = src[src.rfind('/') + 1:]
            urllib.request.urlretrieve(src, _book_dir + '\\images\\' + filename)
            _content = _content.replace(src, 'images/' + filename)
        except Exception as _e:
            print("[ERROR]", _e)
            print("下载图片时出错")
    return _content


def html2txt(_data: str):
    for _a in re.findall(r'<a href=.*?>章节链接</a>', _data):
        _data = _data.replace(_a, '章节链接:' + str_mid(_a, '<a href="', '"'))
    for _img in re.findall(r'<img src=.*?>', _data):
        _data = _data.replace(_img, '图片:"' + str_mid(_img, "alt='", "'") + '",' +
                                    '图片位置:' + str_mid(_img, '<img src="', '"'))
    _data = re.sub(r'<head>[\s\S]*?</head>', '', _data)
    _data = re.sub(r'</?(html|head|body|title|div|h|p).*?>', '', _data)
    _data = re.sub(r'[\r\n]+', nl * 2, _data)
    _data = _data.replace('<br>', '')
    return _data

bookshelf_str = ''
if login_token and reader_id:
    try:
        print("正在获取书架信息...")
        bookshelf_str = bytes(opener.open("http://www.hbooker.com/bookshelf/my_book_shelf/").read()).decode()
        nickname = str_mid(bookshelf_str, '<span class="J_Nickname">', '</span>')
    except Exception as e:
        print("[ERROR]", e)
        print("获取书架信息时出错，取消登录")
        nickname = '${NoName}'
else:
    nickname = '${NoName}'
if nickname:
    bookshelf = list()
    book_index = 0
    if nickname != '${NoName}':
        try:
            print("你的昵称: " + nickname)
            print("书架列表:")
            for str_ in re.findall('<div class="tit">.*?</div>', bookshelf_str):
                book_index += 1
                book_info = (book_index,
                             str_mid(str_, 'data-book-id="', '"'),
                             str_mid(str_, 'target="_blank">', '</a>'))
                bookshelf.append(book_info)
        except Exception as e:
            print("[ERROR]", e)
            print("获取书架信息时出错，取消登录")
            nickname = '${NoName}'
    while True:
        if nickname != '${NoName}':
            for book_info in bookshelf:
                print("编号:", book_info[0], "id:", book_info[1], "书名:", book_info[2])
            while True:
                book_id = input("输入书籍编号或id(输入q退出):").lower()
                if not book_id:
                    continue
                if book_id.startswith('q'):
                    break
                try:
                    if 0 < int(book_id) <= book_index:
                        book_id = bookshelf[int(book_id) - 1][1]
                    break
                except ValueError:
                    continue
        else:
            while True:
                book_id = input("输入书籍id(输入q退出):").lower()
                if book_id:
                    break
        if book_id.startswith('q'):
            break
        try:
            print("正在获取书籍信息...")
            book_chapter_str = bytes(opener.open("http://www.hbooker.com/book/" + book_id).read()).decode()
            book_title_str = str_mid(book_chapter_str, '<div class="book-title">', '</div>')
            book_title = str_mid(book_title_str, '<h1>', '</h1>')
            book_author = str_mid(book_title_str, 'target="_blank" class="">', '</a>')
            print("书名:", book_title, "作者:", book_author)
            book_chapter = list()
            book_chapter_index = 0
            for str_ in re.findall('<li><a target="_blank".*?</a>',
                                   book_chapter_str):
                book_chapter_index += 1
                book_chapter_info = (book_chapter_index,
                                     str_mid(str_, 'href="http://www.hbooker.com/chapter/book_chapter_detail/', '"'),
                                     str_mid(str_, '</i>', '</a>').replace("<i class='icon-vip'></i>", ""))
                book_chapter.append(book_chapter_info)
            print("共", book_chapter_index, "章", "最新章节:", str_mid(book_chapter_str, '<div class="tit">', '</div>'))
        except Exception as e:
            print("[ERROR]", e)
            print("获取书籍信息时出错")
            continue
        try:
            print("正在检查文件...")
            file_lines = list()
            file_data = ''
            cnt_success = 0
            cnt_fail = 0
            file = None
            book_dir = os.getcwd() + "\\..\\books\\" + book_title
            html_head = '<html>' + nl + '<head><title>' + book_title + '</title></head>' + nl + '<body>' + nl
            html_end = '</body>' + nl + '</html>' + nl
            if not os.path.isdir(book_dir):
                os.makedirs(book_dir)
            if os.path.isfile(book_dir + "\\" + book_title + ".html"):
                file = codecs.open(book_dir + "\\" + book_title + ".html", 'r', 'utf-8')
                file_lines = file.readlines()
                file.close()
                file = codecs.open(book_dir + "\\" + book_title + ".html", 'w', 'utf-8')
                for i in range(len(file_lines)):
                    if file_lines[i].startswith('<a href='):
                        chapter_id = str_mid(file_lines[i], '<a href="http://www.hbooker.com/chapter/', '">章节链接</a>')
                        print("尝试修复章节:", "chapter_id:", chapter_id, end="  ----  ")
                        file_lines[i] = download_image(get_content(chapter_id), book_dir) + nl
                        file.seek(0)
                        file.writelines(file_lines)
                        file.flush()
                        if file_lines[i].startswith('<a href='):
                            cnt_fail += 1
                            print("修复失败")
                        else:
                            cnt_success += 1
                            print("修复成功")
                    file_data += file_lines[i]
                if cnt_success or cnt_fail:
                    print("章节修复完成，修复成功", cnt_success, "章，修复失败", cnt_fail, "章")
            else:
                file = codecs.open(book_dir + "\\" + book_title + ".html", 'w', 'utf-8')
        except Exception as e:
            print("[ERROR]", e)
            print("检查文件时出错")
            continue
        try:
            while True:
                while True:
                    try:
                        chapter_start = int(input("输入开始章节编号(留空将自动寻找):") or 0)
                        chapter_end = int(input("输入结束章节编号(留空将自动寻找):") or book_chapter_index)
                        break
                    except ValueError:
                        continue
                if chapter_start == 0:
                    for line in file_lines:
                        if line.startswith('<div id='):
                            try:
                                if chapter_start < int(str_mid(line, '<div id="', '"')) + 1:
                                    chapter_start = int(str_mid(line, '<div id="', '"')) + 1
                            except ValueError:
                                continue
                    if chapter_start > chapter_end:
                        confirm = 'q'
                        input("书籍暂无更新")
                        break
                if chapter_start == 0:
                    chapter_start = 1
                    print("未能识别最新章节编号，将从章节编号1开始")
                if chapter_start <= chapter_end:
                    print("开始章节编号:", book_chapter[chapter_start - 1][0],
                          "chapter_id:", book_chapter[chapter_start - 1][1],
                          "标题:", book_chapter[chapter_start - 1][2])
                    print("结束章节编号:", book_chapter[chapter_end - 1][0],
                          "chapter_id:", book_chapter[chapter_end - 1][1],
                          "标题:", book_chapter[chapter_end - 1][2])
                    while True:
                        confirm = input("确定从这个位置下载吗(y/n/q):").lower()
                        if confirm.startswith('y') or confirm.startswith('n') or confirm.startswith('q'):
                            break
                    if confirm.startswith('y') or confirm.startswith('q'):
                        break
            if confirm.startswith('q'):
                continue
        except Exception as e:
            print("[ERROR]", e)
            print("读取章节编号时出错")
            continue
        try:
            print("正在下载书籍内容...")
            file_data = file_data.replace(html_end, '')
            file.seek(0)
            file.write(file_data)
            file.flush()
            cnt_success = 0
            cnt_fail = 0
            for chapter_index in range(chapter_start - 1, chapter_end):
                chapter_id = book_chapter[chapter_index][1]
                title = book_chapter[chapter_index][2]
                print("章节编号:", book_chapter[chapter_index][0],
                      "chapter_id:", chapter_id,
                      "标题:", title, end="  ----  ")
                content = download_image(get_content(chapter_id), book_dir)
                chapter_data = '<div id="' + str(chapter_index + 1) + '">' + nl + \
                               '<h3>' + title + '</h3>' + nl + \
                               content + nl + '<br><br>' + nl + \
                               '</div>' + nl
                file_data += chapter_data
                file.write(chapter_data)
                file.flush()
                if content.startswith('<a href='):
                    cnt_fail += 1
                    print("下载失败")
                else:
                    cnt_success += 1
                    print("下载成功")
            file_data += html_end
            file.write(html_end)
            file.close()
            file_txt = codecs.open(book_dir + "\\" + book_title + ".txt", 'w', 'utf-8')
            file_txt.seek(0)
            file_txt.write(html2txt(file_data))
            file_txt.close()
            print("下载书籍已完成，下载成功", cnt_success, "章，下载失败", cnt_fail, "章")
            input("按下回车键继续...")
        except Exception as e:
            print("[ERROR]", e)
            print("下载书籍时出错")
else:
    print("获取书架信息失败")
