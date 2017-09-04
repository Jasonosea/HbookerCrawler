# HbookerCrawler
- 欢乐书客网页版爬虫，获取书籍内容，支持图片章节(已付费VIP章节)下载
- 支持导出文件格式：txt，epub(可能会继续添加)
- 章节顺序是按照欢乐书客网页版的顺序，与欢乐书客App的章节顺序有所不同
- 文件将会被下载至 ../books 目录下
- 下载失败的章节会在内容中留下一个章节链接，可尝试章节修复或直接在线阅读
- 不要修改下载好的书籍文件，否则可能会导致无法识别章节和更新书籍
- 请保证下载完成，否则下载好的书籍可能会出现各种不可预料的问题
- 若出现问题可尝试删除书籍有关文件夹

## 需求环境
- Python3(测试环境Python3.6.2)
- PyExecJS(测试环境PyExecJS1.4.0)
- Node.js(测试环境Node.js(V8))
