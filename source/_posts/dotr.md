---
title: 配置文件的保险箱：dotr
tags: [dotfiles, 配置备份, 配置管理, 备份工具, rust]
date: 2026-09-20
categories:
  - [工具]
---

配置备份是一个非常常见的需求。用了十几年电脑的人，多半都踩过一次：某天机器开不了机，或者一条命令把 `.zshrc` 覆盖了，然后发现真正重要的东西并不在 Git 里，而在 home 目录那些说不清该不该提交的文件里。

<!-- more -->

网上关于 dotfiles 的资料非常多。chezmoi、yadm、GNU Stow、自己写的 symlink 脚本，几乎每个人折腾过一套。但这些工具大多在做一个更重的事情：**把你的 home 目录变成一套可部署的配置系统**。模板、条件渲染、跨机器 bootstrap、secret manager——都很完整，也都很重。

[dotr](https://github.com/chenyukang/dotr) 走的是另一条路。作者 [chenyukang](https://catcoding.me/p/dotr-intro/) 自己的原话更直接：需求偏「备份」，不是「配置部署系统」。很多时候你只是想：这个文件对我有用，把它安全地放进一个 Git 仓库里，以后坏了能找回来。

本文不是工具说明书的翻译，而是把它的思想、用法和底层实现放到一起讲清楚。读完你应该能回答三件事：它和 chezmoi 差在哪、你怎么把它跑起来、它凭什么敢把 restore 做成默认保守。

## 前言

由于本文会落到命令、配置和备份流水线，建议你对 dotfiles 有一点直觉：知道 `~/.zshrc`、`~/.gitconfig`、`~/.config/nvim` 这些东西在哪，知道 Git 仓库是什么。如果你连这些都不熟，先备份一次自己的 shell 配置再回来看，会轻松很多。

本文会夹一点 TOML 和命令行。语法都不难，相信我它真的很容易懂。crate 名叫 `dotr-cli`，装完命令是 `dotr`：

```sh
cargo install dotr-cli
```

macOS / Linux 也可以：

```sh
curl -fsSL https://raw.githubusercontent.com/chenyukang/dotr/main/install.sh | sh
```

默认装到 `~/.local/bin`。工具是 Rust 写的，MIT 协议。目前还很年轻，别把它当成十年老牌 dotfiles 方案的替代品，当成一把专门备份配置的小锤子更合适。

## 学习建议

文里会给出能直接跑的命令。强烈建议你开一个隔离目录，比如 `~/dotbackup-playground`，边看边敲。只有动手才可能真正理解：为什么源文件还在原地、为什么 restore 默认不写盘、为什么 Git 历史不会因为一个时间戳字段而吵个没完。

尽可能按思路默写配置，而不是把别人的 `dotr.toml` 整份抄过来。配置备份这件事，抄错一个 `include`，就把缓存和 token 一起提交了。

---

作者是这么定义的：

> 把你指定的文件和目录复制到一个 Git 仓库里，同时保存一份 metadata，方便以后 restore。

一句话来总结 dotr 是什么：

> 它不是配置部署系统，是一台复印机。源文件仍在原来的位置，dotr 只负责按清单复印进保险箱，并且默认不允许你随手把保险箱里的东西盖回原处。

## 什么是 dotfiles 工具，以及为什么很多人用错了

在讲 dotr 之前，我们先看看和它很像、也最容易被拿来对比的东西：**dotfiles 管理器**。这对我们理解 dotr 很有帮助。

所谓 dotfiles，顾名思义，就是 home 目录下那些以点开头的配置：`.zshrc`、`.vimrc`、`.gitconfig`。后来应用把配置塞进了 `~/.config`，名字还叫 dotfiles，习惯而已。

常见方案大致三类：

1. **手工 Git 仓库**：把文件复制进去，或者在仓库里维护一份，再用脚本拷回来。简单，但路径、过滤、加密全靠人。
2. **symlink 管理器**（Stow 这类）：仓库是真身，home 里是软链。好处是改一处两边通；坏处是你的家目录被工具接管了，某次操作失误，真实配置可能直接指向一个半残仓库。
3. **配置部署系统**（chezmoi、yadm）：模板、主机差异、secret、bootstrap 脚本。跨三台机器、公司电脑和个人电脑，这套很强。但你每加一个文件，都要思考它该如何被管理。

dotr 明确不做第 3 类。它甚至默认不做第 2 类。它更接近把第 1 类做成一个守规矩的工具：你列出想备份的东西，它定期复制到仓库。源文件仍然是源文件，仓库里是副本。

想象一下装修。chezmoi 像是把整个家改造成智能家居：灯、门锁、窗帘全部接入中控。dotr 只是给户口本、合同、钥匙复印件做了一只保险箱。家还是原来的家，坏了能找回来就行。

所以它能干什么，其实很具体：

| 你想做的事 | 对应用法 |
|---|---|
| 把若干配置放进 Git | `dotr add` + `dotr backup` |
| 看看这次会备份什么 | `dotr status` |
| 机器坏了，把某个文件找回来 | `dotr restore --apply` |
| 文件里有 token，仓库还想推远程 | `dotr add --encrypt` |
| 懒得每次手动 backup | `dotr watch` / `dotr daemon start` |
| Homebrew 包列表这种「导出才有文件」 | `[[custom_backup]]` |

作者写它的契机很朴素：一条命令把 `.zshrc` 覆盖了；后来 Mac 在外地开不了机，从 GitHub 私有库把备份拉下来，再交给 AI 帮着恢复。工具本身不追求「一键在新电脑上重建人生」，它只保证：**你列过的东西，仓库里有一份能还原的副本**。

## 核心思路：复制，而不是接管

dotr 的仓库结构大概长这样：

```text
dotr.toml
files/
  home/
    .zshrc
    .config/nvim/init.lua
metadata/
  index.json
```

路径映射是直接且可逆的：

```text
~/.zshrc
=> files/home/.zshrc

/Library/example/hello/world
=> files/root/Library/example/hello/world
```

`$HOME` 底下的进 `files/home`，home 之外的绝对路径进 `files/root`。`files/root` 是懒创建的，你真的备份了绝对路径才会出现。

这个设计看起来朴素，但作者说他挺喜欢。它没有要求真实文件必须变成 symlink，也不要求原来的目录结构去适配工具。源文件仍在原地，dotr 只是按配置把它们复制进备份仓库。

一句话来总结这个映射：

> `files/home` 就是 `$HOME` 的复印件，`files/root` 就是 `/` 的复印件。metadata 负责记住复印件自己说不清的事：权限、是不是加密、对应哪条源路径。

## 配置要短，过滤要狠

dotfiles 备份最麻烦的地方，不是 Git，是每个应用目录都不一样。有的目录里只有配置，有的目录混着缓存、session、数据库、token、日志和临时文件。粗暴备份整个 `.config`，基本等于把垃圾一起提交了。

所以 dotr 的配置主要围绕 `[[path]]` 和 `[[path_set]]`：

```toml
[[path_set]]
base = "~"
items = [
  ".gitconfig",
  { src = ".config/nvim", include = ["init.lua", "lua/**", "after/**"] },
  { src = ".config/some-app", include = ["config.toml", "assets/**"], include_binary_file = true },
]
```

`path_set` 是为了让 home-relative 的常见配置写起来更短。字符串等价于 `{ src = "..." }`，table 则可以继续加 `include`、`exclude`、`encrypt`、`force` 这些字段。相对路径会拼到 `base` 上；写了 `~` 或绝对路径，则忽略 `base`。`include` 是相对于 `src` 的。

默认策略会跳过缓存、日志、本地数据库、session、build output、临时文件、`.env`、私钥之类的东西。二进制默认也不进仓库，除非你显式写 `include_binary_file = true`。如果一个目录里只有几个文件值得备份，更推荐显式写 `include`，而不是整个目录打包。

`force = true` 会绕过默认排除、二进制检测和文件大小上限，仍然尊重你写的 `include` / `exclude`。它是给「我知道这是日志，但我就是要这份日志」用的，不是给偷懒用的。

这个取舍很重要：dotr 不帮你猜秘密的边界，也不帮你猜哪个目录「看起来像配置」。猜错比漏备份更危险。

## 如何创建和使用

理论说到这里够了。下面是真正上手。

### 初始化一个保险箱

```sh
dotr init ~/dotbackup --with-defaults --set-default
```

`--with-defaults` 会写一份通用的 starter 配置：shell、Git、SSH、GPG、编辑器、prompt、终端、Homebrew、VS Code 这些常见路径。它 **不会** 迁移你现有的 chezmoi / yadm 仓库，也不会把当前 home 目录吞进去。

`--set-default` 在本机写下 `~/.config/dotr/config.toml`：

```toml
default_repo = "/Users/alice/dotbackup"
```

这份用户配置是机器本地的，不要提交进备份仓库。写过之后，`dotr backup`、`dotr restore` 从哪个目录跑都可以。

仓库是这样找的，按优先级：

1. `--repo` 或 `-C`
2. 环境变量 `DOTR_REPO`
3. 从当前目录往上走，直到看见 `dotr.toml`
4. `~/.config/dotr/config.toml` 里的 `default_repo`

找不到就直接报错，告诉你怎么传 `--repo`。不会默默挑一个看起来像的目录开干。

### 日常就这几条命令

```sh
dotr status
dotr backup
dotr add ~/.config/yazi
dotr restore --diff ~/.ssh/config
dotr restore --apply ~/.zshrc
```

`status` 本质上是一次 dry-run backup：扫描配置里的源，比较当前文件和仓库里的备份，告诉你会新增、修改、删除什么。`backup` 才真正把变化写进去。

`dotr add` 会改 `dotr.toml`，并且顺手跑一次只针对这条路径的备份：

```sh
dotr add ~/.config/yazi
dotr add --encrypt ~/.npmrc
dotr add --force /Library/Logs/MCXTools.log
```

如果这次 add 实际不会备份任何东西——比如被默认规则全部跳过——它会失败，并提示你 `dotr add --force PATH`。而不是悄悄写一条无效配置进 `dotr.toml`，让你三个月后才发现仓库里根本没有这个文件。

对应的，`dotr remove ~/.config/yazi` 会从配置里拿掉，并立刻删掉对应备份。

### restore 默认保守

备份工具还有一个危险操作：恢复。一次错误覆盖，可能让一个环境很难排查。

dotr 的 restore **默认是 dry-run**，必须加 `--apply` 才会写回原位置：

```sh
dotr restore ~/.zshrc          # 只预览
dotr restore --apply ~/.zshrc  # 真正恢复
```

如果目标文件已经存在，而且内容和备份不同，默认不会覆盖，除非再加 `--force`。只是想把某个加密文件临时解出来看看，用 `-o` 输出到别处，这个不需要 `--apply`，因为它根本不碰原位置：

```sh
dotr restore -o /tmp/ssh-config ~/.ssh/config
```

`$HOME` 之外的绝对路径更严，必须 `--apply` 和 `--allow-absolute` 同时给：

```sh
dotr restore --apply --allow-absolute /Library/example/hello/world
```

作者自己写这类工具时很在意「危险动作」：backup 可以勤快一点，restore 应该慢一点。SPEC 里还有一句更硬的：**`dotr watch` 永远不会 restore**。自动备份可以，自动把文件盖回去不行。

### 文件里有秘密，怎么办

很多配置会混进 token、内部 URL、账号名、私有 endpoint。仓库如果要推到远程，这些东西就很尴尬。

dotr 支持对单个 path 显式开启 [age](https://age-encryption.org/) 加密：

```sh
cd ~/dotbackup
dotr keygen
dotr add --encrypt ~/.npmrc
```

它没有去调系统里的 `age` 命令，而是直接用 Rust 的 age 实现做 keygen、backup 和 restore。`recipients` 是公钥，可以进仓库；`~/.config/dotr/identity` 是私钥，必须像密码一样保存，不能提交。

对应配置大概是：

```toml
[encryption]
backend = "age"
recipients_file = "recipients"
identity = "~/.config/dotr/identity"

[[path]]
src = "~/.npmrc"
encrypt = true
```

加密后的文件会带 `.age` 后缀：

```text
~/.config/some-app/token.json
=> files/home/.config/some-app/token.json.age
```

`index.json` 里仍记录明文路径，但明文内容不会进仓库。

dotr **不会自动猜**哪些文件该加密。秘密的边界很难可靠推断，自动猜错反而危险。它只提供机制：你明确说这个 path 要加密，它才加密。

还有一个很多人会忘的坑：如果一个 secret 已经以明文进过 Git 历史，后来把 `encrypt = true` 打开，只能保护未来的备份文件，不能让历史记录自动消失。该 rotate 的还是要 rotate，该改写历史的还是要改写。

### 去掉那些「每次都会变」的噪音

现实里的配置经常有一些每次运行都会变、但毫无备份价值的字段：时间戳、计数器、last refresh、last seen。它们一变，Git 历史就吵。

dotr 支持对匹配到的文件做 **只用于比较的 normalize**：

```toml
[[path]]
src = "~/.config/some-app"
include = ["config.toml"]
normalize = { match = "config.toml", drop_paths = ["runtime.last_updated"] }
```

关键点是 compare-only：不改源文件，也不把仓库里的备份改成删过字段的版本。它只是在算 hash 做比较时，先把指定字段 drop 掉。如果只有这些字段变了，backup 认为没必要写新版本；如果后来真正的配置字段变了，dotr 仍然会复制当前这份原始文件。

目前能识别 TOML、JSON、txt、conf。TOML/JSON 可以按 dot path 删字段，`*` 匹配一层对象：

```toml
drop_paths = ["marketplaces.*.last_updated"]
```

它不能和 `encrypt = true` 一起用。原因很实际：加密备份比较的是密文，比较阶段不该去解析明文。

### 忘掉手动 backup：watch 和 daemon

如果只靠手动跑 `dotr backup`，最后大概率会忘。所以有 watch：

```sh
dotr watch
```

它监听配置里的 source path，做 debounce，再按 `backup_interval_secs` 控制频率。也可以丢到后台：

```sh
dotr daemon start
dotr daemon status
dotr daemon restart
dotr daemon stop
```

这里没有做 systemd unit，也没有 launchd plist。`dotr daemon start` 会解析 repo，写一份用户级 daemon 配置，记下当前的 `dotr` 可执行文件和仓库路径，然后在后台启动 `dotr --repo <repo> watch`。日志默认在：

```text
~/.local/state/dotr/dotr-watch.log
```

注册完监听之后，它会先跑一次完整 backup。这是为了补上 daemon 停着的那段时间里发生的改动。之后由 watch 触发的备份，才缩小到变化过的路径。

### 有些东西根本不是现成文件

Homebrew 包列表、VS Code 扩展列表，这些不是「磁盘上已经有一份配置」，而是「跑一条导出命令才会生成文件」。dotr 用 `[[custom_backup]]` 描述这种关系：

```toml
[[custom_backup]]
name = "homebrew"
backup = "brew bundle dump --file ~/.config/homebrew/Brewfile --force"
restore = "brew bundle --file ~/.config/homebrew/Brewfile"
paths = ["~/.config/homebrew/Brewfile"]
```

backup 前先跑 `backup` 命令，生成文件后再扫描；restore 时文件恢复后再跑 `restore` 命令。dry-run 只打印命令，不执行。这样你就不用再维护一份外面的 bootstrap 脚本，备份关系写在 `dotr.toml` 里就行。

如果开启 Git 自动提交：

```toml
[git]
auto_commit = true
auto_push = false
commit_message = "chore(dotr): automated backup"
```

dotr 只会 stage 自己管理的路径：`dotr.toml`、`files/`、`metadata/`、`recipients` 和 `.gitignore`。这个细节很重要。备份仓库里可能还有你手工放的 README，工具不应该顺手把你没准备好的东西一起提交。如果发现 staged 区里已经有非 dotr 路径，它会直接失败，而不是偷偷帮你提交。

## 底层是怎么跑完一次 backup 的

会用之后，值得往下看一层。否则「复制进 Git」很容易停在口号。

源码都在 `src/` 下一层：`backup.rs`、`restore.rs`、`normalize.rs`、`encryption.rs`、`watch.rs`、`git.rs`……没有很深的包结构。SPEC 把流水线写得很直。

一次 backup 大致是：

```text
1. 读 dotr.toml
2. 先跑 custom_backup.backup（dry-run 除外）
3. 解析 [[path]] / [[path_set]] / custom 的 paths
4. 遍历每个源
5. 套默认排除 + 路径级 exclude
6. 套路径级 include
7. 二进制默认跳过
8. 拒绝无法安全映射进 files/ 的路径
9. 和现有备份比较（有 normalize 就先 drop 再比）
10. 复制新增和变更
11. 源已经消失的备份，删掉（除非 --no-delete）
12. files/ 里的孤儿文件，删掉
13. 写 metadata/index.json
14. 有变化且开了 auto_commit，再 git commit / 可选 push
```

`metadata/index.json` 记的是复印件自己说不清的事，结构大概是：

```json
{
  "version": 1,
  "entries": [
    {
      "source": "~/.zshrc",
      "stored": "files/home/.zshrc",
      "kind": "file",
      "sha256": "...",
      "mode": 420,
      "executable": false,
      "encrypted": false
    }
  ]
}
```

比较用的是内容 hash，不只看 mtime。内容没变、只是被重写了一遍的文件，不会当成一次变更，`index.json` 里的旧条目会保留。权限、可执行位这种「耐久元数据」变了，则仍然会记下来。

加密文件是例外：密文阶段看不到明文 hash，所以退而用 size + mtime 做保守的变更信号。这也是为什么 encrypt 和 normalize 互斥——一个要看明文结构，一个故意不看明文。

restore 这一侧更严：

- 默认 dry-run
- 目标内容不同就拒绝覆盖，除非 `--force`
- home 之外必须 `--allow-absolute`
- 创建缺的父目录
- 恢复可执行位
- symlink 按 symlink 恢复，而不是展开成普通文件
- 匹配文件写回去之后，再跑对应的 `custom_backup.restore`
- stored 路径必须归一化在 `files/home` 或 `files/root` 下，带 `..` 的直接视为非法，防止借 symlink 写出映射根之外

watch 则是同一条 Rust backup 流水线套了文件系统监听：

1. 监听配置里的源路径
2. 注册完先跑一轮完整 backup，补上停机期间的变化
3. 忽略命中 exclude 的事件
4. 突发变更做 debounce
5. 拿进程锁
6. 跑和 `dotr backup` 相同的流水线
7. 用 `backup_interval_secs` 限频
8. 备份仓库自己的变化默认忽略，免得自己写 files/ 把自己唤醒
9. custom_backup 刚写出的文件，会短暂忽略，防止自触发死循环

Git 在 v0 里可以 shell 出去调系统的 `git`，这样你现成的 SSH credential 还能用。但扫描、比较、加密、restore、watch 调度这些必须留在 Rust 里。Git 被挡在一层接口后面，以后换成 `gix` 也行。SPEC 写得很明确：这不是一个套了 Git 的 shell 备份脚本。

虽然真实实现里还有进度输出、结构化日志、doctor 检查这些边角，但上面这条流水线足以说明核心逻辑：**所有聪明都花在「复制哪些、比较什么、什么时候准写回去」上，而不是花在模板引擎上。**

## 和已有工具比一下

最后来一个简单的对比。

| 维度 | chezmoi / yadm 这类 | dotr |
|---|---|---|
| 定位 | 配置部署系统 | 复制式备份工具 |
| 源文件 | 常被仓库/软链接管 | 仍在原地 |
| 跨机器差异 | 模板、条件、profile | 基本不管，恢复后交给你或 AI |
| 秘密 | 常接 secret manager / 模板 | 你显式标记，才走 age |
| 默认动作 | deploy 到目标机 | backup 进仓库；restore 默认只预览 |
| 自动 | 各家 hook / 定时自己做 | watch / daemon，且 watch 绝不 restore |
| 噪音 | 靠模板或忽略规则 | compare-only normalize |
| 适合谁 | 多机器、要一键重建环境 | 想先有一份能找回来的副本 |

- **chezmoi 的优势**：跨机器、模板、bootstrap 完整，适合把环境当成产品来发布。
- **dotr 的优势**：心智负担小，危险动作慢，过滤和加密都是显式的。适合「这台机器上的配置别丢」而不是「三台机器保持同一套生成结果」。

作者自己也说了：如果你需要跨机器模板、条件渲染、复杂 bootstrap、secret manager 集成，那些成熟工具可能更适合。就他那次 Mac 寄修的实际体验而言，把备份交给 AI 恢复更方便，AI 还能顺手处理一些跨平台问题。dotr 负责把材料备齐，不负责当你的运维平台。

## 实际使用时要注意的

第一，仓库可以是私有的，但私有不等于可以塞明文私钥。`~/.ssh/id_rsa`、GnuPG 私钥这类东西，没有单独的恢复和轮换方案，就不要备份。token 类小文件用 `--encrypt`。

第二，默认排除名单很长，`.env`、`*.pem`、`*.key`、`*.db`、`node_modules`、各种 cache / session / log 都会被跳过。你真要备份其中某个文件，用 `--force` 或路径级 `force = true`，并且心里有数。

第三，二进制默认跳过，文件大小默认上限 `20MiB`。应用目录里那堆资源文件，不要指望「备份整个目录就完了」。

第四，symlink 默认 **follow**，复制的是目标内容。如果你就是要保存「这是一个软链」这个事实，设 `follow_symlink = false`。

第五，`dotr check`（`doctor` 是兼容别名）值得在 CI 或定期跑一下。只要配置里有 `encrypt = true`，它会检查 `recipients` 是否存在且是合法的 age recipient。

第六，这是个人向小工具，不是十年稳定的基础设施。接口和默认策略还可能变。先用隔离仓库试，再指向你真正的配置。

## 总结

回到开头那句话。很多人丢配置，不是因为没有 Git，而是因为 Git 被用成了错误的抽象：home 目录既不能整棵提交，也不该被一套模板工程接管。

dotr 做了三件少见的、也足够小的事：

1. **源文件不动**。它是复印机，不是搬家公司。
2. **过滤和加密都是显式的**。不猜秘密，不整目录盲备；你点名的才进仓库，你点名加密的才加密。
3. **backup 勤快，restore 保守**。watch 可以自动复印，但永远不会自动把复印件盖回去。

你可以一行 `dotr init` 开始，用 `status` 看它打算干什么，确认后再 `backup`。哪天机器真的开不了机，至少你还有一份带 metadata 的 Git 仓库，而不是一个「好像曾经备份过」的模糊印象。

家不用先改成智能家居，才有资格拥有保险箱。配置也一样。