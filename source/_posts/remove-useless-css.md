---
title: 如何移除项目中未使用的 CSS
tags: [CSS, AST, Chrome]
date: 2023-08-08
---

使用 chrome 的 devtool 可以查看项目中未被使用的 JS 和 CSS。具体可以参考下 chrome 官方的博客: [Coverage: Find unused JavaScript and CSS](https://developer.chrome.com/docs/devtools/coverage/)

有没有方法可以自己检测呢？甚至是做成工具集成到 CI/CD 甚至 code review 中呢？

看完本文，你能学到如何自己手撸一个这样的工具。同时也会推荐社区里经过验证的好用的同类型库。

<!-- more -->

## 前置知识

- postcss
- jsdom

## 正文

推荐两个库，其中第一个是我使用过的。另外一个研究了一下，和第一个大同小异，下面我会具体分析，大家看完后可以根据自己的情况进行选择。

### uncss

首先第一个工具：uncss

一个最简洁的用法（全部使用默认配置）：

```js
var uncss = require('uncss');

var files = ['my', 'array', 'of', 'HTML', 'files', 'or', 'http://urls.com'],

uncss(files, function (error, output) {
    console.log(output);
});

```

它会在内存中使用 jsdom 打开你的 HTML 文件， 然后像上面提到的 chrome devtools 的 coverage 功能一样分析你的哪些 CSS 选择器是没有被使用到的。

其配置项也非常丰富，具体可以参考[官方文档](https://github.com/uncss/uncss/blob/master/README.md)

它的原理非常简单，第一个核心部分是 process 函数。

> 省略非核心代码

```js
async function process(opts) {
  // getHTML 会调用 jsdom.fromSource ，生成 page 对象。由于可以输入多个文件，因此会返回 pages 数组
  const pages = await getHTML(opts.html, opts);

  // ... 省略非核心代码
  // getStylesheets 会调用 jsdom.getStylesheets 得到样式文件
  return getStylesheets(opts.files, opts, pages);
}
```

经过上面的预处理后会走到第二个关键部分是 uncss 函数。

```js
/**
 * Main exposed function
 * @param  {Array}   pages      List of jsdom pages
 * @param  {Object}  css        The postcss.Root node
 * @param  {Array}   ignore     List of selectors to be ignored
 * @return {Promise}
 */
module.exports = async function uncss(pages, css, ignore) {
  const nestedUsedSelectors = await Promise.all(
    pages.map((page) => getUsedSelectors(page, css))
  );
  const usedSelectors = _.flatten(nestedUsedSelectors);
  const filteredCss = filterUnusedRules(css, ignore, usedSelectors);
  const allSelectors = getAllSelectors(css);
  return [
    filteredCss,
    {
      /* Get the selectors for the report */
      all: allSelectors,
      unused: _.difference(allSelectors, usedSelectors),
      used: usedSelectors,
    },
  ];
};
```

核心就是 `getUsedSelectors(pages, css)` ，根据你提供的 HTML 和 CSS，找到被使用的选择器， 全部的选择器减去被使用的选择器自然就是没有被使用到的选择器。

```js
/**
 * Find which selectors are used in {pages}
 * @param  {Array}    page          List of jsdom pages
 * @param  {Object}   css           The postcss.Root node
 * @return {Promise}
 */
function getUsedSelectors(page, css) {
  let usedSelectors = [];
  css.walkRules((rule) => {
    usedSelectors = _.concat(usedSelectors, rule.selectors.map(dePseudify));
  });

  return jsdom.findAll(page.window, usedSelectors);
}
```

getUsedSelectors 则是使用 postcss， 对 CSS 进行 AST 转化后，调用 dePseudify 进行处理。

dePseudify 基本上就是直接调用了 `postcss-selector-parser`。不熟悉 `postcss-selector-parser` 的话也没关系，看下它官方提供的 demo 就懂了。

```js
const parser = require("postcss-selector-parser");
const transform = (selectors) => {
  selectors.walk((selector) => {
    // do something with the selector
    console.log(String(selector));
  });
};

const transformed = parser(transform).processSync("h1, h2, h3");
```

可以看出， 就是给定一个 css 文本，它会逐个输出 css 中的选择器。

简单总结一下它的原理，使用 jsdom 读取 html 和 css。jsdom 可以得到已经被使用的选择器， postcss 以及插件会得到 css 中的全部选择器。两者相减，就是没有被使用的 css。

### purifycss

相比上一个库，这个就非常小巧了。提供的配置也比较少，[官方文档](https://github.com/purifycss/purifycss)

```js
import purify from "purify-css";

let content = "";
let css = "";
let options = {
  output: "filepath/output.css",
};
purify(content, css, options);
```

核心代码就是 purify 函数。

```js
const purify = (searchThrough, css, options, callback) => {
  // ... 省略非核心代码
  let cssString = FileUtil.filesToSource(css, "css"),
    content = FileUtil.filesToSource(searchThrough, "content");

  let wordsInContent = getAllWordsInContent(content),
    selectorFilter = new SelectorFilter(wordsInContent, options.whitelist),
    tree = new CssTreeWalker(cssString, [selectorFilter]);
  tree.beginReading();
  let source = tree.toString();

  fs.writeFile(options.output, source, (err) => {
    if (err) return err;
  });
};
```

getAllWordsInContent() 是获取全部的 css 选择器。

tree.beginReading() 是为了获取已经被引用的 css 选择器。

两者相减就是未被使用的选择器。

其中 tree.beginReading 则是调用了另外一个库 rework 实现的。rework(this.startingSource).use(this.readPlugin.bind(this));

本质上也是借助于 rework 提供的插件系统，自己实现了一个插件 selectorFilter 来找到被使用的选择器。而 selectorFilter 的核心就是 filterSelectors 这样一个函数：

```js
function filterSelectors(selectors) {
    let contentWords = this.contentWords,
        rejectedSelectors = this.rejectedSelectors,
        usedSelectors = []

    selectors.forEach(selector => {
        
        let words = getAllWordsInSelector(selector),
            usedWords = words.filter(word => contentWords[word])

        if (usedWords.length === words.length) {
            usedSelectors.push(selector)
        } else {
            rejectedSelectors.push(selector)
        }
    })

    return usedSelectors
}
```

如果你没听过 rework 也没关系， 你可以将 rework 看成是 postcss 去理解，问题不大。

## 总结

相信读完本文，你已经明白如何自己实现一个这样的工具，只不过还有需要考虑就是了。

如果你是想在开发阶段大概看一下未被使用的代码，推荐 chrome 的 devtool 工具 coverage。

如果你想使用现成工具，个人更推荐使用 uncss，因为其实基于 jsdom 的， 实现上更接近 chrome 的 coverage 功能，支持的功能也更多。你甚至可以基于它实现 e2e 测试后，出具一份未被使用的选择器名单。

而 purifycss 则简单许多，但是原理是相似的，都是将 css 进行 ast 化，然后使用插件分析规则作为被使用的选择器，然后 html 中引用的选择器作为全部的选择器，两者相减得出没有被使用的选择器。