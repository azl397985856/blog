---
title: 记一次从 webpack 4 升级 webpack 5 + swc 的经历
tags: [webpack, swc]
date: 2023-03-27
---

最近将项目的 webpack 4 升级到了 webpack 5，用了一两天的时间，遇到了一些网上找不到资料的问题， 于是决定将过程记录一下。

<!-- more -->

直接找到官方提供的迁移教程 [To v5 from v4](https://webpack.js.org/migrate/5/) 进行操作。

## 升级 webpack

将项目依赖的版本直接改为最新版本，注意将变更同步到 package.json 和 lock 文件。

## 逐个检查 loader 和 plugin 的 兼容性

我用到了一个叫 [virtual-module-webpack-plugin](https://github.com/rmarscher/virtual-module-webpack-plugin) 的插件，根据 readme 的介绍，直接改为 [webpack-virtual-modules](https://github.com/sysgears/webpack-virtual-modules) 即可。

写法有一点小小的变动。

before:

```js
plugins: [
  new VirtualModulePlugin({
    moduleName: "src/mysettings.json",
    contents: JSON.stringify({ greeting: "Hello!" }),
  }),
];
```

after:

```js
plugins: [
  new VirtualModulesPlugin({
    "src/mysettings.json": JSON.stringify({ greeting: "Hello!" }),
  }),
];
```

## 检查项目中是否使用到了 breakchange 功能

使用官方提供的命令在项目下跑一下即可。

```bash
node --trace-deprecation node_modules/webpack/bin/webpack.js
```

核心就是在项目下跑一下 webpack，webpack 会打印一些 deprecation 警告，通过上面的命令可以将其筛出来。

1. 内置模块不再 polyfill

由于 webpack 5 内置不在 polyfill path，process 等，因此如果你的项目用到了，需要自己处理。处理方式也很简单。

对于 path:

```js
config.resolve.fallback.path = require.resolve("path-browserify");
```

更多请参考：[how-to-polyfill-node-core-modules-in-webpack-5](https://stackoverflow.com/questions/64557638/how-to-polyfill-node-core-modules-in-webpack-5)

2. 个别 sourcemap 选项变更

比如 cheap-module-eval-sourcemap 改为了 eval-cheap-module-source-map

这个问题虽然网上我没找到解决方案，但是我问了 chatgpt 它告诉了怎么做（感谢chatgpt）。

3. 如果你开发了一些插件和 loader， 那么要注意一些 api 变了。

比如 assets.compilation，再或者 compiler.hooks.invalid.call 

这些变化虽然没有在官方文档体现，但是你的项目中如果使用 ts，那么其会直接报错，应该也不算太坑。

## 循环依赖

webpack4 默认帮助我们处理循环依赖问题。 而webpack5则不会。

webpack5 会报错：`webpack 5 cannot access '__webpack_default_export__' before initialization`

因此如果你的项目中使用了循环依赖， 可以尝试改变写法。如果你不知道哪里有循环依赖，也可以使用 webpack 官方推荐的检测插件。

[Circular Dependency Plugin](https://github.com/aackerman/circular-dependency-plugin) - Detect modules with circular dependencies when bundling -- Maintainer: Aaron Ackerman

## types 丢失

webpack 4 的版本，如果直接使用 api 模式， 那么可以使用很多它导出的类型，webpack 5 中不再导出， 可以使用 patch-package 的方式修改包，也可以自己 declare webpack module 去扩展。

比如不再导出的类型有：

- MultiWatching
- LoaderContext
- Plugin
- ...

## 升级到 swc-loader

之前用的是 babel-loader，这次顺便升级一下 swc，速度据说比 babel-loader 快很多。实际使用我的项目要快 20%-40%。由于每个项目不一样，仅供参考。

升级 swc-loader 很简单。

before:

```js
module: {
  rules: [
    {
      test: /\.m?js$/,
      exclude: /(node_modules)/,
      use: {
        // `.babelrc` can be used to configure swc
        loader: "babel-loader",
      },
    },
  ];
}
```

after:

```js
module: {
  rules: [
    {
      test: /\.m?js$/,
      exclude: /(node_modules)/,
      use: {
        // `.swcrc` can be used to configure swc
        loader: "swc-loader",
      },
    },
  ];
}
```

由于我项目中使用了 sourcemap，因此直接修改会报错。

```
swc-loader 0: failed to read input source map from user-provided sourcemap
```
解决方式很简单，直接 swc-loader 传递 sourceMap: false 即可，这样swc-loader 就不处理 sourcemap 了。如果 为 true 的话，swc-loader 会将 sourcemap JSON.stringify 一下，从而出问题。

swc-loader 处理这部分的源码大概是：

```js
swc.transform(source, options).then(output => callback(null, output.code, parseMap ? JSON.parse(output.map) : output.map), err => callback(err))
```

也就是说设置不解析 sourcemap 后就不会序列化了。

## 其他遇到的问题

- node.setImmediate 不支持了，其实 node 上的东西都不支持了。比如 buffer， path 等等。
- optimization.noEmitOnErrors 变为了 optimization.emitOnErrors，这个就是 true 和 false 换一下的事，不理解 webpack5 为啥要改这个。
- compiler.outputFileSyste.write 签名好像变了
- compilation.assets 的类型变了。之前 Source 类的 map 函数返回值可以是 null， 现在只能是 Object 类型

这几个解决方式网上都有，也很简单，不再赘述。


## 总结

这次迁移使得项目性能提升 20% - 30%，总共花了一两天的时间，效果还不错。

另外也会之后升级 rspack 做了准备，因此 rspack 给的迁移例子都是 webpack 5 的， 也就是说如果 webpack 5 出问题更容易找到资料。

我自己试了一下， 目前强行迁移到 rspack 坑很多，并且网上几乎没资料可以参考，所以决定先等等等到社区相对成熟了再入坑。
