---
title: 前端测试最佳实践（持续更新，建议收藏）
tags: [前端, 测试, 单元测试, vue]
categories:
  - [前端, 测试]
---

最近公司在推行单元测试，但是一些同事对于单元测试只是了解，甚至不怎么了解。因此推动单元测试的阻碍是有的，这种阻碍除了人的层面，还有基础设施的层面。希望通过本文，一方面加深大家对前端测试最佳实践的认知，另一方面可以作为手册，在日常开发中做参考。本文也会不断更新，期待你的参与。

如果大家对前端测试不太清楚，可以先看下文末我写的科普短文。如果你已经对前端测试有所了解，并且希望对前端测试有更深入的了解，以及对如何写出更好的单元测试有兴趣的话，那就让我们开始吧。

<!-- more -->

## 写易于测试的代码（Writing test-friendly code）

这是一个非常宽泛的话题，本文试图从几个具体的切入点来阐述这个庞大且模糊的话题。

### 纯函数（Pure Function）

关于[纯函数](https://github.com/azl397985856/functional-programming "函数式教程")可以参考之前我写的一篇函数式教程中的入门篇。

简单来说，纯函数就是数学中的函数。有两个好处：

- 断言容易了。 （可推导性）
- 我可以多次，顺序无关地执行测试用例。 （无副作用）

我举一个例子，这是一个稍微高级一点的技巧。不过你一旦理解了其意图，就会发现其思想是多么的简单。

```jsx
const app = {
    name: `lucifer's site`
    start(html) {
        document.querySelector('#app').innerHTM = html;
    }
}

app.start(<div>inner</div>);
```

上面代码如果要测试，首先你要在 node 环境模拟 document。

如果换一种写法呢？

```jsx
const app = {
    name: `lucifer's site`
    start(querySelector, html) {
        querySelector('#app').innerHTM = html;
    }
}

app.start(document.querySelector, <div>inner</div>);

```

这样模拟 querySelector 就会变得容易起来。eg:

```jsx
// .test.js
import app from "./app";
app.start(() => <div id="app">lucifer</div>, <div>inner</div>);
```

如果你熟悉这种看成方法的话，可能知道它的名字`控制反转`，英文名 IoC。

### 单一职责（Single Responsibility Principle）

如果一个函数承担了一个以上的职责。那么对我们测试有什么影响呢？

如果对于一个函数 f,其功能有 A 和 B。

- A 的输入我们计作 ia，输出计作 oa。
- B 的输入我们计作 ib，输出计作 ob。

那么 f 的圈复杂度会增加很多，具体来说。

- 如果 A 功能和 B 功能相关的话，其测试用例的长度增长是笛卡尔积。
- 如果 A 功能和 B 功能无关的话，其测试用例的长度增长是线性增长。

eg:

```js
function math(a, b, operator) {
  if (operator === "+") return a + b;
  if (operator === "-") return a - b;
  if (operator === "*") return a * b;
  if (operator === "/") return a / b;
}
```

如上代码有四个功能，并且四个功能互相独立。测试用例增长是线性的，也就说将其拆分为四个函数之后，测试用例的数量不变，但是单一函数的圈复杂度降低了，虽然总的软件复杂度并没有降低。

如果四个功能相互耦合的话，后果会更严重。这种情况，拆分多个功能块已经无法解决问题了。这个时候需要对功能进行再次拆解，直到子功能块相互独立。

## 写清晰直白的测试描述（Wrting Deadly Simply Description）

这里我给一个简单的判断标准。

当这个测试报错的时候， 其他人能够只看报错信息，就知道出了什么问题。

比如这样写是好的：

```js
describe(`math -> add`, () => {
  it("3 + 2 should equal to 5", () => {
    expect(3 + 2).to.be.equal(5);
  });
});
```

而这样是不好的：

```js
describe(`math -> add`, () => {
  it("add two numbers", () => {
    expect(3 + 2).to.be.equal(5);
  });
});
```

我举的例子大家可能不屑一顾， 但是当你以我的标准去衡量的时候会发现很多用例都不合格。

## 逻辑覆盖率（Logic Coverage）

很多人关注的是单元测试的物理覆盖率，比如行覆盖率，文件覆盖率等，而大家往往会忽略逻辑覆盖率。

eg:

```js
// a.js
export default (a, b) => a / b


// a.test.js
import divide './a.js'
describe(`math -> divide`, () => {
  it("2 / 2 should be 1", () => {
    expect(divide(2, 2)).to.be(1);
  });
});
```

如上物理覆盖率可以达到 100%，但是很明显逻辑覆盖率却不可以。因为它连最简单的被除数不能为 0 都没包括。

一个更格式的例子，应该是：

```js
// a.js
export default (a, b) => {
    if (b === 0 or b === -0) throw new Error('dividend should not be zero!')
    if (Number(a) !== a || Number(b)=== b) throw new Error(`divisor and dividend should be number，but got ${a, b}`)
    return a / b
}


// a.test.js
import divide './a.js'
describe(`math -> divide`, () => {
  it("when dividend it zero, there should throw an corresponding eror", () => {
    expect(divide(3, 0)).toThrowError(/dividend should not be zero/);
  });
  it("when dividend it zero, there should throw an corresponding eror", () => {
    expect(divide(3, 'f')).toThrowError(/divisor and dividend should be number/);
  });
  it("2 / 2 should be 1", () => {
    expect(divide(2, 2)).to.be(1);
  });
});
```

逻辑的严密性是双向的，一方面他让你的测试用例更严密，更无懈可击。另一方面你的测试用例越严密， 就越驱使你写出更严密的代码。如上 divide 方法就是我根据测试用例反馈的结果后添加上去的。

然后我上面的测试逻辑上还是很不严密，比如：

- 没有考虑大数的溢出。
- 没有考虑无限循环小数。

这么一个简单的除法就有这么多 edge cases，如果是我们实际的业务的话，情况会更加复杂。因此**写好**测试从来都不是一件简单的事情。

## 给测试增加 lint（Add Linting）

测试代码也是需要 lint 的。除了源码的一些 lint 规则，测试应该要加入一些独特的规则。

比如，你的测试代码只是把代码跑了一遍，没有进行任何断言。亦或者是直接断言`expect(true.to.be(true))`，都是不应该被允许的。

比如，断言的时候使用非全等，这也不好的实践。

再比如，使用`toBeNull()`断言，而不是:

```js
expect(null).toBe(null);

expect(null).toEqual(null);

expect(null).toStrictEqual(null);
```

...

类似的例子还有很多，总之测试代码也是需要 lint 的 ，并且相比于被测试代码，其应该有额外的特殊规则，来避免测试代码的**腐烂问题**。

## CI

### 本地测试（Local CI）

可以仅对修改的文件进行测试，eg:

```bash
jest -o
```

### 分阶段测试（Tags）

我们可以按照一定分类标准对测试用例进行分类。

举个例子，我按照测试是否有 IO 将用例分为 IO 类型和 非 IO 类型。那么我就可以在提交的时候只执行非 IO 类型，这样反馈更快。等到我推送到远程的时候执行一次全量操作。

eg:

```js
describe(`"face swiping" -> alipay #io`, () => {
  it("it should go to http://www.alipay.com/identify when user choose alipay", () => {
    // simulate click
    // do heavy io
    // expect
  });
});
```

我们可以这么做

```bash
jest -t = "#io";
```

同样，我可以按照其他纬度对用例进行切分，比如各种业务纬度。这在业务达到一定规模之后，收益非常明显。eg:

```
jest -t = "[#io|#cold|#biz]";
```

如上会仅测试有`io`,`cold`,`biz` 三个标签中的一个或者多个的用例。

> 文件夹和文件名本身也是一种 tag，合理利用可以减少很多工作。

## 框架相关（Framework）

大家问的比较多的问题是如何测试视图，以及如何测试特定的某一种框架下的代码。

### Vue

一个典型的 Vue 项目可能有如下文件类型：

- html
- vue
- js
- ts
- json
- css
- 图片，音视频等媒体资源

如何对他们进行测试呢？JS 和 TS 我们暂时讨论，这个和框架相关性不大。而我们这里关心框架相关的 vue 文件和视图相关的文件。而**json，图片，音视频等媒体资源是没有必要测试的。**

那么如何测试 html，vue 和 css 文件呢？而大多数情况， 大家应用都是 CSR 的，html 只是一个傀儡文件，没有测试的价值。css 的话，如果要测试，只有两种情况，一种是对 CSSOM 进行测试，另外一种是对渲染树的内容进行测试。而一般大家都会对渲染树进行测试。为什么呢？留给大家来思考，欢迎文章后留言讨论。因此本文主要讨论 vue 文件，以及渲染树的测试。

实际上， vue 文件会导出一个 vue 的构造函数，并且合适的时候完成实例化和挂载的过程。而其真正渲染到中的时候，会把 template 标签，style 标签内容一并带过去，当然这中间有一些复杂逻辑存在，这不是本文重点，故不做延伸。

那么，对基于 vue 框架的应用测试主要关注一点，渲染树本身。 其实你用别的框架，或者不用框架也是一样的。

不同的是，vue 是一种基于数据驱动的框架。

```js
(props) => view;
```

因此我们是不是只要测试不同的 props 组合，是否展示我们期望的 view 就可以了？

是也不是。 我们先假定”是“。那么我们的问题转化为：

- 如何组合合适的 props
- 如何断言 view 是否正确渲染

对于第一个问题，这个是组件设计的时候应该考虑的事情。对于第二个问题，答案是 `vue-test-utils`。

`vue-test-utils` 本身就是解决这个问题的，如果我将一个 app 看成是组件的有机体（组件以及组件之间的通信协作），并将组件看成函数的话。那么`vue-test-utils` 的核心功能就是:

- 帮你执行这些函数。
- 改变函数内部的状态。
- 触发函数之间的通信。
- 。。。

`vue-test-utils` 的 wrapper 同时完成了上面两件事`setProps` 和 `assert`。`vue-test-utils` 还帮你做了很多事情， 比如组件嵌套（类似函数调用栈）如何测试，怎么 mock props，router 等。

一句话来说，就像是一双无形的手，**帮你操作 app 的初始化， 挂载，更新，卸载等，并且直接或者间接提供断言机制**。 更多可以参考 https://vue-test-utils.vuejs.org/

以上内容基于一个事实 `我们只要测试不同的 props 组合，是否展示我们期望的 view 就可以`。然而， vue 虽然将其抽象为函数，但是要注意这个函数和我上文讲到的纯函数相差甚远，就连以`函数式友好`闻名的 React 也做不到这一点。

也就是说，你还需要考虑副作用。从这一点上来看，这是和我上文提到的最佳实践背离的。但是真正地将副作用全部抽离开的框架不怎么流行，比如 cyclejs, elm。因此我们必须接受这个事实。我们虽然无法避免这种事情的发生，但是我们可以限制其在我们可控制的范围，典型的技巧就是沙箱机制，这同样超出了本文的论述范围，故不做引申。

### React

TODO

## 其他（Others）

### Make it Red， Make it Green

其实这就是测试驱动开发的本质。

- 先写用例，甭管飘红不飘红，先把测试用例写好，定义好问题边界。

- 然后一个个将红色的变成绿色。

- 再结合上面我提到的技巧，做持续集成。在你打字的时候可以执行的测试用例有哪些，在你提交到本地仓库的时候可以执行的用例有哪些。

## 参考（Reference）

- [两年前写的前端测试短文](https://github.com/azl397985856/frontend-test "两年前写的前端测试短文")
- [eslint-plugin-jest](https://github.com/jest-community/eslint-plugin-jest)
