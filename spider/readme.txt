使用说明：
目前测试情况，最好全部使用点击操作，有些网站直接打开加载不完。1.0可以使用，以后有时间再开发了。
由于时间关系，异常捕获不全面，待完善。

模板说明：
extract_way：1。正则，2。BeautifulSoup（待开发）3。xpath（待开发）。
output_way：1。本地json，其他带开发。
scroll_script：为滚动脚本，浏览器不变，可不变。
scroll_length：滚动幅度，视异步数据情况而定。
scroll_time：滚动次数，视页面幅度而定，为上限。代码内另有判断，实际会小于等于上限。
limit：详细页面限制翻页次数，避免部分网站垃圾数据
list_size：记录列表页面“大小”，用来翻页。
list：中用来取得列表页数据。
url_unit：拼接详细页面翻页。
details：用来取得详细页面数据。
click：点击相关
click_link_id：用于识别详细页面链接，第二条key不能空，value可以空
