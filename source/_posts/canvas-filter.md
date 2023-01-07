---
title: 『不要再问我头像如何变灰了，试试这几种滤镜吧！』
tags: [Canvas, 图片处理, 滤镜]
date: 2020-04-12
---

在实际的工作中，有时候会有一些需求，让你做一些图片的滤镜效果，比如将图片变成黑白，调整图片亮度等。本文手把手教你如何实现`五种滤镜效果`，核心代码总共不到 70 行。

笔者所在的公司就有一个需求需要用到图片处理的知识，大概场景我来描述一下：

用户可以手动上传印章，并且支持给印章设置不同的显示效果，这里的效果具体指的是“线条的清晰程度”，如下图所示：

![](https://p.ipic.vip/c246jq.jpg)

这里我们使用 Canvas 来实现。如果你对 Canvas 不熟悉，建议看下之前我写的一篇文章[100 \* 100 Canvas 占用内存多大](https://cloud.tencent.com/developer/article/1494747)，花上几分钟看完，基本上够看懂这篇文章了。

<!-- more -->

## 准备工作

首先我们先将图片绘制到 Canvas 画布上，为了简单起见，图片大小固定为 300 x 300。

```html
<canvas id="canvas" width="300px" height="300px"></canvas>
```

(html)

```js
//获取canvas元素
ctx = document.getElementById("canvas").getContext("2d");
//创建image对象
var img = new Image();
img.src = require("./seal.png");
//待图片加载完后，将其显示在canvas上
img.onload = () => {
  ctx.drawImage(img, 0, 0);
  this.imgData = ctx.getImageData(0, 0, 300, 300);
};
```

(js)

效果是这样的：

![](https://p.ipic.vip/0tohtm.jpg)

## 操作像素

熟悉 Canvas 的应该知道上面的 this.imgData 实际上就是[ImageData](https://developer.mozilla.org/zh-CN/docs/Web/API/ImageData)类的实例，其中 imgData.data 是一个 Uint8ClampedArray， 其描述了一个一维数组，包含以 RGBA 顺序的数据，数据使用 0 至 255（包含）的整数表示。 简单来说，就是`图片像素信息，每四位表示一个像素单元`。其中每四位的信息分别是 RGBA。即第一个 Bit 标记 R，第二个 Bit 表示 G，第三个 Bit 表示 B，第四个 Bit 表示 A，第五个 Bit 又是 R...，依次类推。

![](https://p.ipic.vip/pleai1.jpg)

接下来，我们就要操作 imgData，来实现滤镜的效果。简单起见，我这里对超过 200 的值进行了一次`提高亮度`的操作。实际上这个值是 200，还是别的数字，需要我们化身"调参工程师"，不断实验才行。 并且粗暴地对 RGB 执行同样的逻辑是不合理的。更为合理的做法是对 RGB 的阀值分别进行度量，由于比较麻烦，我这里没有实现。但是如果你对效果要求比较高，那么最好可以分开度量。

```js
const data = this.imgData.data;
for (let i = 0; i < data.length; i += 4) {
  if (data[i] < 200) {
    data[i] = data[i] + brightness > 255 ? 255 : data[i] + brightness;
  }

  if (data[i + 1] < 200) {
    data[i + 1] =
      data[i + 1] + brightness > 255 ? 255 : data[i + 1] + brightness;
  }
  if (data[i + 2] < 200) {
    data[i + 2] =
      data[i + 2] + brightness > 255 ? 255 : data[i + 2] + brightness;
  }
}
```

如上，我们对图片的像素进行了处理，以达到我们的目的，这样从用户感官上来看，显示效果发生了变化，大概效果如图：

![](https://p.ipic.vip/dmihq9.jpg)

（清晰版）

![](https://p.ipic.vip/tal3ui.jpg)

（模糊版）

> 如果你愿意的话，你也可以将处理好的图片进行导出，也很简单，直接调用 Canvas 实例的 `toDataURL` 方法即可，图片保存的格式也可以在这个方法中进行指定。

日常开发中，我们还可能碰到很多其他的滤镜效果。下面介绍几个比较现常见的效果。 如果你正好用到了不妨作为参考。如果遇到了新的滤镜效果， 不妨在文末向我留言，看到后会及时回答，提前感谢你的参与。

下面介绍其他四种滤镜效果。这里只贴出核心代码，完整代码可以访问我的 [Github Repo](https://github.com/azl397985856/canvas-filter-demo) 进行查看。如果你嫌下载到本地麻烦，也可以在这里[在线安装并访问](https://ec08f895-51be-4f77-8b7f-04fc08a9f443.ws-us02.gitpod.io/#/workspace/canvas-filter-demo)，打开这个链接，分别执行`yarn`和`yarn start`即可。

以下效果均以下图为原图制作：

![](https://p.ipic.vip/uxxgga.jpg)

## 如何实现黑白效果

![](https://p.ipic.vip/ugkrg0.jpg)

```js
for (let i = 0; i < data.length; i += 4) {
  // 将红黄蓝按照一定比例混合，具体比例为0.299 : 0.587 : 0.114， 这个比例需要慢慢调制。
  const avg = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
  data[i] = data[i + 1] = data[i + 2] = avg;
}
```

## 如何实现反色效果

![](https://p.ipic.vip/wqv4in.jpg)

```js
for (let i = 0; i < data.length; i += 4) {
  data[i] = 255 - data[i]; //r
  data[i + 1] = 255 - data[i + 1]; //g
  data[i + 2] = 255 - data[i + 2]; //b
}
```

## 如何给图片增加噪音

![](https://p.ipic.vip/zxan9d.jpg)

```js
const random = ((Math.random() * 70) >>> 0) - 35;
for (let i = 0; i < data.length; i += 4) {
  data[i] = data[i] + random;
  data[i + 1] = data[i + 1] + random;
  data[i + 2] = data[i + 2] + random;
}
```

## 如何提高图片亮度

![](https://p.ipic.vip/cjk1pu.jpg)

![](https://p.ipic.vip/wq5ubk.jpg)

```js
const brightness = +e.target.value;
for (let i = 0; i < data.length; i += 4) {
  data[i] = data[i] + brightness > 255 ? 255 : data[i] + brightness;
  data[i + 1] = data[i + 1] + brightness > 255 ? 255 : data[i + 1] + brightness;
  data[i + 2] = data[i + 2] + brightness > 255 ? 255 : data[i + 2] + brightness;
}
```

# 总结

本文通过不到 70 行代码实现了`五种滤镜效果`，对于其他滤镜效果也可以参考这种方式来实现。还不赶紧拿上小姐姐的照片来秀一手么？
