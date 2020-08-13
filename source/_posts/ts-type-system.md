---
title: TypeScript 类型系统（草稿）
tags: [前端, 浏览器, webkit]
date: 2020-08-13
categories:
  - [前端, 浏览器]
  - [前端, webkit]
  - [浏览器, webkit]
---

## 类型系统是 TypeScript 最主要的功能

TypeScript 官方描述中有一句：**TypeScript adds optional types to JavaScript that support tools for large-scale JavaScript applications **。实际上这也正是 Typescript 的主要功能，即给 JavaScript 添加静态类型检查。要想实现静态类型检查，首先就有有类型系统。

TypeScript 支持 JavaScript 中所有的类型，并且还支持一些 JavaScript 中没有的。 那为什么要增加 JavaScript 中没有的类型呢？我举个例子，比如如下给一个变量声明类型为 Object，Array 的代码。

```ts
const a: Object = {};
const b: Array = [];
```

- 其中第一行代码 Typescript 允许，但是太宽泛了，我们很难得到有用的信息，推荐的做法是使用 interface 来描述，我们后面会讲到。

- 第二行 Typescript 则会直接报错，我们需要使用泛型来进一步约束。

总之，我们使用 Typescript 的主要目的仍然是要它的静态类型检查，帮助我们提供代码的扩展性和可维护性。因此 Typescript 需要维护一套完整的类型系统。

有的同学可能有疑问， JavaScript 不是也有类型么？ 它和 Typescript 的类型是一回事么？JavaScript 不是动态语言么，那么经过 Typescript 的限定会不会丧失动态语言的动态性呢？我们继续往下看。

## 变量类型和值类型

- JavaScript 中的类型其实是值的类型。实际上不仅仅是 JavaScript，任何动态类型语言都是如此，这也是动态类型语言的本质。

- Typescript 中的类型其实是变量的类型。实际上不仅仅是 Typescript，任何静态类型语言都是如此，这也是静态类型语言的本质。

记住这两句话，我们接下来解释一下这两句话。

对于 JavaScript 来说，一个变量可以是任意类型。

```js
var a = 1;
a = "lucifer";
a = {};
a = [];
```

上面的值是有类型的。比如 1 是 number 类型，"lucifer" 是字符串类型， {} 是对象类型， [] 是数组类型。而变量 a 是没有固定类型的。

对于 Typescript 来说， 一个变量只能接受和它类型兼容的类型的值。说起来比较拗口， 看个例子就明白了。

```ts
var a: number = 1;
a = "lucifer"; // error
var b: any = 1;
a = "lucifer"; // ok
a = {}; // ok
a = []; // ok
```

我们不能将 string 类型的值赋值给变量 a， 因为 string 和 number 类型不兼容。而我们可以将 string,Object,Array 类型的值赋值给 b，因此 它们和 any 类型兼容。简单来说就是，一旦一个变量被标注了某种类型，那么其就只能接受这个类型以及它的子类型。

## 类型空间和值空间

类型和值居住在不同的空间，一个在阳间一个在阴间。他们之间互相不能访问，甚至不知道彼此的存在。

### 类型空间

如下代码会报类型找不到的错：

```ts
const aa: User = { name: "lucifer", age: 17 };
```

这个比较好理解，我们只需要使用 interface 声明一下 User 就行。

```ts
interface User {
  name: string;
  age: number;
}

const aa: User = { name: "lucifer", age: 17 };
```

也就是说使用 interface 可以在类型空间声明一个类型。这个是 Typescript 的类型检查的基础，也是本文要讲的内容。

实际上类型空间内部也会有子空间。我们可以用 namespace（老）和 module（新） 来创建新的子空间。子空间之间不能之间接触，需要依赖导入导出来交互。

### 值空间

比如，我用 Typescript 写下如下的代码：

```ts
const a = window.lucifer();
```

Typescript 会报告一个类似`Property 'lucifer' does not exist on type 'Window & typeof globalThis'.` 的错误。

实际上，这种错误并不是类型错误，而是值的错误。我们可以这样解决：

```ts
declare var lucifer: () => any;
```

也就是说使用 declare 可以在值空间声明一个变量。这个是 Typescript 的变量检查的基础，不是本文要讲的主要内容，大家知道就行。

## 类型编程和值编程

上面说了**类型和值居住在不同的空间，一个在阳间一个在阴间。他们之间互相不能访问，甚至不知道彼此的存在。**

使用 declare 和 interface or type 就是分别在两个空间编程。比如 Typescript 的泛型就是在类型空间编程，叫做类型编程。除了泛型，还有集合运算，一些操作符比如 keyof 等。值的编程在 Typescript 中更多的体现是在类似 lib.d.ts 这样的库。当然 lib.d.ts 也会在类型空间定义各种内置类型。我们没有必要去死扣这个，只需要了解即可。

lib.d.ts 的内容主要是一些变量声明（如：window、document、math）和一些类似的接口声明（如：Window、Document、Math）。寻找代码类型（如：Math.floor）的最简单方式是使用 IDE 的 F12（跳转到定义）。

## 类型系统的组成

TypeScript 要想解决 JavaScript 动态语言类型太宽松的问题，就需要：

1. 提供给类型设定类型的能力
2. 提供常用类型
3. 可以扩展出自定义类型

第一个问题是通过类型注解的语法来完成。即类似这样：

```ts
const a: number = 1;
```

> Typescript 的类型注解是这样， Java 的类型注解是另一个样子，Java 类似 int a = 1。 这个只是语法差异而已，作用是一样的。

第二个问题， Typescript 提供了 lib.d.ts。随着 ES 的不断更新， JavaScript 类型和全局变量会逐渐变多。Typescript 也是采用这种 lib 的方式来解决的。

![](https://tva1.sinaimg.cn/large/007S8ZIlly1ghmyjgyd7qj307o0lxgmq.jpg)

（部分 lib）

第三个问题，Typescript 主要是通过 interface，type 打通类型空间。

接下来，我们介绍类型系统的功能，即它能为我们带来什么。

## 类型系统的主要功能

1. 定义类型以及其上的属性和方法。

比如定义 String 类型， 以及其原型上的方法和属性。

2. 提供自定义类型的能力

```ts
interface User {
  name: string;
  age: number;
  say(name: string): string;
}
```

这个是我自定义的类型 User，这是 Typescript 必须提供的能力。

3. 类型兼容体系。

这个主要是用来判断类型是否正确的，上面我已经提过了，这里就不赘述了。

4. 类型推导

有时候你不需要显式说明类型（类型注解），Typescript 也能知道他的类型，这就是类型推导结果。

```ts
const a = 1;
```

如上代码，编译器会自动推导出 a 的类型 为 number。还可以有连锁推导，泛型的入参（泛型的入参是类型）推导等。类型推导还有一个特别有用的地方，就是用到类型收敛。

我们来详细了解下类型推导和类型收敛。

## 类型推导和类型收敛

## 总结
