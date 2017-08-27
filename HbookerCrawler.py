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
    ret = str(Decrypt_js.call('decrypt', _chapter_content, _encryt_keys, _chapter_access_key))
    ret = ret.replace("<p class='chapter'>", '')
    ret = ret.replace('</p>', '')
    return ret

print("请先登录你的欢乐书客帐号，之后得到一些Cookies并输入程序。")
print("若不登录则直接留空所有Cookies。")

login_token = ""
reader_id = ""
if not os.path.isdir(os.getcwd() + "\\..\\books"):
    os.mkdir(os.getcwd() + "\\..\\books")
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


def get_content(_chapter_id: str):
    _content = '$$$[章节链接:http://www.hbooker.com/chapter/' + _chapter_id + ']$$$'
    try:
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
                _content = decrypt(chapter_content, encryt_keys, chapter_access_key)
                _content = re.sub(r"\r\n|\r|\n", nl * 2, _content)
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
        return nl + _content + nl * 2


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
            for str_ in re.findall('<div class="tit">[\S\s]+?</div>', bookshelf_str):
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
                book_id = input("输入书籍编号或id(输入q退出):")
                if not book_id:
                    continue
                if book_id.lower().startswith('q'):
                    break
                try:
                    if 0 < int(book_id) <= book_index:
                        book_id = bookshelf[int(book_id) - 1][1]
                    break
                except ValueError:
                    continue
        else:
            while True:
                book_id = input("输入书籍id(输入q退出):")
                if book_id:
                    break
        if book_id.lower().startswith('q'):
            break
        try:
            print("正在获取书籍信息...")
            opener.addheaders = headers_default
            book_chapter_str = bytes(opener.open("http://www.hbooker.com/book/" + book_id).read()).decode()
            book_title_str = str_mid(book_chapter_str, '<div class="book-title">', '</div>')
            book_title = str_mid(book_title_str, '<h1>', '</h1>')
            book_author = str_mid(book_title_str, 'target="_blank" class="">', '</a>')
            print("书名:", book_title, "作者:", book_author)
            book_chapter = list()
            book_chapter_index = 0
            for str_ in re.findall('<li><a target="_blank"[\S\s]+?</a>',
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
            fixed_chapter = list()
            file_data = ''
            cnt_success = 0
            cnt_fail = 0
            if not os.path.isdir(os.getcwd() + "\\..\\books"):
                os.mkdir(os.getcwd() + "\\..\\books")
            if os.path.isfile(os.getcwd() + "\\..\\books\\" + book_title + ".txt"):
                file = codecs.open(os.getcwd() + "\\..\\books\\" + book_title + ".txt", 'r', 'utf-8')
                file_data = file.read()
                file.seek(0)
                for line in file.readlines():
                    if line.startswith('$$$'):
                        chapter_id = str_mid(line, '$$$[章节链接:http://www.hbooker.com/chapter/', ']$$$')
                        print("尝试修复章节:", "chapter_id:", chapter_id)
                        before_str = nl + '$$$[章节链接:http://www.hbooker.com/chapter/' + chapter_id + ']$$$' + nl
                        content = get_content(chapter_id)
                        fixed_chapter.append((before_str, content))
                        if content.find('$$$') == -1:
                            cnt_success += 1
                        else:
                            cnt_fail += 1
                file.close()
            file = codecs.open(os.getcwd() + "\\..\\books\\" + book_title + ".txt", 'w', 'utf-8')
            for fix in fixed_chapter:
                file_data.replace(fix[0], fix[1])
            file.write(file_data)
            file.flush()
            if len(fixed_chapter):
                print("章节修复完成，修复成功", cnt_success, "章，修复失败", cnt_fail, "章")
        except Exception as e:
            print("[ERROR]", e)
            print("检查文件时出错")
            continue
        try:
            while True:
                chapter_start = input("输入开始章节编号(留空将自动寻找):") or 0
                chapter_end = input("输入结束章节编号(留空将自动寻找):") or book_chapter_index
                if chapter_start == 0:
                    if file_data.rfind('No.') > -1:
                        try:
                            chapter_start = int(str_mid(file_data, 'No.', '  ', file_data.rfind('No.'))) + 1
                            if int(chapter_start) > int(chapter_end):
                                confirm = 'q'
                                print("书籍暂无更新")
                                break
                        except ValueError:
                            chapter_start = 1
                            print("未能识别最新章节编号，将从章节编号1开始")
                    else:
                        chapter_start = 1
                        print("未能识别最新章节编号，将从章节编号1开始")
                try:
                    if int(chapter_start) <= int(chapter_end):
                        print("开始章节编号:", book_chapter[int(chapter_start) - 1][0],
                              "chapter_id:", book_chapter[int(chapter_start) - 1][1],
                              "标题:", book_chapter[int(chapter_start) - 1][2])
                        print("结束章节编号:", book_chapter[int(chapter_end) - 1][0],
                              "chapter_id:", book_chapter[int(chapter_end) - 1][1],
                              "标题:", book_chapter[int(chapter_end) - 1][2])
                        while True:
                            confirm = input("确定从这个位置下载吗(y/n/q):")
                            if confirm.lower().startswith('y') or confirm.lower().startswith('n') or confirm.lower().startswith('q'):
                                break
                        if confirm.lower().startswith('y') or confirm.lower().startswith('q'):
                            break
                except ValueError:
                    continue
            if confirm.lower().startswith('q'):
                continue
        except Exception as e:
            print("[ERROR]", e)
            print("读取章节编号时出错")
            continue
        try:
            print("正在下载书籍内容...")
            for chapter_index in range(int(chapter_start) - 1, int(chapter_end)):
                chapter_id = book_chapter[chapter_index][1]
                title = book_chapter[chapter_index][2]
                print("章节编号:", book_chapter[chapter_index][0],
                      "chapter_id:", chapter_id,
                      "标题:", title)
                content = get_content(chapter_id)
                if content.find('$$$') == -1:
                    cnt_success += 1
                else:
                    cnt_fail += 1
                chapter_data = nl + 'No.' + str(chapter_index + 1) + '  ' + title + nl + content
                file.write(chapter_data)
                file.flush()
            file.close()
            print("小说下载已完成，下载成功", cnt_success, "章，下载失败", cnt_fail, "章")
        except Exception as e:
            print("[ERROR]", e)
            print("下载书籍时出错")
else:
    print("获取书架信息失败")
