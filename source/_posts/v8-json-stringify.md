---
title: 我们是如何让 JSON.stringify 的速度提升两倍以上的
tags: [v8,javascript,json,stringify,性能优化]
date: 2025-12-21
categories:
  - [前端]
  - [v8]
---

大家好，我是 lucifer~

今天咱们来聊聊一个前端开发中常见的“幕后英雄”——`JSON.stringify`。你知道吗？这个函数在 V8 引擎（Chrome 和 Node.js 的 JavaScript 引擎）里最近被优化得飞起，速度直接翻倍以上！咱们会用通俗的话解释概念，加点背景知识和生活比喻，还会配上代码示例帮你理解。如果你边看边敲代码，效果会更好哦——记住，实践出真知！

为什么选这个话题？因为 `JSON.stringify` 几乎无处不在：发网络请求、存 localStorage、日志记录……它慢一点，整个网页就卡一点。优化它，就等于给你的 app 装了个涡轮增压器。咱们先从基础聊起，然后深入优化细节，最后看看实际效果。走起！

<!-- more -->

## 旧版的问题：为什么它那么慢？

旧版的 `JSON.stringify` 用递归方式遍历对象：遇到数组就往下钻，遇到对象就展开属性。这听起来简单，但有隐患：

- **栈溢出风险**：递归太深（比如嵌套 1000 层），浏览器就崩溃。所以每次递归前都要检查栈空间，额外开销大。
- **字符串处理低效**：JavaScript 字符串有单字节（ASCII）和双字节（Unicode）两种。旧版混在一起处理，分支判断多，CPU 闲置。
- **转义字符慢**：字符串里有引号、反斜杠啥的，得转义（像 \"）。旧版一个字符一个字符检查，费时。
- **键值检查繁琐**：每个属性都要验证是不是可枚举、键是不是字符串、需不需要转义。
- **数字转换瓶颈**：浮点数转字符串用旧算法 Grisu3，不够快。
- **缓冲区管理傻**：用一个大数组存结果，对象越大，数组越长，还得不停复制扩展。

结果？在 JetStream2 测试中，旧版表现平平。V8 团队瞄准这些痛点，推出“快车道”模式，只针对常见场景（纯数据对象，无自定义函数），避开复杂情况。复杂对象？ fallback 到旧版，保证兼容。

## 优化黑科技一：引入“快车道” (Fast Path)

“快车道”就像高速公路：前提是你不开“改装车”（无自定义 .toJSON() 方法、无 replacer 函数、无 space 缩进）。为什么？这保证了过程无副作用——不会触发垃圾回收或用户代码，纯计算。由此，它可以绕过通用序列化器所需的许多耗时的检查和防御逻辑，比如栈溢出防护、用户代码执行防范等，直接用一个专属的迭代实现，避开递归的开销。

在这个模式下，他们把递归改成迭代（循环）：用一个栈模拟遍历，避免栈检查开销。还能支持更深嵌套，不会崩。

类比：递归像爬楼梯，一层一层上；迭代像坐电梯，直达。

代码示例：虽然 V8 是 C++ 实现的，但咱们用 JS 模拟迭代版 stringify 的思路（简化版，只处理对象和数组）：

```javascript
function simpleIterativeStringify(obj) {
  const stack = [{ value: obj, isKey: false, parent: [] }];
  let result = "";

  while (stack.length > 0) {
    const current = stack.pop();
    const { value, isKey, parent } = current;

    if (typeof value === "string") {
      result += isKey ? `"${value}":` : `"${value}"`; // 简单转义，实际更复杂
    } else if (typeof value === "number") {
      result += value.toString();
    } else if (Array.isArray(value)) {
      parent.push("[");
      for (let i = value.length - 1; i >= 0; i--) {
        // 反序入栈
        stack.push({ value: value[i], isKey: false, parent });
      }
    } else if (typeof value === "object" && value !== null) {
      parent.push("{");
      const keys = Object.keys(value).reverse(); // 反序处理
      for (const key of keys) {
        stack.push({ value: value[key], isKey: false, parent });
        stack.push({ value: key, isKey: true, parent });
      }
    }
    // ... 其他类型处理
  }
  return result; // 实际需要处理逗号、分隔等
}

console.log(simpleIterativeStringify({ name: "小明", age: 25 })); // 类似 JSON 输出
```

这个模拟展示了迭代怎么用栈避免递归。实际 V8 更高效，但思路一样。

## 优化黑科技二：字符串处理大升级

字符串是 stringify 的主力，占了大部分工作量。V8 新版针对 JavaScript 字符串的两种内部表示——单字节（one-byte，纯 ASCII）和双字节（two-byte，含 Unicode）——做了模板化处理（templated processing）。简单说，就是编译出两个专版函数：一个只处理单字节字符串，一个只处理双字节。这样，在纯单字节场景（常见于英文数据），全程无分支检查；如果混杂，动态切换。

详细怎么工作？序列化开始时，检查第一个字符串的实例类型（instance type）。如果是单字节，就用单字节版 stringifier 处理后续。如果途中遇到双字节字符串，就切换到双字节版，继承当前状态（比如缓冲区位置），继续处理。最后，把两部分输出连接起来。切换成本低，因为 V8 本来就有实例类型检查机制。

类比：旧版像一个厨师做菜时不停问“这是米饭还是面条？”，每步都判断；新版像两个专厨，一个只炒米饭，一个只煮面条，需要时无缝换人。

对比旧版：旧版用统一实现，每处理一个字符都要分支检查编码（是单字节还是双？），CPU 缓存命中率低，分支预测失败多。结果？慢。新版模板化后，常见纯单字节场景零分支，速度飞升。即使切换，也只多点二进制大小（minor binary size increase），但性能收益大。

除了模板化，转义加速也是重头戏。转义就是处理特殊字符，如 " 变成 \"，\ 变成 \\。旧版逐字符循环检查：for 循环一个一个看，有特殊就转义。慢，因为常见字符串无特殊字符，却白白循环一圈。

新版用 SIMD（单指令多数据，像并行工人）和 SWAR（软件 SIMD，用位运算）加速。长字符串用硬件 SIMD（如 ARM64 Neon，一次处理 16 字节），扫描整块找特殊字符；短字符串用 SWAR，在通用寄存器上位运算批量查（比如用 XOR 和 AND 魔法检测 '"' 或 '\\'）。

类比：旧版像一个保安一个门检查行李；新版像安检机，一扫一大片。如果无问题，直接 memcpy 大块拷贝字符串到输出，零修改。

前后对比：旧版逐字符循环，时间 O(n)，但常量大（每个字符分支多）；新版并行扫描，时间接近 O(n/16)，常量小。尤其无转义常见案，拷贝超快。V8 源码有具体实现，比如 SWAR 用位运算处理 8 字节 chunk：

代码示例（伪 C++，参考 V8 源码）：

```cpp
// 旧版逐字符示例（简化）
void oldEscape(const char* str, size_t len, char* output) {
  for (size_t i = 0; i < len; ++i) {
    char c = str[i];
    if (c == '"' || c == '\\') {
      // 转义逻辑
      *output++ = '\\';
      *output++ = c;
    } else {
      *output++ = c;
    }
  }
}

// 新版 SWAR 示例：检查短字符串 chunk 是否有需转义字符
uint64_t has_escape(uint64_t chunk) {
  // 位运算魔法：检测 '"' (0x22)、'\\' (0x5C) 等
  const uint64_t quote_mask = chunk ^ 0x2222222222222222ULL;  // XOR 匹配所有位置的引号
  const uint64_t backslash_mask = chunk ^ 0x5C5C5C5C5C5C5C5CULL;
  // 结合高位检查 (sign bit)
  uint64_t quote_high = quote_mask & 0x8080808080808080ULL;
  uint64_t bs_high = backslash_mask & 0x8080808080808080ULL;
  return (quote_high | bs_high) != 0;  // 如果非零，有转义
}

// 使用：如果 has_escape(chunk) == 0，直接 memcpy(chunk) 拷贝整块；否则，逐个处理
```

这个 SWAR 让短字符串扫描超快。长字符串 SIMD 类似，但用向量指令如 Neon 的 vceq_u8（相等比较）。结果？转义部分速度提升显著，尤其大字符串。

另外，混合编码字符串无缝切换：检测到双字节，就跳到双字节版本。

## 优化黑科技三：属性键的“快速通道” (Express Lane)

对象键通常是字符串。V8 加了个“快速通道”（Express Lane），专门优化属性键的迭代过程，消除多余检查。

详细来说：他们给对象的隐藏类（hidden class，V8 内部用来优化对象形状的机制）加了个标志。如果一个对象的所有属性键满足这些条件——不是 Symbol、可枚举、且键字符串无需转义（没引号、反斜杠等特殊字符）——就标记这个隐藏类为“fast-json-iterable”。当下次遇到同形状的对象时（比如数组里一堆类似对象），V8 直接跳过键的验证：不用检查类型、可枚举性、转义扫描，而是批量直接拷贝键到输出缓冲区。

类比：第一次安检全查，后面熟客直接过绿通道。尤其在处理大数组（比如上千个统一结构的对象）时，这省时巨大，因为键重复率高，避免了成千上万次的重复检查。这优化还顺带惠及 `JSON.parse`，加速键比较。

代码示例：实际在 V8 C++ 中实现，但咱们想象 JS 版简化逻辑：

```javascript
// 模拟隐藏类标志
const hiddenClassFlags = new Map();

// 检查并标记
function markFastIterable(obj) {
  const keys = Object.keys(obj);
  for (const key of keys) {
    if (typeof key !== "string" || key.includes('"') || key.includes("\\")) {
      return false; // 不合格
    }
  }
  hiddenClassFlags.set(obj.constructor, true); // 标记形状
  return true;
}

// stringify 时用
function fastKeyCopy(key) {
  if (hiddenClassFlags.get(/* obj 的形状 */)) {
    return key; // 直接拷贝，无检查
  } else {
    // 旧版检查...
  }
}
```

实际更复杂，但这展示了标志怎么加速。

## 优化黑科技四：数字转换和缓冲区革新

- **数字转字符串**：换成 Dragonbox 算法，比 Grisu3 快，还生成最短字符串。所有 Number.toString() 都受益！Dragonbox 用更高效的数学方法（基于浮点表示的龙算法变体）计算最短表示，避免 Grisu3 的多轮迭代和分支。

  类比：Grisu3 像手工计算小数位；Dragonbox 像用计算器，一步到位。

  代码示例（伪 JS，展示使用）：实际 V8 内部，但咱们对比：

  ```javascript
  // 旧版 Grisu3 模拟（简化，实际 C++）
  function grisu3ToString(num) {
    // 多步迭代、分支计算位数
    let digits = [];
    // ... 复杂逻辑，可能多轮循环
    return digits.join("");
  }

  // 新版 Dragonbox 模拟（简化）
  function dragonboxToString(num) {
    // 直接计算最短表示，少分支
    const { significand, exponent } = decomposeFloat(num);
    // 快速移位和乘法生成字符串
    return formatShortest(significand, exponent);
  }

  console.log(dragonboxToString(3.1415926535)); // "3.1415926535" 更快
  ```

> 代码参考： https://github.com/jk-jeon/dragonbox

- **分段缓冲区**：旧版用一个大缓冲，不停扩容复制。新版用小块链表缓冲（Zone 分配），写满一个接下一个，无拷贝。

  类比：旧版像写日记，一本写满抄到大本；新版像活页夹，随写随加页。最后组装成完整字符串。

  代码示例（伪 C++，参考 V8）：

  ```cpp
  // 旧版单一缓冲
  char* buffer = new char[initial_size];
  size_t pos = 0;
  while (writing) {
    if (pos >= current_size) {
      // 扩容并拷贝：慢！
      char* new_buffer = new char[current_size * 2];
      memcpy(new_buffer, buffer, pos);
      delete[] buffer;
      buffer = new_buffer;
      current_size *= 2;
    }
    // 写数据
    buffer[pos++] = 'a';
  }

  // 新版分段缓冲
  struct Segment { char data[4096]; size_t used; Segment* next; };
  Segment* head = new Segment();  // Zone 分配
  Segment* current = head;
  size_t pos = 0;
  while (writing) {
    if (pos >= 4096) {
      // 新段，无拷贝
      current->next = new Segment();
      current = current->next;
      pos = 0;
    }
    // 写数据
    current->data[pos++] = 'a';
  }
  // 最后组装：遍历链表拷贝到最终字符串
  ```

  这避免了频繁拷贝，尤其大对象时。

## 实际效果和对比

在 JetStream2 测试中，新版速度提升 2 倍以上！跨平台（桌面、移动）都行。限制：复杂对象 fallback 旧版。

用表格对比旧新：

| 方面       | 旧版               | 新版                  |
| ---------- | ------------------ | --------------------- |
| 遍历方式   | 递归               | 迭代                  |
| 字符串转义 | 逐字符检查         | SIMD/SWAR 批量        |
| 键检查     | 每次属性都查       | 隐藏类标志 + 批量拷贝 |
| 数字转换   | Grisu3             | Dragonbox             |
| 缓冲区     | 单大数组，频繁拷贝 | 分段链表，无拷贝      |
| 速度提升   | 基准               | >2x (JetStream2)      |

如果你好奇性能图，这里是 V8 官方的 JetStream2 对比图（来源：V8 博客），新版柱子高一倍！

## 总结与建议

通过这些优化，V8 让 `JSON.stringify` 从“老牛车”变“高铁”，尤其适合纯数据场景。实际开发中，保持对象简单，就能享受到加速。

想深入？去 [V8 博客](https://v8.dev/blog/json-stringify)，或自己测测性能：用大对象 benchmark 旧新 Chrome。

记住，优化不是魔法，是针对痛点的工程。边看边试代码，你也能掌握！有问题，欢迎评论交流。下次见~
