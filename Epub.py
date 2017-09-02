import zipfile
import re
import os
import codecs

nl = '\r\n'


def str_mid(string: str, left: str, right: str, start=None, end=None):
    pos1 = string.find(left, start, end)
    if pos1 > -1:
        pos2 = string.find(right, pos1 + len(left), end)
        if pos2 > -1:
            return string[pos1 + len(left): pos2]
    return ''


def getallfiles(dirpath: str):
    result = list()
    for _name in os.listdir(dirpath):
        if os.path.isdir(dirpath + '/' + _name):
            result.extend(getallfiles(dirpath))
        else:
            result.append(dirpath + '/' + _name)
    return result


class EpubFile:
    _filepath = ''
    _tempdir = ''
    _content_opf = ''
    _content_opf_manifest = ''
    _content_opf_spine = ''
    _chapter_format_manifest = ''
    _chapter_format_spine = ''
    _toc_ncx = ''
    _toc_ncx_navMap = ''
    _chapter_format_navMap = ''
    _chapter_format = ''

    def __init__(self, filepath: str, tempdir: str, book_id: str, book_title: str, book_author: str):
        self._filepath = filepath
        self._tempdir = tempdir
        _template = zipfile.ZipFile(os.getcwd() + "/template/template.epub")
        self._content_opf = str(_template.read('OEBPS/content.opf'))
        self._chapter_format_manifest = str_mid(self._content_opf, '${chapter_format_manifest}={', '}')
        self._chapter_format_spine = str_mid(self._content_opf, '${chapter_format_spine}={', '}')
        self._toc_ncx = str(_template.read('OEBPS/toc.ncx'))
        self._chapter_format_navMap = str_mid(self._toc_ncx, '${chapter_format_navMap}={', '}')
        self._chapter_format = str(_template.read('OEBPS/Text/${chapter_format}.xhtml'))
        if os.path.isfile(filepath):
            try:
                with zipfile.ZipFile(self._filepath, 'r', zipfile.ZIP_DEFLATED) as _file:
                    _file.extractall(self._tempdir)
                    try:
                        self._content_opf = str(_file.read('OEBPS/content.opf'))
                        self._toc_ncx = str(_file.read('OEBPS/toc.ncx'))
                    except (KeyError, NameError, IOError):
                        self._content_opf = str(_template.read('OEBPS/content.opf'))
                        self._toc_ncx = str(_template.read('OEBPS/toc.ncx'))
            except zipfile.BadZipFile:
                for _name in _template.namelist():
                    if _name.find('$') == -1:
                        _template.extract(_name, self._tempdir)
                re.sub('\${.*?}={[\S\s]*?}', '', self._content_opf)
                self._content_opf_manifest = str_mid(self._content_opf, '<manifest>', '</manifest>')
                self._content_opf_spine = str_mid(self._content_opf, '<spine toc="ncx">', '</spine>')
                re.sub('\${.*?}={[\S\s]*?}', '', self._toc_ncx)
                self._toc_ncx_navMap = str_mid(self._toc_ncx, '<navMap>', '</navMap>')
                self._content_opf = self._content_opf.replace('${book_id}', book_id)
                self._content_opf = self._content_opf.replace('${book_title}', book_title)
                self._content_opf = self._content_opf.replace('${book_author}', book_author)
                self._toc_ncx = self._toc_ncx.replace('${book_id}', book_id)
                self._toc_ncx = self._toc_ncx.replace('${book_title}', book_title)
                self._toc_ncx = self._toc_ncx.replace('${book_author}', book_author)
                with codecs.open(self._tempdir + '/OEBPS/content.opf', 'w', 'utf-8') as _file:
                    _file.write(self._content_opf)
                with codecs.open(self._tempdir + '/OEBPS/toc.ncx', 'w', 'utf-8') as _file:
                    _file.write(self._toc_ncx)
        else:
            for _name in _template.namelist():
                if _name.find('$') == -1:
                    _template.extract(_name, self._tempdir)
            re.sub('\${.*?}={[\S\s]*?}', '', self._content_opf)
            self._content_opf_manifest = str_mid(self._content_opf, '<manifest>', '</manifest>')
            self._content_opf_spine = str_mid(self._content_opf, '<spine toc="ncx">', '</spine>')
            re.sub('\${.*?}={[\S\s]*?}', '', self._toc_ncx)
            self._toc_ncx_navMap = str_mid(self._toc_ncx, '<navMap>', '</navMap>')
            self._content_opf = self._content_opf.replace('${book_id}', book_id)
            self._content_opf = self._content_opf.replace('${book_title}', book_title)
            self._content_opf = self._content_opf.replace('${book_author}', book_author)
            self._toc_ncx = self._toc_ncx.replace('${book_id}', book_id)
            self._toc_ncx = self._toc_ncx.replace('${book_title}', book_title)
            self._toc_ncx = self._toc_ncx.replace('${book_author}', book_author)
            with codecs.open(self._tempdir + '/OEBPS/content.opf', 'w', 'utf-8') as _file:
                _file.write(self._content_opf)
            with codecs.open(self._tempdir + '/OEBPS/toc.ncx', 'w', 'utf-8') as _file:
                _file.write(self._toc_ncx)
        _template.close()

    def setcover(self, image: bytes):
        with open(self._tempdir + '/OEBPS/Images/cover.jpg', 'wb') as _file:
            _file.write(image)

    def addchapter(self, chapter_index: str, chapter_id: str, chapter_title: str, chapter_content: str):
        _data = self._chapter_format.replace('${chapter_title}', chapter_title)\
            .replace('${chapter_content}', chapter_content)
        with codecs.open(self._tempdir + '/OEBPS/Text/' + chapter_id + '.xhtml', 'w', 'utf-8') as _file:
            _file.write(_data)
        if self._content_opf_manifest.find('id="' + chapter_id + '.xhtml"') == -1:
            _before_content_opf_manifest = self._content_opf_manifest
            self._content_opf_manifest += self._chapter_format_manifest.replace('${chapter_id}', chapter_id) + nl
            self._content_opf = self._content_opf.replace(_before_content_opf_manifest, self._content_opf_manifest)
        if self._content_opf_spine.find('idref="' + chapter_id + '.xhtml"') == -1:
            _before_content_opf_spine = self._content_opf_spine
            self._content_opf_spine += self._chapter_format_spine.replace('${chapter_id}', chapter_id) + nl
            self._content_opf = self._content_opf.replace(_before_content_opf_spine, self._content_opf_spine)
        if self._toc_ncx_navMap.find('id="' + chapter_id) == -1:
            _before_toc_ncx_navMap = self._toc_ncx_navMap
            self._toc_ncx_navMap += self._chapter_format_navMap.replace('${chapter_id}', chapter_id)\
                                        .replace('${chapter_index}', chapter_index)\
                                        .replace('${chapter_title}', chapter_title) + nl
            self._toc_ncx = self._toc_ncx.replace(_before_toc_ncx_navMap, self._toc_ncx_navMap)
        with codecs.open(self._tempdir + '/OEBPS/content.opf', 'w', 'utf-8') as _file:
            _file.write(self._content_opf)
        with codecs.open(self._tempdir + '/OEBPS/toc.ncx', 'w', 'utf-8') as _file:
            _file.write(self._toc_ncx)

    def addimage(self, filename: str, image: bytes):
        with open(self._tempdir + '/OEBPS/Images/' + filename, 'wb') as _file:
            _file.write(image)

    def addimagechapter(self, chapter_index: str, chapter_id: str, chapter_title: str, image: bytes):
        self.addchapter(chapter_index, chapter_id, chapter_title,
                        '<img src="../Images/' + chapter_id + '.png" alt=\'' + chapter_title + '\'>')
        with open(self._tempdir + '/OEBPS/Images/' + chapter_id + '.png', 'wb') as _file:
            _file.write(image)

    def fixchapter(self, chapter_id: str, chapter_title: str, chapter_content: str):
        _data = self._chapter_format.replace('${chapter_title}', chapter_title) \
            .replace('${chapter_content}', chapter_content)
        with codecs.open(self._tempdir + '/OEBPS/Text/' + chapter_id + '.xhtml', 'w', 'utf-8') as _file:
            _file.write(_data)

    def fiximagechapter(self, chapter_id: str, chapter_title: str, image: bytes):
        self.fixchapter(chapter_id, chapter_title, '<img src="../Images/' + chapter_id + '.png">')
        with open(self._tempdir + '/OEBPS/Images/' + chapter_id + '.png', 'wb') as _file:
            _file.write(image)

    def export(self):
        with zipfile.ZipFile(self._filepath, 'w', zipfile.ZIP_DEFLATED) as _file:
            _result = getallfiles(self._tempdir)
            for _name in _result:
                _file.write(_name, _name.replace(self._tempdir + '/', ''))

    def export_txt(self):
        with codecs.open(self._filepath.replace('.epub', '.txt'), 'w', 'utf-8') as _file:
            _data = ''
            for _name in os.listdir(self._tempdir + '/OEBPS/Text'):
                if _name.find('$') > -1 or _name == 'cover.xhtml':
                    continue
                with codecs.open(_name, 'r', 'utf-8') as _file_xhtml:
                    _data_chapter = _file_xhtml.read()
                    for _a in re.findall(r'<a href=.*?>章节链接</a>', _data_chapter):
                        _data_chapter = _data_chapter.replace(_a, '章节链接:' + str_mid(_a, '<a href="', '"'))
                    for _img in re.findall(r'<img src=.*?>', _data_chapter):
                        _data_chapter = _data_chapter.replace(_img, '图片:"' + str_mid(_img, "alt='", "'") + '",' +
                                                              '位置:"' + str_mid(_img, '<img src="', '"')
                                                              .replace('../', '') + '"')
                    _data_chapter = re.sub(r'</?[\S\s]*?>', '', _data_chapter)
                    _data_chapter = re.sub(r'[\r\n]+', nl * 2, _data_chapter)
                _data += _data_chapter + nl
            _file.write(_data)
