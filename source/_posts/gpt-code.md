---
title: 如何自己搭建一个 GPT 代码生成器？
tags: [ai, chatgpt, 代码生成器]
categories: [ai]
date: 2024-07-13
---

自从 chatpgt 发布以来，有很多人都在使用它来生成代码，然后包装成一个产品给大家使用。有的甚至是付费的，用它来赚钱。

使用方式基本上都是：

1. 你输入一个问题，然后它会给你生成一个代码片段。这个代码片段可能是一个函数，也可能是一个类，也可能是一个模块，甚至直接是一个代码库。
2. 你可以选择使用这个代码片段，也可以继续输入问题，让它生成更多的代码片段。或者对答案进行改进
3. 如果你对答案满意，你可以将答案复制到你的项目中，或者导出代码。

![](https://p.ipic.vip/vydqqw.png)

![](https://p.ipic.vip/gufjyx.png)

这样的一款产品是怎么做出来的？代码复杂吗？我可以自己做一个吗？自己做的话，需要多少时间，多少钱？

<!-- more -->

## 三步搭建一个 GPT 代码生成器

实际上做一个这样的产品并不难，甚至也不需要花钱。

只需要几个步骤：

1. 你需要一个 chatgpt 的 API Key，这个可以通过多种渠道获得，可以是免费的，只不过会有一些限制，比如每天只能调用多少次，或者只能调用多少次之后就要付费。
2. 你需要一个前端页面，用来接收用户的输入，然后调用后端 API，将用户的输入传过去即可，等待后端响应后将结果展示给用户。 更进一步，我们甚至可以在前端直接预览效果。
3. 你需要一个后端服务，用来接收前端传过来的问题，然后调用 chatgpt 的 API，将问题传过去，等待 chatgpt 的响应，然后将响应返回给前端。

这样一个产品就做好了。

对于第一点，获取 chatgpt 的 API Key，可以通过官方网站申请，也可以通过一些第三方网站购买。比如 [openai](https://openai.com)。

对于第二点，前端页面可以写的非常简单，直接一个 input 输入框，一个按钮，然后一个 div 用来展示 chatgpt 返回的代码片段即可。这样根本花不了多少时间。

对于第三点，新增一个后端路由，然后调用 chatgpt 也非常简单。不过我需要额外补充一下。那就是如果将用户的输入无脑传给 chatgpt，那么 chatgpt 会返回一个代码片段，但是这个代码片段可能是不符合你的预期的。因为 chatgpt 生成的代码片段是基于你的输入的，如果你的输入不够详细，那么生成的代码片段可能会有问题。

因此，我们可以在后端对 chatgpt 的响应进行处理。增加一些 prompt，让 chatgpt 生成的代码片段更符合我们的预期。

比如如下代码就是在用户的输入前面加了一些提示，让 chatgpt 生成的代码片段更如何一个专业前端的代码片段，并且不要加注释，并且指定了 ui 库。甚至增加了一个示例，让 chatgpt 书写风格更符合我们的预期。

```js
// prompt 是用户输入的问题
// currentCode 是上一步 chatgpt 返回的代码片段
// uiMode 是指定的 ui 库
// uiExample 是指定的 ui 库的示例代码
const detailedPrompt = `
Blow is the existing code，I wrapped it in a code block for better readability:
\`\`\`jsx
${currentCode}
\`\`\`

Please make the following changes:
${prompt}

Return the complete and functional implementation code without any additional explanations and any markdown code block markers.
`;
const messages = [
  {
    role: "system",
    content: `You are a professional front-end developer. Only provide the complete and functional implementation code without any additional explanations and any markdown code block markers, whether modifying existing code or writing from scratch.
                always use ${uiMode} for the implementation. Here is a example :
                \`\`\`jsx
                ${uiExample}
                \`\`\
                `,
  },
  { role: "user", content: detailedPrompt },
];
```

## 总结

自己搭建一个 GPT 代码生成器并不难，只需要几个步骤，就可以做出一个产品。不过需要注意的是，chatgpt 生成的代码片段可能不符合你的预期，因此需要在后端对 chatgpt 的响应进行处理，增加一些 prompt，让 chatgpt 生成的代码片段更符合我们的预期。

这里我给大家一个参考的项目 [gpt-frontend-code-gen](https://github.com/bravekingzhang/gpt-frontend-code-gen) ，这个项目是一个 GPT 代码生成器，你可以参考这个项目，自己搭建一个 GPT 代码生成器。