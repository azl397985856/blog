---
title: 一切皆插件：DeepSeek Harness
tags: [deepseek, harness, agent, cordis, plugin]
date: 2026-09-27
categories:
  - [ai, agent]
---

Agent 是一个非常流行的概念。模型负责思考，但模型自己并不能读文件、跑命令、记住上下文、在真实环境里把一件事做完。网上关于 Agent 的资料非常多，Claude Code、Codex 这类产品大家也用得不少，但是把「模型之外那一层」从零讲清楚的却很少。

<!-- more -->

熟悉这类产品的朋友应该知道：扩展点大多锁死在核心里。想换模型、换工具、加一层审计、换一套沙箱，往往只能 fork。DeepSeek 把这一层单独抽出来开源了，名字叫 **DeepSeek Harness**（`dsh`），口号就六个字：**一切皆插件**。

本文不是产品手册，而是把它的思想、接入方式和底层实现放到一起讲清楚。读完你应该能回答三件事：它到底是什么、你怎么把它跑起来、它凭什么敢说「没有特权内核」。

## 前言

由于本文会落到配置、SDK 和事件流，建议你对大模型 Agent 有一点直觉：知道「模型会调工具」，知道有会话、有权限、有工作目录。如果你连 Agent 是什么都不熟，可以先随便玩一下 Claude Code 或任何带工具调用的聊天产品，有体感再回来看会轻松很多。

本文会夹一点 TypeScript 和 Python。语法都不难，相信我它真的很容易懂。如果你实在卡住，丢给大模型翻译成你熟悉的语言就行。

官方入口放这里，后面会反复用到：

- 源码：[github.com/deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)
- 产品页：[deepseek.com/harness](https://www.deepseek.com/harness/)
- 文档：[deepseek-harness.github.io](https://deepseek-harness.github.io/deepseek-harness/)

目前是 **开发者预览**，MIT 协议，迭代很快，会有破坏性变更。跑之前最好先翻一下仓库里的 [SAFETY.md](https://github.com/deepseek-ai/deepseek-harness/blob/master/SAFETY.md)。

## 学习建议

为了方便对照，文里会给出能直接跑的命令和尽量短的代码。强烈建议你开一个隔离目录，边看边敲，一起运行看效果。只有动手才可能真正理解：为什么换模型不用改源码，为什么卸掉一个插件不会留下孤儿状态。

尽可能按思路默写，而不是复制粘贴。复制一遍和理解一遍，差别非常大。

Agent 的世界里，模型是灵魂，但灵魂自己走不了路。Harness 才是手脚、记忆和纪律。今天我们就从这句公式开始。

---

DeepSeek 自己是这么定义的：

> **Agent = Model + Harness**

模型负责思考。Harness 负责让 Agent 理解环境、使用工具，并在真实场景里持续工作。

一句话来总结 Harness 是什么：

> 它不是一个模型，也不是一个聊天网站。它是给模型配上工具、会话、沙箱、循环和 UI 的那一层运行时。你可以把它理解成 Agent 的操作系统。

## 什么是 Harness

在讲插件之前，我们先看一个很容易混淆的问题：你平时用的编码 Agent，到底哪一部分是模型，哪一部分是产品？

模型只会「想」和「说」。真正让它变得能干活的，是外面那一层：

- 怎么把仓库、终端、浏览器交给它
- 怎么记住上一轮说了什么、调了什么工具
- 怎么在删文件、跑命令之前问你一声
- 怎么把一次任务拆成多步，失败了重试，子任务再派出去
- 怎么在界面上把过程展示出来

这些东西合在一起，就是 Harness。Claude Code 有自己的 Harness，Cursor 有自己的，Codex 也有。差别在于：它们大多把这一层做成了产品核心，你很难拆。DeepSeek Harness 的野心是把这一层做成 **可组装的开源基础设施**。

想象一个插座板。模型是插上去的电器，工具、沙箱、UI、甚至「思考的主循环」都是插座上的插口。电器坏了换电器，插口不够就再插一个排插——这就是「一切皆插件」要达到的体感。

所以它能干什么，其实很具体：

| 你想做的事 | 它对应的用法 |
|---|---|
| 本地对着仓库干活 | 浏览器 Web UI |
| 脚本里跑一次任务就退出 | headless |
| 嵌进自己的 Python / TS 程序 | SDK |
| 给 IDE、自动化客户端接上 | ACP |
| 换模型、换搜索、换沙箱 | 写插件或改 YAML |
| 给模型做最小环境评测 | Minimal 模式 |

它能读改工作区文件、跑命令、委派子 Agent、维护计划。Web UI 在权限策略要求批准时会弹确认——这不是装饰，是 Harness 作为「手脚」必须有的纪律。

## 在讲插件之前，先看看「写死的核心」

这对我们理解后面的 Cordis 很有帮助。

传统做法大概是这样：仓库里有一个 `agent-loop.ts`，里面 import 了某个模型 SDK，再 import 了一堆工具，再 import 一套文件层。你要换模型，就去改 loop；你要加审计，就去 loop 里插一行；你要禁用某个工具，还得翻它的注册表。时间久了，核心文件谁都不敢动。

Harness 把这个问题反过来处理：**内核不承载任何 Agent 能力**。内核只负责三件事：插件怎么加载、怎么卸载、插件之间的依赖谁先谁后。模型适配器是插件，工具是插件，会话日志是插件，沙箱是插件，调度是插件，UI 是插件，**连 Agent 主循环本身也是插件**。

扩展方式永远只有一种：在旁边再挂一个插件。没有「特权内核」需要你去 patch。

这个内核叫 [Cordis](https://github.com/cordiverse/cordis)。设计思想写在论文 [A Programming Paradigm for Spatiotemporal Composability](https://arxiv.org/abs/2608.25512) 里，作者来自北大与 DeepSeek。名字很长，事情其实就两维：

- **时间上可组合**：插件卸掉时，它产生的副作用必须能撤销，不能留下孤儿监听、孤儿工具、孤儿提示词。
- **空间上可组合**：插件用依赖声明自己需要谁；对方还没来就等，对方走了自己也停。

落到运行时，就是两个很朴素的机制：每次注册都带着反向撤销函数；依赖变化会自动激活或停用插件。HMR（热更新）能干净生效，靠的就是这个，而不是「重启试试」。

## 一切皆插件

Cordis 里有五个概念，搞懂这五个，后面的 profile、bundle、patch 都只是组装方式。

**1. 插件是一个 Service。**  
它可以是带 `inject` 和 `apply(ctx)` 的函数，也可以是一个类。加载的时候，Cordis 把它挂进当前上下文。

**2. Context 是服务仓库。**  
一个服务占一个稳定的 `ctx.<key>`，比如 `ctx.tools`、`ctx.llm`、`ctx.sessions`。别人按 key 找，不 import 具体实现。所以换 DeepSeek 适配器还是换别的厂商，对 loop 来说都只是 `ctx.llm` 没变。

**3. `inject` 声明依赖。**  
你需要 `tools` 就写 `inject = ['tools']`。服务没就绪，插件不会启动。加载顺序由依赖图表达，不是手写 boot 序列。

**4. 用类型化事件通信。**  
不是到处 callback。服务声明事件名，再按模式分发：`emit` 观察一下，`waterfall` 当中间件可以短路，`serial` 按序等待，`parallel` 一起跑，`bail` 碰到第一个有效值就停。

**5. 注册是可逆的副作用。**  
提示词片段、工具 schema、适配器、监听器，都通过 `ctx.effect()` / `ctx.on()` 装上。插件卸载时按预期撤销。

一个极简插件大概长这样：

```ts
export const name = 'hello-tool'
export const inject = ['tools']

export function apply(ctx) {
  // effect 的返回值会在卸载时执行，这就是「可逆」
  ctx.effect(() => {
    const dispose = ctx.tools.register({
      name: 'hello',
      description: 'Say hello',
      execute: async () => ({ content: 'hello from a plugin' }),
    })
    return dispose
  })
}
```

虽然真实仓库里的工具还要过 schema、权限、沙箱、观测，但这个例子足以说明核心逻辑：**能力是挂上去的，不是写死的；挂上去的东西必须能摘下来。**

`waterfall` 特别值得单独说一句。它是环绕中间件：监听器拿到 `(args, next)`，调用 `next()` 才把请求传给下游。不调用就直接返回，等于短路。策略插件可以在这里拒绝一次危险的工具调用，观察插件则必须把 `next()` 传下去。Harness 里的 `agent/pre-step`、`llm/stream`、`tools/*` 都是这种事件。

一句话来总结 Cordis：

> Cordis 是插座板，插件是插头。插座板不管你插的是台灯还是冰箱，它只保证：插上能用，拔掉不留电。

## 四种运行模式

「一切皆插件」还有一个很实际的后果：所谓不同模式，并不是四套独立 Agent，而是同一棵树上装了不同的插件集。

| 模式 | 默认装什么 | 适合干什么 |
|---|---|---|
| **Standard** | 完整工具：文件、Shell、检索、Skills、规划、子 Agent | 日常编码、重构 |
| **PTC** | 几乎全套工具，但模型写一段代码来编排多轮调用 | 长链路任务，少跟模型来回聊天 |
| **Minimal** | 只留 shell + 文件编辑 | 模型基准、轻量任务 |
| **Creative** | 可检查当前运行时，内存里试插件，组新模式 | 开发、实验 |

PTC 全称 Programmatic Tool Calling，产品页上有时也叫 Code Mode。它很容易被理解成「另一种 Agent」，其实改的不是权限，是编排。

标准模式下，模型一轮调一个工具，调完看结果，再决定下一步——来回很多次。PTC 让模型对着一份生成出来的 SDK 写一小段程序，经 `run_code` 把多轮调用组合在一起。每一次真正的工具调用，仍然走同一条审批、沙箱、观测管线。也就是说：**模型陈述计划的方式变了，它被允许做什么没有变。**

想象你让助手去厨房做菜。标准模式是「拿盐」「好了」「拿锅」「好了」。PTC 是助手先写一张菜谱，再按菜谱连续做，但每一步仍要经过你定好的安全规则。

## 如何创建和使用

理论说到这里够了。下面是真正上手。

### 最快：一行命令打开 Web UI

需要 Node.js。

```sh
npx @deepseek-ai/dsh web
```

默认会在 `http://127.0.0.1:3080` 拉起页面，本机启动还会用默认浏览器打开。SSH 过去的话它只打印 URL，因为端口转发的地址归你的 SSH 客户端管。不想自动打开浏览器就加 `--no-open`。

然后三步：

1. 打开 **Settings → Models**，填入 [DeepSeek API Key](https://platform.deepseek.com/)，保存。模型路由立刻可用，不用重启。
2. 点 **Choose workspace**，选一个项目目录。注意：`dsh` 的启动目录只是默认文件系统位置，Web UI 必须你自己选一个 workspace，选完才能发消息。
3. 开一个 session，随便说一句：「Summarize this repository and identify its main packages.」

Agent 会开始读文件、跑命令、写计划。需要批准的操作会先问你。

### 从源码跑

想看实现、改插件，就不要只停留在 npx：

```sh
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pnpm install
pnpm run build
pnpm dsh web
```

`pnpm run build` 负责准备产物，`pnpm dsh web` 直接用这些产物，不会再编一次。

### CLI 的几种打开方式

`dsh` 不是一堆互不相干的可执行文件，而是通过 **named profile** 启动同一套运行时。

```sh
dsh web                               # Web UI
dsh --profile headless "修失败的测试"    # 跑一次，打印最终答案，退出
dsh --profile sdk                     # stdio 上的 JSON-RPC，给 SDK 用
dsh --profile sdk-minimal             # 极简 Agent 树
dsh --profile acp                     # ACP 协议，给自动化客户端
```

几个常用参数：

- `--profile <name>` 指定启动哪套组装
- `--from-default-profile <template>` 从出厂模板建一个自定义 profile
- `--patch` 再叠一层配置
- `--dump-config` 把实际组装出来的插件树打印出来，这是排错神器
- `--port 8080` Web 端口，这个参数由 profile 自己解析

默认 workspace 就是你敲 `dsh` 时的当前目录。数据落在 `$DSH_HOME`，一般是 `~/.dsh`。有一个例外下面马上会说：Python SDK **故意不自动发现** `~/.dsh`，必须你显式传入，免得一个脚本把你日常环境搞乱。

### 嵌进自己的程序：Python SDK

```sh
python -m pip install deepseek-harness-sdk
```

这个包会带上同版本、当前平台的 runtime wheel，里面就是 `dsh` CLI。Python 侧 **没有重新实现一遍 Agent**。它只是拉起 `dsh --profile sdk`，然后在 stdio 上用 newline-delimited JSON-RPC 对话。

前置条件：Python 3.10+；Linux x64/arm64、macOS 14+ arm64 或 Windows x64；一个 DeepSeek 兼容的 API；以及——隔离的 workspace 和隔离的 Harness home。

```python
from pathlib import Path
from deepseek_harness import DeepSeekHarness

workspace = Path("/abs/path/to/workspace").resolve()
dsh_home = Path("/abs/path/to/isolated-dsh-home").resolve()

with DeepSeekHarness(
    provider="deepseek-official",
    model="deepseek-v4-flash",
    max_tokens=49_152,
    cwd=str(workspace),
    dsh_home=str(dsh_home),
    profile="sdk-minimal",
) as harness:
    result = harness.run(
        "Inspect the repository and fix the failing tests.",
        session_id="example-001",
    )

print(result.final_response)
```

`DeepSeekHarness` 是懒启动的，进了 context manager 才拉 runtime，退出才关掉。首次握手默认 30 秒超时，普通一轮对话默认不限时。

命令行示例也有：

```sh
python python/sdk/examples/minimal.py \
  --workspace /abs/path/to/workspace \
  --dsh-home /abs/path/to/dsh-home \
  --session-id example-001 \
  "Inspect the repository and fix the failing tests."
```

一句话来总结 SDK：

> Python 不是另一个 Agent，它只是同一棵插件树的遥控器。遥控器在 Python，发动机仍是 Node 里的 `dsh`。

### 装插件、换能力

插件用 pnpm 装进某个 profile：

```sh
dsh plugin --profile web add <某个-dsh-plugin>
```

社区发现话题是 [dsh-plugin](https://github.com/topics/dsh-plugin)。

真正让「不改源码也能换能力」成立的，是配置的叠法。一次运行的 `dsh` 等于启动时按层叠出来的插件树：

1. profile 列出的每个 bundle 的 patch
2. 该 profile 自己的 `cordis.patch.yml`
3. `$DSH_HOME/cordis.patch.yml`
4. 命令行 `--patch` overlay

每一行按 **id** 整段替换或插入。想看你这台机器实际启动了什么：

```sh
dsh --profile web --dump-config
```

打印出来的任意一行，都可以被你自己的 patch 换掉。Web profile 默认开了 HMR，改 YAML 会热重载；headless / sdk / acp 默认关掉，避免一次任务跑到一半插件树变了。

出厂模板大概是这样分工的：`dsh-base` 提供模型、工具、持久化、沙箱、凭据这些底座；上面再叠 `dsh-web-app`、`dsh-headless`、`dsh-sdk-app`、`dsh-acp-app`。有一个例外：`sdk-minimal` 是独立完整的一棵树，不经过 `dsh-base`，专门给最小环境用。

换模型也是同一套路。写一个适配器，继承 `LlmAdapter`，实现 `stream()`：把 Harness 的中立请求翻译成厂商 API，再把响应翻回统一的 `StreamChunk`。仓库里已经有 `packages/llm/llm-deepseek/` 和 `packages/llm/llm-pi-ai/` 可以对照。然后在配置里把 provider / model 指过去就行。

## 底层是怎么跑完一轮的

会用之后，值得往下看一层。否则「一切皆插件」很容易停在口号。

### 两个时间单位：Turn 和 Step

Harness 把一次对话拆成两级：

- **Step**：一次模型请求，加上它调用的那些工具
- **Turn**：零个或多个 Step。领到第一条输入之前打开，没有任何未完成工作时关闭

简化成伪流程就是：

```text
turn/start
  领取下一条输入
  组装 prompt + 工具 schema
  -> agent/pre-step          拒绝，或者放行
     step/start
     准备模型调用
     从日志投影出模型能看见的历史
     llm/stream              流式输出
     若有 tool/call
        tools/pre-execute    策略、守卫
        tools/execute
        tools/post-execute
     step/end
     还欠一次模型请求？或者又来了新输入？ -> 下一个 step
  -> agent/turn-stopping
turn/end
```

`agent/created` 是串行事件：初始化失败会回滚，不会留下半残 Agent。`agent/pre-step` 这类 waterfall 可以在第一步就拒绝，于是这一轮一个 step 都不开。取消不会把 system / user message 提交进日志——模型没看见的东西，就不该假装看见过。

### 三种事件，别用错域

这是改 Harness 时最容易走错的一步。事件分三个域：

- **Session 事件**：持久事实，追加进日志。跨 reload 还得活着的东西走这里，比如 `user/message`、`assistant/message`、`tool/result`。
- **Agent 事件**（`agent/*`）：活着的 Agent 的 inbox、step、状态。用来观察或拦截正在进行的工作。
- **Capability 事件**（`fs/*`、`tools/*`、`telemetry/*`）：给某个能力缝挂策略，不必 import 主循环。

有一条不变量，值得记住：

> 模型可见的数据，必须作为事件落盘。

恢复、分叉、检索、回放，用的是同一条事件流。日志是 JSONL，可压缩成 zstd，文件名类似 `session.jsonl` 或带版本的 `session.vN.jsonl`。投影函数 `deriveMessages()` 再把事件折成模型上下文。失败和重试记在 `assistant/attempt` 里，不会把一次失败伪装成一次成功回复。

这就是官网说的第二句话：**每一次运行都可追溯。**

### 能力缝：换掉一块，其它跟着走

「Seam」听着抽象，其实就是：定义一个接口，一边是 provider，一边是 consumer。换 provider，所有 consumer 自动走新实现。

几个最常用的：

| 你以为的能力 | 实际挂在 | 换它意味着什么 |
|---|---|---|
| 模型 | `ctx.llm` | 换厂商、换本地模型、甚至换成回放器做测试 |
| 工具注册与执行 | `ctx.tools` | 工具调用统一过策略 → 守卫 → 分派 → 后处理 |
| 文件系统 | `ctx.fs` | 本地、沙箱、SSH，对 `tool-fs` 都一样 |
| 命令执行环境 | `ctx.sandbox` | 消费者交出即将 spawn 的 argv，后端按策略包装 |
| 会话 | `ctx.sessions` | 只追加的事件流，谁都不能改历史 |
| 主循环 | `ctx.agentLoop` | 连「怎么思考」都可以换 |

`ctx.tools` 尤其不是一个字典。一次工具调用会依次经过：策略前处理 → 单调守卫 → 环绕分派 → 策略后处理 → 结果观测。PTC 里模型写的代码，每一枪也走这条管线。所以 PTC 再怎么「写程序」，也跳不出你配置的权限。

### 和传统框架比一下

最后来一个简单的对比。

| 维度 | 典型编码 Agent 产品 | DeepSeek Harness |
|---|---|---|
| 定位 | 成品产品 | 可组装的运行时 |
| 模型 | 大多绑死或有限切换 | `ctx.llm` 上的一个插件 |
| 主循环 | 核心代码 | 也是插件 |
| 扩展方式 | fork / 官方 hook | 挂插件 + YAML patch |
| 卸载 | 经常留下状态 | 注册可逆，卸载即撤销 |
| 可追溯性 | 各家日志格式不同 | 统一追加式会话事件流 |
| 嵌入方式 | 通常就是那个 App | Web / headless / SDK / ACP / Desktop 同一套树 |

* **产品型 Agent 的优势**：开箱即用，体验打磨过，适合直接干活。
* **Harness 的优势**：能力可替换，运行可追溯，适合你要自研、要评测、要把 Agent 嵌进自己的系统。

它现在还是开发者预览。核心插件和 API 会继续变。把它当成「今天就能替换 Claude Code 的成品」会失望；把它当成「Agent 操作系统的开源底座」就对了。

## 实际使用时要注意的

第一，隔离。Agent 能读文件、跑命令。SDK 场景尤其不要指向你的日常 `~/.dsh` 和重要仓库，给它一次性的 workspace 和 home。

第二，它默认面向 DeepSeek 兼容 API，文档示例是 `deepseek-v4-flash`。其它 OpenAI-compatible endpoint 也可以接，再不行就自己写 adapter。

第三，Desktop 是 Electron 套了一份签过名的生产 runtime，独占 `$DSH_HOME/profiles/desktop`。公共 CLI **不能**管理这个 profile。默认端口是 `19387`。数据可以和 CLI 共享，包和 lockfile 是分开的。

第四，反馈走 [GitHub Discussions](https://github.com/deepseek-ai/deepseek-harness/discussions)。想写插件，先读文档里的 Cordis Primer，再看 cookbook：加一个包、加一个工具、接一个 LLM adapter，这三篇够你入门。

## 总结

回到开头那句公式。模型是灵魂，Harness 是手脚、记忆和纪律。DeepSeek 把后半段开源，并且做到了三件少见的事：

1. **内核不承载能力**。Cordis 只管理加载、卸载和依赖，具体本事全在插件上。
2. **用配置组装，而不是改源码**。profile、bundle、YAML patch 叠成一棵树，`--dump-config` 能把这棵树摊开给你看。
3. **模型看见的一切都落盘**。恢复、分叉、检索、回放共用同一条事件流。

你可以一行命令打开 Web UI 试试手感，也可以把 Python SDK 嵌进自己的流水线，还可以只留下 shell 和文件编辑去跑模型基准。不管哪种打开方式，底下都是同一棵可拆的插件树。

灵魂再强，没有手脚也走不远。Harness 要解决的，就是让手脚能换、能卸、并且每一步都留得住痕迹。