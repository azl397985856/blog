# TypeScript 类型系统

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

## 变量的类型和值得类型

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

但是上面的值是有类型的。比如 1 是 number 类型，"lucifer" 是字符串类型， {} 是对象类型， [] 是数组类型。

对于 Typescript 来说， 一个变量只能接受和它类型兼容的类型的值。说起来比较拗口， 看个例子就明白了。

```ts
var a: number = 1;
a = "lucifer"; // error
var b: any = 1;
a = "lucifer"; // ok
a = {}; // ok
a = []; // ok
```

类型空间和值空间

类型编程和值编程

## 类型系统的主要功能就是

1. 定义类型和类型上的属性和方法
2. 提供自定义类型的能力，并扩展 1

## 基础类型

## 复合类型

## 泛型（请参考）

## 类型收敛

## 类型推导
