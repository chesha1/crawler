# crawler
## pixiv_novel
### pixiv_novel_v1.py
包含了一些写在开始的函数，可以处理直接获取到的文章标题，去除不想要的部分得到纯净的标题  
但其实没有必要，因为可以直接获取到纯净的标题和系列标题  

### pixiv_novel_v2.py
调整了一下文件结构，删除冗余函数

### pixiv_novel_v3.py
对于没有访问权限（好 P 友）的文件，直接跳过，不会影响运行  
自动启动和关闭 Chrome

### pixiv_novel_v4.py
对文件名进行修改，把在 Windows（onedrive）下面非法的文件名字符替换成 _  
调整了文件结构和部分命名

### pixiv_novel_v5.py
增加了从每天的 toplist 中爬取一页小说的功能

### pixiv_novel_v6.py
增加了从每月、每季度、每年的 toplist 中爬取一页小说的功能  
增加了清理文件名的逻辑

### delete_dep.py
对于用 pixiv_novel.py 下载的文件  
删除重复文件，如果相同文件名下有文件大小相差超过 1kb，删除更早的那个文件  
如果大小相差过大，默认有不同的内容，保留多个版本

## bili_image.py
下载 B 站动态中的图片  
从 txt 文件的每一行中获取动态号  