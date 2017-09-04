import urllib.request
import http.cookiejar
import re
import os
import codecs
import execjs
import Epub

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
headers_chapter = [('Accept', 'application/json, text/javascript, */*; q=0.01'),
                   ('Accept-Encoding', 'deflate'),
                   ('Accept-Language', 'zh-CN, zh; q=0.8'),
                   ('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'),
                   ('Host', 'www.hbooker.com'),
                   ('Origin', 'http://www.hbooker.com'),
                   ('Referer', 'http://www.hbooker.com/chapter/book_chapter_detail'),
                   ('X-Requested-With', 'XMLHttpRequest')]
headers_book_chapter_image = [('Accept', 'image/webp,image/*,*/*;q=0.8'),
                              ('Accept-Encoding', 'deflate'),
                              ('Accept-Language', 'zh-CN, zh; q=0.8'),
                              ('Host', 'www.hbooker.com'),
                              ('Referer', 'http://www.hbooker.com/chapter/book_chapter_detail')]
nl = '\r\n'
doc_help = "下载的书籍文件及配置文件在 ../books 目录下。" + nl + \
           "支持导出文件格式: txt,epub" + nl + \
           "图片章节可通过修改配置文件中的area_width,font,font_size,bg_color_name,text_color_name实现不同文字效果" + nl + \
           "area_width:图片宽度; 默认:816" + nl + \
           "font:字体; 默认:undefined" + nl + \
           "font_size:字体大小; 默认:14" + nl + \
           "bg_color_name:背景颜色; 默认:default; 可用设置:default,green,blue,white,gray,pink,night;" + nl + \
           "text_color_name:文字颜色; 默认:default; 可用设置:default,green,blue,white,gray,pink,night;"


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


def decrypt(_str: str, _encryt_keys: str, _access_key: str):
    return str(Decrypt_js.call('decrypt', _str, _encryt_keys, _access_key))

print("请先登录你的欢乐书客帐号，之后得到一些Cookies并输入程序。")
print("若不登录则直接留空所有Cookies。")

login_token = ""
reader_id = ""
area_width = "816"
font = "undefined"
font_size = "14"
bg_color_name = "default"
text_color_name = "default"
if not os.path.isdir(os.getcwd() + "/../books"):
    os.makedirs(os.getcwd() + "/../books")
if os.path.isfile(os.getcwd() + "/../books/hbookercrawler.cfg"):
    cfg_file = codecs.open(os.getcwd() + "/../books/hbookercrawler.cfg", 'r', 'utf-8')
    for line in cfg_file.readlines():
        if line.startswith("login_token="):
            login_token = str_mid(line, 'login_token="', '"')
        elif line.startswith("reader_id="):
            reader_id = str_mid(line, 'reader_id="', '"')
        elif line.startswith("area_width="):
            area_width = str_mid(line, 'area_width="', '"')
        elif line.startswith("font="):
            font = str_mid(line, 'font="', '"')
        elif line.startswith("font_size="):
            font_size = str_mid(line, 'font_size="', '"')
        elif line.startswith("bg_color_name="):
            bg_color_name = str_mid(line, 'bg_color_name="', '"')
        elif line.startswith("text_color_name="):
            text_color_name = str_mid(line, 'text_color_name="', '"')
    cfg_file.close()

login_token = input('Cookie: login_token(默认:"' + login_token + '")=') or login_token
reader_id = input('Cookie: reader_id(默认:"' + reader_id + '")=') or reader_id

with codecs.open(os.getcwd() + "/../books/hbookercrawler.cfg", 'w', 'utf-8') as cfg_file:
    cfg_file.write('login_token="' + login_token + '"' + nl)
    cfg_file.write('reader_id="' + reader_id + '"' + nl)
    cfg_file.write('area_width="' + area_width + '"' + nl)
    cfg_file.write('font="' + font + '"' + nl)
    cfg_file.write('font_size="' + font_size + '"' + nl)
    cfg_file.write('bg_color_name="' + bg_color_name + '"' + nl)
    cfg_file.write('text_color_name="' + text_color_name + '"')
del cfg_file

cj = http.cookiejar.CookieJar()

cj.set_cookie(make_cookie("login_token", login_token))
cj.set_cookie(make_cookie("reader_id", reader_id))
cj.set_cookie(make_cookie("user_id", reader_id))

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener_chapter = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener_book_chapter_image = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

opener.addheaders = headers_default
opener_chapter.addheaders = headers_chapter
opener_book_chapter_image.addheaders = headers_book_chapter_image


def get_content(_chapter_id: str):
    _content = '<a href="http://www.hbooker.com/chapter/' + _chapter_id + '">章节链接</a>'
    try:
        _post_data = str('chapter_id=' + _chapter_id).encode()
        ajax_get_session_code_str = bytes(opener_chapter.open(
            "http://www.hbooker.com/chapter/ajax_get_session_code", _post_data
        ).read()).decode('unicode_escape')
        _code = str_mid(ajax_get_session_code_str, '"code":', ',')
        _chapter_access_key = str_mid(ajax_get_session_code_str, '"chapter_access_key":"', '"')
        if _code == "100000":
            _post_data = str('chapter_id=' + _chapter_id +
                             '&chapter_access_key=' + _chapter_access_key).encode()
            get_book_chapter_detail_info_str = bytes(opener_chapter.open(
                "http://www.hbooker.com/chapter/get_book_chapter_detail_info", _post_data
            ).read()).decode('unicode_escape')
            _code = str_mid(get_book_chapter_detail_info_str, '"code":', ',')
            if _code == "100000":
                _encryt_keys = str_mid(get_book_chapter_detail_info_str, '"encryt_keys":[', ']')
                _chapter_content = str_mid(get_book_chapter_detail_info_str, '"chapter_content":"', '"')
                _content = decrypt(_chapter_content, _encryt_keys, _chapter_access_key)
                _content = _content.replace("<p class='chapter'>", '<p>')
            elif _code == "400002":
                try:
                    ajax_get_image_session_code_str = bytes(opener_chapter.open(
                        "http://www.hbooker.com/chapter/ajax_get_image_session_code", b'\n'
                    ).read()).decode('unicode_escape')
                    _code = str_mid(ajax_get_image_session_code_str, '"code":', ',')
                    if _code == "100000":
                        _encryt_keys = str_mid(ajax_get_image_session_code_str, '"encryt_keys":[', ']')
                        _access_key = str_mid(ajax_get_image_session_code_str, '"access_key":"', '"')
                        _image_code = str_mid(ajax_get_image_session_code_str, '"image_code":"', '"')
                        _image_code = decrypt(_image_code, _encryt_keys, _access_key)
                        opener_chapter.open("http://www.hbooker.com/chapter/get_book_chapter_image_height"
                                            "?chapter_id=" + _chapter_id +
                                            "&area_width=" + area_width +
                                            "&font=" + font +
                                            "&font_size=" + font_size +
                                            "&image_code=" + _image_code +
                                            "&bg_color_name=" + bg_color_name +
                                            "&text_color_name=" + text_color_name, b'\n')
                        _content = opener_book_chapter_image.open(
                            "http://www.hbooker.com/chapter/book_chapter_image"
                            "?chapter_id=" + _chapter_id +
                            "&area_width=" + area_width +
                            "&font=" + font +
                            "&font_size=" + font_size +
                            "&image_code=" + _image_code +
                            "&bg_color_name=" + bg_color_name +
                            "&text_color_name=" + text_color_name
                        ).read()
                except Exception as _e:
                    print("[ERROR]", _e)
                    print("下载图片章节时出错")
            else:
                print("[INFO]", "code:", _code, "tip:", str_mid(get_book_chapter_detail_info_str, '"tip":"', '"'))
        else:
            print("[INFO]", "code:", _code, "tip:", str_mid(ajax_get_session_code_str, '"tip":"', '"'))
    except Exception as _e:
        print("[ERROR]", _e)
        print("获取章节内容时出错")
    finally:
        return _content


def get_images(_content: str):
    _images = list()
    for img in re.findall(r'<img src="http.*?>', _content):
        try:
            src = str_mid(img, '<img src="', '"')
            if src.rfind('/') == -1:
                continue
            filename = src[src.rfind('/') + 1:]
            _images.append((filename, src))
        except Exception as _e:
            print("[ERROR]", _e)
            print("下载图片时出错")
    return _images

epub_file = None
bookshelf_str = ''
if login_token and reader_id:
    try:
        print("正在获取书架信息...")
        bookshelf_str = bytes(opener.open("http://www.hbooker.com/bookshelf/my_book_shelf/").read()).decode()
        nickname = str_mid(bookshelf_str, '<span class="J_Nickname">', '</span>')
    except Exception as e:
        print("[ERROR]", e)
        print("获取书架信息时出错，取消登录")
        input("按下回车键继续...")
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
            input("按下回车键继续...")
            nickname = '${NoName}'
        del bookshelf_str
    while True:
        if nickname != '${NoName}':
            for book_info in bookshelf:
                print("编号:", book_info[0], "id:", book_info[1], "书名:", book_info[2])
            while True:
                book_id = input("输入书籍编号或id(输入q:退出,h:帮助):").lower()
                if not book_id:
                    continue
                if book_id.startswith('q'):
                    exit()
                elif book_id.startswith('h'):
                    print(doc_help)
                try:
                    if 0 < int(book_id) <= book_index:
                        book_id = bookshelf[int(book_id) - 1][1]
                    break
                except ValueError:
                    continue
        else:
            while True:
                book_id = input("输入书籍id(输入q:退出,h:帮助):").lower()
                if book_id.startswith('q'):
                    exit()
                elif book_id.startswith('h'):
                    print(doc_help)
                elif book_id:
                    break
        try:
            print("正在获取书籍信息...")
            book_chapter_str = bytes(opener.open("http://www.hbooker.com/book/" + book_id).read()).decode()
            book_title_str = str_mid(book_chapter_str, '<div class="book-title">', '</div>')
            book_title = str_mid(book_title_str, '<h1>', '</h1>')
            book_author = str_mid(book_title_str, 'class="">', '</a>')
            book_cover_url = str_mid(str_mid(book_chapter_str, '<div class="book-cover">', '</div>'), '<img src="', '"')
            print("书名:", book_title, "作者:", book_author)
            book_chapter = list()
            book_chapter_index = 0
            for str_ in re.findall('<li><a target="_blank".*?</a>',
                                   book_chapter_str):
                book_chapter_index += 1
                book_chapter_info = (str_mid(str_, 'href="http://www.hbooker.com/chapter/book_chapter_detail/', '"'),
                                     str_mid(str_, '</i>', '</a>').replace("<i class='icon-vip'></i>", "[VIP]"))
                book_chapter.append(book_chapter_info)
            print("共", book_chapter_index, "章", "最新章节:", str_mid(book_chapter_str, '<div class="tit">', '</div>'))
            del book_chapter_str, book_title_str
        except Exception as e:
            print("[ERROR]", e)
            print("获取书籍信息时出错")
            input("按下回车键继续...")
            continue
        try:
            print("正在检查文件...")
            cnt_success = 0
            cnt_fail = 0
            book_dir = os.getcwd() + "/../books/" + book_title
            book_file_cfg = None
            book_file_cfg_lines = list()
            last_id = 0
            fail_list = list()
            downloaded_list = list()
            if not os.path.isdir(book_dir):
                os.makedirs(book_dir)
            epub_file = Epub.EpubFile(book_dir + "/" + book_title + ".epub", book_dir + "/cache",
                                      book_id, book_title, book_author)
            if os.path.isfile(book_dir + "/" + book_title + ".cfg"):
                book_file_cfg = codecs.open(book_dir + "/" + book_title + ".cfg", 'r', 'utf-8')
                book_file_cfg_lines = book_file_cfg.readlines()
                book_file_cfg.close()
                for line in book_file_cfg_lines:
                    if line.startswith('chapter_error='):
                        for _i in str_mid(line, 'chapter_error={', '}').split(','):
                            if not _i or int(_i) - 1 < 0 or int(_i) - 1 > len(book_chapter):
                                continue
                            print("尝试修复章节:", "编号:", _i, "chapter_id:", book_chapter[int(_i) - 1][0], end="")
                            content = get_content(book_chapter[int(_i) - 1][0])
                            if isinstance(content, str):
                                if content.startswith('<a href='):
                                    fail_list.append(_i)
                                    cnt_fail += 1
                                    print("  ----  修复失败")
                                else:
                                    epub_file.fixchapter(
                                        book_chapter[int(_i) - 1][0], book_chapter[int(_i) - 1][1], content)
                                    for _image_info in get_images(content):
                                        epub_file.addimage(_image_info[0], _image_info[1])
                                    downloaded_list.append(_i)
                                    last_id = max(last_id, int(_i))
                                    cnt_success += 1
                                    print("  ----  修复成功")
                            else:
                                epub_file.fiximagechapter(
                                    book_chapter[int(_i) - 1][0], book_chapter[int(_i) - 1][1], content)
                                downloaded_list.append(_i)
                                last_id = max(last_id, int(_i))
                                cnt_success += 1
                                print("  ----  修复成功")
                    elif line.startswith('chapter_downloaded='):
                        _list = str_mid(line, 'chapter_downloaded={', '}').split(',')
                        if len(_list) and _list[0]:
                            downloaded_list.extend(_list)
                    elif line.startswith('chapter_last_id='):
                        last_id = int(str_mid(line, 'chapter_last_id="', '"') or 0)
                book_file_cfg = codecs.open(book_dir + "/" + book_title + ".cfg", 'w', 'utf-8')
                book_file_cfg.write('chapter_error={' + ','.join(fail_list) + '}' + nl +
                                    'chapter_downloaded={' + ','.join(downloaded_list) + '}' + nl +
                                    'chapter_last_id="' + str(last_id) + '"' + nl)
                book_file_cfg.close()
                if cnt_success or cnt_fail:
                    epub_file.export()
                    epub_file.export_txt()
                    print("章节修复完成，修复成功", cnt_success, "章，修复失败", cnt_fail, "章")
        except Exception as e:
            print("[ERROR]", e)
            print("检查文件时出错")
            input("按下回车键继续...")
            continue
        try:
            while True:
                while True:
                    try:
                        chapter_start = int(input("输入开始章节编号(留空将自动寻找):") or last_id + 1)
                        chapter_end = int(input("输入结束章节编号(留空将自动寻找):") or book_chapter_index)
                        break
                    except ValueError:
                        continue
                if chapter_start < 1:
                    chapter_start = 1
                if chapter_start > book_chapter_index:
                    confirm = 'q'
                    input("书籍暂无更新...")
                    break
                if chapter_start <= chapter_end:
                    print("开始章节编号:", chapter_start,
                          "chapter_id:", book_chapter[chapter_start - 1][0],
                          "标题:", book_chapter[chapter_start - 1][1])
                    print("结束章节编号:", chapter_end,
                          "chapter_id:", book_chapter[chapter_end - 1][0],
                          "标题:", book_chapter[chapter_end - 1][1])
                    while True:
                        confirm = input("确定从这个位置下载吗(y/n/q):").lower()
                        if confirm.startswith('y') or confirm.startswith('n') or confirm.startswith('q'):
                            break
                    if confirm.startswith('y') or confirm.startswith('q'):
                        break
                else:
                    print("输入无效:", "开始章节编号", chapter_start, "大于", "结束章节编号", chapter_end)
            if confirm.startswith('q'):
                if book_file_cfg:
                    book_file_cfg.close()
                continue
        except Exception as e:
            print("[ERROR]", e)
            print("读取章节编号时出错")
            input("按下回车键继续...")
            continue
        try:
            print("正在下载书籍内容...")
            epub_file.setcover(book_cover_url)
            cnt_success = 0
            cnt_fail = 0
            content = ''
            for chapter_index in range(chapter_start - 1, chapter_end):
                chapter_id = book_chapter[chapter_index][0]
                chapter_title = book_chapter[chapter_index][1]
                print("章节编号:", chapter_index + 1,
                      "chapter_id:", chapter_id,
                      "标题:", chapter_title, end="")
                if downloaded_list.count(str(chapter_index + 1)) > 0:
                    print("  ----  章节已下载，跳过该章节")
                    continue
                content = get_content(chapter_id)
                if isinstance(content, str):
                    if content.startswith('<a href='):
                        fail_list.append(str(chapter_index + 1))
                        cnt_fail += 1
                        print("  ----  下载失败")
                    else:
                        epub_file.addchapter(str(chapter_index + 1), chapter_id, chapter_title, content)
                        for _image_info in get_images(content):
                            epub_file.addimage(_image_info[0], _image_info[1])
                        downloaded_list.append(str(chapter_index + 1))
                        last_id = max(last_id, chapter_index + 1)
                        cnt_success += 1
                        print("  ----  下载成功")
                else:
                    epub_file.addimagechapter(str(chapter_index + 1), chapter_id, chapter_title, content)
                    downloaded_list.append(str(chapter_index + 1))
                    last_id = max(last_id, chapter_index + 1)
                    cnt_success += 1
                    print("  ----  下载成功")
            epub_file.export()
            epub_file.export_txt()
            book_file_cfg = codecs.open(book_dir + "/" + book_title + ".cfg", 'w', 'utf-8')
            book_file_cfg.write('chapter_error={' + ','.join(fail_list) + '}' + nl +
                                'chapter_downloaded={' + ','.join(downloaded_list) + '}' + nl +
                                'chapter_last_id="' + str(last_id) + '"' + nl)
            book_file_cfg.close()
            print("下载书籍已完成，下载成功", cnt_success, "章，下载失败", cnt_fail, "章")
            input("按下回车键继续...")
        except Exception as e:
            print("[ERROR]", e)
            print("下载书籍时出错")
            input("按下回车键继续...")
else:
    print("获取书架信息失败")
