---
title: 跨域了？ 装个插件就够了！
tags: [前端]
date: 2022-02-06
categories:
  - [前端]
---

浏览器为了安全引入了同源策略，这直接导致默认情况下前后端域名如果不同，那么则功能会受限。 随着前后端分离的发展，前端和后端职责的分离，前端会有专门的`本地开发服务器(local dev server)`用于本地开发。这个时候和后端接口联调时就很可能会遇到跨域安全问题。

这本身是浏览器的一种安全策略，但是却对前端开发造成了影响。如何解决呢？

<!-- more -->

之前我的解决方式是通过本地代理（node 或 nginx 等服务）解决。基本思路就是给请求响应头增加大概如下内容：

```
Access-Control-Allow-Origin: https://foo.example
Access-Control-Allow-Methods: POST, GET, OPTIONS
Access-Control-Allow-Headers: X-PINGOTHER, Content-Type
Access-Control-Max-Age: 86400
```

后来我使用了更方便的工具： 浏览器扩展。之后跨域问题便可以一去不复返。

刚开始的时候用的是一个专门给请求加跨域头的插件 `Allow CORS: Access-Control-Allow-Origin` ，地址：https://chrome.google.com/webstore/detail/allow-cors-access-control/lhobafahddgcelffkeicbaginigeejlf/related?hl=en-US。

![](https://tva1.sinaimg.cn/large/008i3skNly1gz3wawv2cpj30sk0d874x.jpg)

这个插件使用起来非常简单，只需要点击切换 on 和 off 的状态即可。 on 的时候会自动给请求头增加跨域功能，off 则相当于禁用了插件。

后来我发现这个插件有些头不会加上，比如 access-control-expose-headers 。

因此一个**通用的给请求增加头信息**的插件就有必要了。于是我选择了 `requestly`

![](https://tva1.sinaimg.cn/large/008i3skNly1gysjmuktv3j32do0u0q6n.jpg)

美中不足是每个规则只能免费改**一个**头。不过好消息是你可以新建多个规则，每个规则改一个头就可以白嫖了。

地址：https://app.requestly.io

requestly 不仅仅可以增加跨域请求头，理论上可以对请求和响应做任意的修改。因此用来做 mock，统一加参数等等都是可以的。

基于此，使用浏览器扩展就可以彻底解决前端在本地开发时候遇到的跨域问题了。
