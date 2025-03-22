---
title: AI + terminal 等于 Warp？
tags: [工具, Warp, iTerm2, 终端]
categories:
  - [工具, 终端]
date: 2025-03-19
---

作为一个开发者，终端是你最亲密的伙伴。它可能是你调试代码的战场，也可能是你部署项目的指挥部。但让我们面对现实：大多数人用的终端，要么是 macOS 自带的 Terminal，要么是久负盛名的 iTerm2。这些工具很可靠，但它们也像老派的骑士——忠诚，却不够灵动。然后，Warp 来了，像个不按套路出牌的叛逆者，直接挑战终端的传统定义。

Warp 和 iTerm2，一个是新世代的先锋，一个是久经考验的经典。它们有何不同？Warp 又在哪些地方彻底碾压了 iTerm2？让我们一探究竟。

<!-- more -->

Warp 下载地址：https://app.warp.dev/referral/VZRGNK

## Warp 和 iTerm2

先说 iTerm2。它是 macOS 终端界的标杆，开源、稳定、功能丰富。从多标签页到分屏，从自定义主题到强大的快捷键支持，它几乎满足了所有传统终端用户的需求。它就像一辆经过精心调校的老爷车，虽然不是最快的，但你知道它永远不会抛锚。

Warp 则完全是另一回事。它不是在既有框架上修修补补，而是从零开始，用 Rust 重写了一个现代终端。Rust 带来的性能优势显而易见：启动快、响应快。但更重要的是下面三点。

### 1. 智能化：AI 加持的未来感


Warp 内置了 AI 支持，可以根据自然语言生成命令、解释错误，甚至帮你调试。这在 iTerm2 上完全没有。

**AI 聊天**

你问 iTerm2 “怎么杀掉某个进程”，它会报错；而 Warp 却能直接吐出 `kill -9 <pid>`，甚至告诉你为什么用 `-9`。对于开发者来说，这都是生产力的飞跃。

再比如你想列出开头为 . 的文件和文件夹，就可以这样直接问 Warp：

![](https://p.ipic.vip/i928lb.png)

有了这个功能，从此你有机会不用懂怎么写命令，直接用自然语言来完成之前需要命令行完成的工作。

**带上下文的互动式命令**

比如我想订阅 lucifer.ren/blog 的 RSS，但是我一方面不知道它的 RSS 在哪。另外一方面我也不知道用命令行怎么写。那么你可以直接直接告诉 warp：“get the rss info from lucifer.ren/blog”

接下来它会告诉你命令是：`curl -L https://lucifer.ren/blog/rss.xml`，并且会直接执行。然后告诉你：

> The initial attempt to get the RSS feed from lucifer.ren/blog/rss.xml returned a 404 error page. Let me try an alternative URL that's commonly used for RSS feeds - atom.xml, as I noticed in the 404 page there's a reference to "/blog/atom.xml".

大概意思就是它猜测 rss 地址是 `lucifer.ren/blog/rss.xml`，但是 curl 了下发现 404 了，但是它发现 404 页面有一个 /blog/atom.xml 链接，于是尝试了这个链接，果然成功了。

最后它告诉你用这个命令 `curl -L https://lucifer.ren/blog/atom.xml`

还贴心地帮你分析了一波：

> 成功获取到了 lucifer.ren/blog 的 RSS/Atom feed。从最近的文章列表来看，这是一个主要关注算法、前端开发、区块链（Web3）等技术话题的博客。最新的几篇文章包括：...

![](https://p.ipic.vip/yuioaz.png)

**报错修复**

另外一点很爽的是它能提供很多有用建议。比如你执行 `install` 命令报错了，它会根据报错信息给出建议，你需要做的就是按提示操作。有时候甚至**你只需要不停按 enter 键，它就能帮你修复问题**。

比如 `pnpm install` zsh 报错: command not found: pnpm。它会先告诉你原因：

> The output shows that pnpm is not installed on the system. Since we're on macOS (indicated by the /Users path), we can install pnpm using npm, which is typically pre-installed with Node.js. Let's check if npm is available first.

接下来给出建议，让你输入 npm --version，看看 npm 是否安装成功，以及版本。

他发现你的 npm 是 7.21.1，于是说：

> Great, npm is available. We can now use npm to install pnpm globally. The recommended way to install pnpm is using npm's global installation flag (-g).

接下来建议你 `npm install -g pnpm`， 你继续 enter 来接受它的建议。

然后不出意外又报错了，它又建议你 `npm install -g pnpm@7`，然后 `npm audit` 查看效果。

最后你输入 `pnpm install` 成功了。

![](https://p.ipic.vip/0ehnv3.png)

这就是 Warp 的智能化能力。这种感觉就好像**有一个老手程序员再远程协助你，帮你修复错误！**

### 2. 协作与分享：团队玩家的逆袭

iTerm2 是单机时代的产物，配置和命令历史只能自己用。Warp 却有云同步和 Warp Drive 功能，你可以把常用命令、工作流保存下来，随时分享给团队。生成一个命令块的链接，扔给同事，他们就能直接复用你的操作。这在 iTerm2 上得靠手动复制粘贴，效率差了一大截。

### 3. 界面与美感：从功能至上到赏心悦目

iTerm2 的界面很实用，但谈不上好看，主题再怎么调也有种上世纪的味道。Warp 的 UI 设计现代感爆棚，默认主题就足够抓眼球。

![](https://p.ipic.vip/jhovzr.png)

部分主题参考：

![](https://p.ipic.vip/1q34g0.png)

![](https://p.ipic.vip/fmt28k.png)

而且它的命令块、补全菜单都经过精心打磨，用起来有种“爽”的感觉。iTerm2 的自定义虽然灵活，但需要折腾，Warp 开箱即用就能惊艳你。

## 总结

Warp 首先吸引我的是 UI，主题非常现代化。

然后用起来就发现了它 AI 能力的强大，Warp 和 iTerm2 的最大区别就是 AI 的加持，这是一个未来趋势。个人每天的使用 API 频率是有限制的，不过对于我来说已经够了。如果你觉得不够，可以采用付费方案。

另外它将终端从单机应用转变为协作工具，让开发者和团队更高效地工作。

Warp 的界面设计、功能强大、云同步、协作分享，则让它成为终端界的先锋。

Warp 下载地址：https://app.warp.dev/referral/VZRGNK

## 力扣专属折扣

力扣免费题目已经有了很多经典的了，也覆盖了所有的题型，只是很多公司的真题都是锁定的。个人觉得如果你准备找工作的时候，可以买一个会员。另外会员很多 leetbook 也可以看，结合学习计划，效率还是蛮高的。

现在力扣在每日一题基础上还搞了一个 plus 会员挑战，每天刷题可以获得积分，积分可以兑换力扣周边。

![](https://p.ipic.vip/saz963.png)

如果你要买力扣会员的话，这里有我的**专属力扣折扣：https://leetcode.cn/premium/?promoChannel=lucifer** (年度会员**多送两个月**会员，季度会员**多送两周**会员)
