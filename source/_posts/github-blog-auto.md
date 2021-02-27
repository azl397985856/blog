---
title: 如何自动同步博客到 Github 主页？
tags: [Github, 持续集成]
categories: [Github]
date: 2021-02-27
---

## 前言

Github 支持通过创建同名仓库的形式自定义主页。比如我的 Github 用户名是 azl397985856，那么新建一个名为 azl397985856 的仓库即可。接下来你可以通过修改此仓库的 README 文件来自定义 Github 主页。也就是说，你想要自定义主页就新建一个同名仓库并修改 README 就行了。

修改 README 能玩出什么花样呢？请接着往下看。

<!-- more -->

## 装修效果

先上一下我的装修效果：

![](https://tva1.sinaimg.cn/large/008eGmZEly1go0wmr2tajj30yn0p447m.jpg)

## 开始动手

### 添加数据统计

上图的那几个 Github 数据统计以及奖杯使用的是一个外部服务。想要显示哪个就添加相应代码即可：

数据统计：

```md
<img src="https://github-readme-stats.vercel.app/api?username=azl397985856&show_icons=true" alt="logo" height="160" align="right" style="margin: 5px; margin-bottom: 20px;" />
```

> 注意将 username 改成自己的用户名哦(下面也是一样，不再赘述)，不然就显示的 lucifer 我的信息啦。

奖杯：

```md
<img src="https://github-profile-trophy.vercel.app/?username=azl397985856&theme=flat&column=7" alt="logo" height="160" align="center" style="margin: auto; margin-bottom: 20px;" />
```

### 自动更新博客

如上图我的装修主页，其中博客的文章列表不是写死的，而是每隔一个小时定时读取我的[博客](https://lucifer.ren/blog/ "lucifer 的网络博客") 内容，并提取前 5 篇文章。

如果你也想要这个功能，就在 README 中添加如下代码即可：

```md
## 📕 Latest Blog Posts

<!-- BLOG-POST-LIST:START -->
<!-- BLOG-POST-LIST:END -->
```

之后读取的博客列表会填充在两个注释之间，也就是说你可以**通过改变注释的位置，将其放到页面任意位置**。

为了实现**每个小时定时更新的功能**，我们可以使用 Github Action 的定时任务来实现。

具体操作步骤如下：

![](https://tva1.sinaimg.cn/large/008eGmZEly1go0x6m5ha2j30yb06zt9o.jpg)

![](https://tva1.sinaimg.cn/large/008eGmZEly1go0x818quij30nh09mdh2.jpg)

接下来将如下内容复制粘贴进去：

```yml
name: Blog Posts

on:
  # Run workflow automatically
  schedule:
    # Runs every hour, on the hour
    - cron: "0 * * * *"

jobs:
  update-readme-with-blog:
    name: Update this repo's README with latest blog posts
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: gautamkrishnar/blog-post-workflow@master
        with:
          # comma-separated list of RSS feed urls
          feed_list: "https://lucifer.ren/blog/atom.xml"
```

> 注意：这里的 `cron: "0 * * * *"` 的意思是每个小时进行一次，并且是每个小时的 0 分。 因为你需要等到下一个整点才能看到效果，有时候 Github 会有延时，晚几分钟也正常，大家不要着急，耐心等待即可。

请将 feed_list 替换为你自己的 RSS 订阅地址。如果有多个订阅地址，则用英文半角逗号分割。

如果你的博客没有 RSS 或者你不知道自己的 RSS 地址就无法使用了哦。我的博客是用 hexo 生成的，因此添加 RSS 就很容易了，如果你的博客是挂到第三方的，也会提供 RSS 地址。比如 CSDN 就提供了 RSS 地址：

![](https://tva1.sinaimg.cn/large/008eGmZEly1go0xhrc16dj311i06240f.jpg)

由于大家的博客可能都不相同，因此具体大家可以自行搜索。

## 完整源代码

本文所有的代码都可以在如下的代码仓库中找到。

仓库地址：https://github.com/azl397985856/azl397985856

如果在使用过程中碰到其他问题，也欢迎私信我哦~ 最后祝大家都有一个高大上的 Github 主页。
