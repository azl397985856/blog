---
title: 如何将 github 上的代码一键部署到服务器？
tags: [CD, GitHub]
date: 2021-02-14
categories:
  - [CD]
---

- 在 Github 上看到一些不错的仓库，想要贡献代码怎么办？

- 在 Github 上看到一些有用的网站，想部署到自己的服务器怎么办？

- 。。。

我想很多人都碰到过这个问题。

- 如果要贡献代码，之前我的做法通常是将代码克隆到本地，然后在本地的编辑器中修改并提交 pr。
- 如果想部署到自己的服务器，之前我的做法通常是克隆到本地，然后本地修改一下部署的配置，最后部署到自己的服务器或者第三方的云服务器（比如 Github Pages）。

而现在随着云技术的普及，我们**没有必要将代码克隆到本地进行操作，而是直接在云端编辑器中完成修改，开发，并直接部署到云服务器**。今天就给大家推荐一个工具，一键将代码部署到云服务器。

​<!-- more -->

## 什么是一键部署？

今天给大家介绍的就是一键部署。那什么是一键部署呢？顾名思义，就是有一个按钮，点击一下就能完成部署工作。

如下是一个拥有一键部署按钮的项目：

![](https://tva1.sinaimg.cn/large/008eGmZEly1gnmaoyktqej311r0u0jxo.jpg)

点击之后进入如下页面，你可以对一些默认配置进行修改（也可以直接使用默认配置）:

![](https://tva1.sinaimg.cn/large/008eGmZEly1gnmapsm8k8j30u00vftdf.jpg)

修改后点击**Deploy app** 即可。部署成功之后就可以通过类似如下的地址访问啦~

![](https://tva1.sinaimg.cn/large/008eGmZEly1gnmaqkh8hfj31810u0ag0.jpg)

> 图中演示地址是：https://leetcode-cheat.herokuapp.com/

大家可以直接进我的仓库 https://github.com/leetcode-pp/leetcode-cheat，点击部署按钮试试哦。

## 它是如何实现的呢？

我是一个喜欢探究事物原理的人，当然对它们的原理了如指掌才行。其实它的原理很容易，我们从头开始说。

### 1. 如何在 Github 中显示发布按钮。

上面的部署按钮就是如下的一个 Markdown 内容渲染的:

```md
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
```

上面内容会被渲染成如下的 DOM：

```html
<a href="https://heroku.com/deploy" rel="nofollow"
  ><img
    src="https://camo.githubusercontent.com/6979881d5a96b7b18a057083bb8aeb87ba35fc279452e29034c1e1c49ade0636/68747470733a2f2f7777772e6865726f6b7563646e2e636f6d2f6465706c6f792f627574746f6e2e737667"
    alt="Deploy"
    data-canonical-src="https://www.herokucdn.com/deploy/button.svg"
    style="max-width:100%;"
/></a>
```

也就是说其实就是一个被 a 标签包裹的 svg 图片，点击之后会完成 url 跳转。

### 2. 云服务厂商如何获取默认配置？

这里以 heroku 为例，其他厂商（比如腾讯）原理都差不多。

由于上面的原因，实际上我们传递给第三方云厂商的方式只可能是 url。因此我们可以直接将配置通过 ur 的方式传输。比如 https://heroku.com/deploy?a=1&b=2&c=3 。 这种方式对于少量数据是足够的，那如何数据量很大呢？我们知道浏览器 url 的长度是有限的，而且不同的浏览器限制也不尽相同。

那怎么解决呢？现在比较流行的思路是**约定**。以 heroku 来说，就约定根目录的 `app.json` 文件中存配置，这种约定的方式我个人强烈推荐。

比如我的仓库的 app.json 就是：

```json
{
  "name": "LeetCode Cheatsheet",
  "description": "力扣加加，或许是西湖区最好的算法题解",
  "repository": "https://github.com/leetcode-pp/leetcode-cheat",
  "logo": "https://tva1.sinaimg.cn/large/008eGmZEly1gnm68epc0kj30u00tsaav.jpg",
  "keywords": ["github", "leetcode", "cheatsheet", "91algo", "algorithm"],
  "env": {
    "REACT_APP_BUILD_TARGET": {
      "description": "枚举值：extension 和 web",
      "value": null
    },
    "PUBLIC_URL": {
      "description": "静态资源存放位置（可使用 cdn 加速）",
      "value": "https://cdn.jsdelivr.net/gh/leetcode-pp/leetcode-cheat@gh-pages/"
    }
  },
  "buildpacks": [
    {
      "url": "https://buildpack-registry.s3.amazonaws.com/buildpacks/mars/create-react-app.tgz"
    }
  ]
}
```

可以看出，除了配置仓库，logo，描述这些常规信息，我还配置了环境变量和 buidpacks。buildpacks 简单来说就是构建应用的方式， 关于 buildpacks 的更多信息可以参考 [heroku 官方文档](https://devcenter.heroku.com/articles/buildpacks)

大家可能还有疑问，为啥上面的链接是 https://heroku.com/deploy。可以看出 url 中也没有任何参数信息，那为什么它就知道从哪来的呢？我觉得 ta 应该利用的是浏览器的 referer，用它可以判断从哪里过来的，进而搜索对应项目根目录的 app.json 文件。你可以通过右键在新的**无痕模式**中打开来验证。你会发现右键在新的无痕模式中打开是无法正常部署的。

## 这有什么用呢？

一键部署意味着部署的门槛更低，不仅是技巧上的，而且是成本上的。比如 heroku 就允许你直接免费一键部署若干个应用，直接生成网站，域名可以直接访问。如果你觉得域名不喜欢也可以自定义。如果你想修改源码重新构建也是可以的。

比如我看到别人的博客很漂亮。如果 ta 提供了一键部署，那么就可以直接部署到自己的云服务器，生成自己的 url。关联自己的 git 之后，推送还能自动部署（CD）。而且这一切都可以是免费的，至少我现在用的是免费的。 而如果 ta 没有提供一键部署，就需要你自己手动完成了。如果你对这些熟悉还好，无非就是多花点时间。而如果你是技术小白，我可能仅仅是想部署一下，用自己的域名访问之类，没有一键部署就很不友好啦。

## 相关技术

gitpod 是我一直在用的一个工具，它可以帮助我直接在云端编辑一些内容。或者有一些环境问题，需要虚拟主机的，也可以用它来解决。 它不仅仅提供了在线 IDE 的所有功能，还集成了 CI 和 CD，用起来也是非常方便。

同样地，你也可以在你的仓库中增加**在 Gitpod** 一键打开的功能。

![](https://tva1.sinaimg.cn/large/008eGmZEly1gnmbmu2ijhj319m0ioq5x.jpg)

## 小技巧

一些开源项目你不知道怎么贡献。其实可以另辟蹊径，比如给他们贡献一个 logo，再比如贡献**一键部署**功能。这或许是你迈向开源事业的第一步。

## 更多资料

- [heroku-button](https://devcenter.heroku.com/articles/heroku-button "heroku-button")
- [cloudbase 一键部署](https://docs.cloudbase.net/framework/deploy-button.html#bu-shu-an-niu-shi-ru-he-gong-zuo-de "cloudbase 一键部署")
