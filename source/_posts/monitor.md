---
title: [RFC]XX公司监控平台需求和技术调研
tags: [RFC]
---

## 背景

线上问题回溯困难，无法快速准确重现问题，导致客户满意度下降，影响团队交付效率和质量。

## 需求
期望有一套工具，系统或者平台，可以满足：

1. 在收到用户反馈的时候能够快速重现问题并解决。
2. 测试同学发现问题，不需要花费大量事件和开发人员重现，沟通，以及记录问题重现路径等
3. 线上发现问题可以进行告警，防止大规模用户有问题，并且不能及时感知和解决。
4. 缩短团队内部BUG修复的闭环流程，减少非本质复杂度问题的干扰，快速将问题聚焦到具体的代码。


带着上面的需求，我们来看下市面上已有的经典方案， 在这里挑选几个具有代表性的。

<!-- more -->
## 市面上已有的方案对比

### LogRocket

一句话概括： 用看录像的方式重现问题。

官网地址： https://logrocket.com/

#### 特点

![](https://tva1.sinaimg.cn/large/006y8mN6ly1g8w8nsefw6j31ji0braaj.jpg)

![](https://tva1.sinaimg.cn/large/006y8mN6ly1g8w8mp9lp5j31bc0qr410.jpg)

![](https://tva1.sinaimg.cn/large/006y8mN6ly1g8w8myz28pj31su0u0ta3.jpg)

更多功能： https://docs.logrocket.com/docs


#### 接入方式

![](https://tva1.sinaimg.cn/large/006y8mN6ly1g8w8kqmquvj313k0opwfb.jpg)

#### 价格

![](https://tva1.sinaimg.cn/large/006y8mN6ly1g8w8lgqwlgj30rg0n3wf0.jpg)

### Sentry

一句话概括： 开源，强大的监控平台。

官网地址： https://sentry.io/

#### 特点

功能较多，提供了较多的概念和功能，比如Context，ENvironments，Breadcrumbs等。另外其和CI，CD集成地也非常好。 详细内容： https://docs.sentry.io/workflow/releases/?platform=node

另外其支持的平台和扩展功能非常多，如果对这部分有特殊要求，Sentry无疑是优先考虑的选择。

#### 接入方式

- Sign up for an account
- Install your SDK
```bash
# Using yarn
$ yarn add @sentry/node@5.8.0
```
- Configure it
```js
const Sentry = require('@sentry/node');
Sentry.init({ dsn: 'https://<key>@sentry.io/<project>' });
```


#### 价格

![](https://tva1.sinaimg.cn/large/006y8mN6ly1g8w8qipkskj30x10jt758.jpg)

### FunDebug

一句话概括：国内知名度较高的监控工具，国内业务这块很有竞争力。

https://www.fundebug.com/

#### 特点

支持小程序，小游戏。多种现成的报警方式，支持WebHook，智能报警（同样的代码产生的同一个错误，在不同浏览器上的报错信息是各不相同的），内置团队协作工具。

#### 接入方式

这里以Vue项目为例。

1. 免费注册

2. 创建项目

3. 配置

```bash
npm install fundebug-javascript fundebug-vue --save

```

```js
import * as fundebug from "fundebug-javascript";
import fundebugVue from "fundebug-vue";
fundebug.init({
    apikey: "API-KEY"
})
fundebugVue(fundebug, Vue);
```


#### 价格

![](https://tva1.sinaimg.cn/large/006y8mN6ly1g8w9mhtq44j30x60mb3z3.jpg)

## 其他后期可能功能点

1. 性能监控

2. 用户行为监控（已经有埋点，不不确定是否可以Cover这个需求）


## 自研

假设我们已经做好了我们自己的监控平台，我们需要对公司内部甚至外部宣传我们的监控平台，我们会怎么进行宣传。

然后带着这些东西，我们进行规划，技术选型，排期，写代码，测试，上线。


### 宣传语

1. 接入方便，侵入性小
2. 支持多端，扩展性强（支持多种框架定制接入），完美契合业务发展
3. 打通客服系统，开发直接对接到客户，免去了中间对接的信息缺失和时间损耗。
4. 重现率高，能够准确重现用户的现场情况
5. 打通报警系统
6. 打通调试平台
...


### 优劣分析

#### 优势

完美契合我们自身的业务，后期好维护和增添功能

#### 劣势

如果功能需要做的超出市面，需要耗费巨大的人力和财力。

如果市面上不断发展，功能不能断完善，内部如果想要这样的功能要么继续追赶，要不买一套商用的，但是之前的努力岂不是白费了。除非内部两套系统，但是这种模式未免太反直觉。

### 架构与选型

对外都宣传完了，我们需要具体开始进行架构与选型了。

#### 定义对外接口

我们对外宣传的目标是`接入方便，侵入性小`。因此一定要简洁，这里参考了以上几个平台的写法，其实这几个平台的都是大同小异。


1. 注册应用获取AppId
2.  安装
```bash
npm i --save @lucifer/monitor
```
3. 引用
```js
import monitor from '@lucifer/monitor'
monitor.init({
    user: {
        name: '',
        email: '',
        mobile: '',
        isVIP: true
    },
    appId: 'lucifer520'
})
```
4. 多端和多框架支持

Vue：
```js
import Vue form 'vue';
import monitor from '@lucifer/connectors/vue';
monitor.init({
    user: {
        name: '',
        email: '',
        mobile: '',
        isVIP: true
    },
    appId: 'lucifer520'
})
monitor.use(Vue)
```

Wechat：

```js
import monitor from '@lucifer/connectors/wechat';
monitor.init({
    user: {
        name: '',
        email: '',
        mobile: '',
        isVIP: true
    },
    appId: 'lucifer520'
})
```



#### 定义内部接口

架构图：

![](https://tva1.sinaimg.cn/large/006y8mN6ly1g8xj6xnibej30xd0hzgo5.jpg)

接口系统交互图会在详细设计中给出，这里只给出大致范围：

- logs服务器和告警平台的交互接口
- rules的规则解析
- logs的解析
- 构建系统对接
- 调试系统对接
- ...



#### 业务形态特点

- 数据量会随着采集规模增大而增加，因此预估用户数量以及增长速度对系统架构设计有很大影响
- 终端的上报策略对影响很大，断网，弱网等情况如何上报也对结果有影响


#### 框架选型 & 规范 & 约定

省略