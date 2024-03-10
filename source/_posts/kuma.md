---
title: kuma - css-in-js 的未来？
tags: [前端, css-in-js]
date: 2024-03-07
categories:
  - [前端, css-in-js]
---

kuma 是一个炙手可热的 css-in-js 的解决方案，有人甚至说他是 css-in-js 的未来，这篇文章我们来探讨一下 css-in-js 与 kuma。

<!-- more -->

## 什么是 css-in-js

CSS-in-JS 是一种将 CSS 代码嵌入到 JavaScript 代码中的技术。它可以提供一些优势，例如更好的组件化、更好的性能、更好的开发体验等。

以 emotion 为例，如下代码就是一个典型的 css-in-js 的例子：

```jsx
import React from "react";
import { css } from "@emotion/react";

const buttonStyles = css`
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  background-color: #007bff;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
`;

function Button({ children }) {
  return <button css={buttonStyles}>{children}</button>;
}
```

相对地，就是传统的 css 代码：

```css
.button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  background-color: #007bff;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
}
```

```jsx
import React from "react";
import "./button.css";

function Button({ children }) {
  return <button className="button">{children}</button>;
}
```

## css-in-js 的优缺点

首先我们来看下 css-in-js 的优点：

1. 更好的组件化：css-in-js 可以让你将样式和组件放在一起，这样可以更好地组织代码。（想象一下引入 antd 等组件库的时候，我们需要自己单独引入一下 css 文件。而如果组件库是用 css-in-js 写的，就不会有这个问题了）
2. 某些情况下有更好的性能：css-in-js 可以减少网络请求数量，因此某些情况下可以提供更好的性能。
3. 由于 css-in-js 是运行时的，所以可以根据不同的条件动态生成样式。

然后我们来看下 css-in-js 的缺点：

1. 学习成本：css-in-js 有一定的学习成本，因为它需要学习新的语法和工具。
2. 某些情况下有性能问题：如果 css 很多的话，css-in-js 可能会有性能问题，因为它可能会增加 JavaScript 代码的大小。

## kuma 是什么，它是如何解决传统 css-in-js 的问题的？

kuma 的核心卖点是零运行时的 css-in-js 技术（zero-runtime CSS-in-JS）。同时也利用了运行时 CSS-in-JS 的表达能力。这两种技术的结合可以提供强大的样式能力，同时也保持了良好的性能。

"Zero-runtime CSS-in-JS"是一种在构建时生成 CSS 的技术，而不是在运行时。这意味着所有的 CSS 都在 JavaScript 代码执行之前就已经被生成和插入到页面中，这可以减少运行时的性能开销。

kuma 使用 Babel 插件或 Webpack 加载器来实现。babel 插件可以将 css-in-js 的代码转换成 css 代码。这样就可以在构建时生成 css 代码。也就是说你写的是 css-in-js 的代码，但是构建后生成的是 css 文件。这样可以同时获得 css-in-js 的优点，又避免了 css-in-js 的缺点。

但是核心的点在于并不是所有的 css 都可以在静态地生成，有些 css 是需要在运行时生成的。这如何处理呢？

kuma 的解决方案是静态提取可以在构建时确定的样式，并对可能动态更改的样式执行静态“脏检查”，并在运行时注入它们。

而这一切对开发者来说是透明的，你只需要写 css-in-js 的代码，然后构建后就会生成 css 文件。

## kuma 的核心原理

假设我们写了如下的 css-in-js 代码：

```jsx
function App() {
  return (
    <Heading
      as="h3"
      className={css`
        color: red;
        @media (max-width: sm) {
          color: blue;
        }
      `}
    >
      Kuma UI
    </Heading>
  );
}
```

经过 kuma 的处理，会变成如下的 css 代码：

```css
._1 {
  color: red;
}
@media (max-width: sm) {
  ._1 {
    color: blue;
  }
}
```

和如下的 jsx 代码：

```jsx
function App() {
  return <Heading as="h3" className="_1">Kuma UI</Heading>;
}
```

> lucifer 提示：如果让你自己实现这个转化，你会吗？

了解到 kumaui 做了什么之后，我们接下来看它是如何完成这样的转化的。

kumaui 的 css 方法本质上是接受一个模板字符串，然后将其转化成 css 代码。这个过程是通过 Babel 插件来完成的。

比如核心代码 kuma-ui/packages/babel-plugin/src/transform.ts

```ts
import { transformSync } from "@babel/core";
import { compile } from "@kuma-ui/compiler";
import pluin from ".";
import { sheet } from "@kuma-ui/sheet";

export function transform(code: string, id: string) {
  const result = transformSync(code, {
    filename: id,
    sourceMaps: true,
    plugins: [pluin],
  });
  if (!result || !result.code) return;

  const bindings = (
    result.metadata as unknown as { bindings: Record<string, string> }
  ).bindings;
  const compiled = compile(result.code, id, bindings);
  result.code = compiled.code;
  (result.metadata as unknown as { css: string }).css =
    sheet.getCSS() + compiled.css;
  sheet.reset();
  return result;
}
```

如上代码就是就是一个 babel 插件，核心逻辑写在了 compile 函数里面。compile 函数接受一个 css-in-js 的代码，然后将其转化成 css 代码。

kuma-ui/packages/compiler/src/compile.ts

```ts
import {
  Project,
  Node,
  SyntaxKind,
  JsxOpeningElement,
  JsxSelfClosingElement,
} from "ts-morph";
import { collectPropsFromJsx } from "./collector";
import { extractProps } from "./extractor";
import { componentList } from "@kuma-ui/core/components/componentList";
import { optimize } from "./optimizer/optimize";
import { processTaggedTemplateExpression } from "./processTaggedTemplateExpression";

const project = new Project({});

const compile = (
  code: string,
  id: string,
  bindings: Record<string, string>,
) => {
  const css: string[] = [];
  const source = project.createSourceFile(id, code, { overwrite: true });
  source.forEachDescendant((node) => {
    if (
      node.getKind() === SyntaxKind.JsxElement ||
      node.getKind() === SyntaxKind.JsxSelfClosingElement
    ) {
      let openingElement: JsxOpeningElement | JsxSelfClosingElement;
      if (node.getKind() === SyntaxKind.JsxElement) {
        const jsxElement = node.asKindOrThrow(SyntaxKind.JsxElement);
        openingElement = jsxElement.getOpeningElement();
      } else {
        openingElement = node.asKindOrThrow(SyntaxKind.JsxSelfClosingElement);
      }
      const jsxTagName = openingElement.getTagNameNode().getText();
      // Check if the current JSX element is a Kuma component
      const originalComponentName = Object.keys(bindings).find(
        (key) =>
          bindings[key] === jsxTagName &&
          Object.values(componentList).some((c) => c === key),
      );
      if (!originalComponentName) return;

      const componentName =
        originalComponentName as (typeof componentList)[keyof typeof componentList];
      const extractedPropsMap = collectPropsFromJsx(openingElement);
      const result = extractProps(
        componentName,
        openingElement,
        extractedPropsMap,
      );
      if (result) css.push(result.css);

      optimize(
        componentName,
        openingElement,
        extractedPropsMap["as"] as string | undefined,
      );
    }
    if (Node.isTaggedTemplateExpression(node)) {
      processTaggedTemplateExpression(node, bindings);
    }
  });
  return { code: source.getFullText(), id, css: css.join(" ") };
};

export { compile };
```

可以看出遇到 kuma 组件就会调用 extractProps 函数，然后将其中的 css-in-js 代码转化成 css 代码。

上面的代码忽略细节后其实非常简单，不做过多解释。

而关于大家比较关心的 dirty check，其实和 vue 的 block tree 有点类似，对于没有 JS表达式的节点，可以完整提取出 css（就像我们前面举的例子一样）。而对于动态的比如如下代码：

```jsx
function App() {
  const useRed = localStorage.getItem("useRed");
  return (
    <Heading
      as="h3"
      className={css`
        color: ${useRed ? "red" : "blue"};
      `}
    >
      Kuma UI
    </Heading>
  );
}
```

由于无法在构建时确定 color 是 red 和 blue，那就还是需要在运行时注入它们。（这个只是为了方便大家理解举的例子，并不意味着 kuma 是对这种非常简单的动态处理也没有做“静态化”处理）。

幸运的是，静态的应用场景还是比较多的，因此总体上 kuma 还是比较快的。

关于更深入的 dirty check 原理内容完全可以开一期文章来讲，这里就不展开了。

## 总结

kuma 是一个 css-in-js 的解决方案，它利用了"zero-runtime CSS-in-JS"技术，同时也利用了运行时 CSS-in-JS 的表达能力。这两种技术的结合可以提供强大的样式能力，同时也保持了良好的性能。

kuma 的核心原理是通过 Babel 插件将 css-in-js 的代码转化成 css 代码。这样可以在构建时生成 css 代码。也就是说你写的是 css-in-js 的代码，但是构建后生成的是 css 文件。这样可以同时获得 css-in-js 的优点，又避免了 css-in-js 的缺点。

- kuma ui 仓库地址：https://github.com/kuma-ui/kuma-ui
- kuma ui 官网：https://www.kuma-ui.com/docs