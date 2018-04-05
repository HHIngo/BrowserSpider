使用说明：
目前测试情况，最好全部使用点击操作，有些网站直接打开加载不完。
由于时间关系，异常捕获不全面，待完善。
BeautifulSoup，xpath鄙人不怎么用，没有测试
拼接url的模式，由于测试网站直接进入详细页面加载不完（点击没事），无法完成测试。有时间再找别的网站测试。
登陆模块考虑开发，但考虑封号风险，暂时没做。

1.0 可以使用，以后有时间再开发了。
1.1 更新bloomfilter,数据提纯和精炼
1.2 更新重整数据格式（考虑可能有定制需求，可以再提出来），以便于数据分析。更改集合去重url与website_id联系，提升数据量大后的效率。

模板说明：
extract_way：1.正则，2.BeautifulSoup（待开发）3。xpath（待开发）。
output_way：1.本地json，其他带开发。
dedup_way：1.集合去重，2.bloomfilter
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

Alchemy.json
purify: 提纯{表达式：内容}
refine：剔除表达式
reconstruct：重整数据的key,value对应数据(key数量等于value数量) 
