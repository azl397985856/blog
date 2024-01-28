---
title: 关于 Error Boundaries， 你需要知道的一切
date: 2024-01-28
tags: [前端, 异常处理]
categories:
  - [前端]
---

在我们的应用中，难免会遇到一些异常情况，比如网络请求失败，或者是用户输入了一些非法的数据等等。这些异常情况如果没有得到处理，就会导致应用崩溃，从而影响用户体验。而 Error Boundaries 就是用可以处理这些异常情况中的一部分。

<!-- more -->

## 什么是 Error Boundaries

Error Boundaries 是 React 16 引入的一个新特性，用于捕获子组件树在渲染过程中抛出的异常，从而避免整个组件树的崩溃。

使用方法很简单，只需要定义一个组件，实现 `componentDidCatch` 和 `render` 方法即可。

一般而言，我们会在 getDerivedStateFromError 中将状态设置为 true， 然后 render 中根据这个设置的状态来渲染不同内容。如下代码所示：

```jsx
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    // Example "componentStack":
    //   in ComponentThatThrows (created by App)
    //   in ErrorBoundary (created by App)
    //   in div (created by App)
    //   in App
    logErrorToMyService(error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return this.props.fallback;
    }

    return this.props.children;
  }
}
```

## Error Boundaries 的好处与限制

Error Boundaries 的好处是显而易见的，它可以避免一个组件错误导致整个页面无法正常渲染的问题。

尽管 Error Boundaries 可以捕获子组件树中的异常，从而避免一个组件错误导致整个页面无法正常渲染的问题。但是它也有一些限制：

1. 只能捕获子组件树中的异常，不能捕获自身组件树中的异常。
2. 不能捕获事件处理器中的异常。
3. 不能捕获异步渲染中的异常。
4. 不能捕获服务端渲染中的异常。
5. 不能捕获自身组件的构造函数中的异常。

对于这些问题，我们必须结合其他的异常处理机制来解决，本文不再赘述。

## Error Boundaries 的底层实现原理

Error Boundaries 的底层实现原理是什么呢？

遇到错误的时候，React 首先做的是捕获到这个错误，接下来将这个错误交给 componentDidCatch 来处理。类似我们在 JavaScript 中使用 try/catch 来捕获异常，然后在 catch 中处理异常。

我们可以通过源码来一探究竟。

```jsx
function handleError(root, errorInfo) {
  // Call componentDidCatch or handleError on the boundaries below us
  let boundary = root;
  while (boundary) {
    const inst = getInst(boundary);
    if (inst !== null && typeof inst.componentDidCatch === 'function') {
      invokeGuardedCallbackAndCatchFirstError(
        'componentDidCatch',
        inst,
        errorInfo
      );
      return;
    } else if (typeof boundary.tag !== 'number') {
      // Host components don't have lifecycle methods
      // so we don't need to try to invoke them
      return;
    }
    boundary = boundary.return;
  }
}
```

可以看到，当一个组件抛出异常时，接下来 React 会从当前组件开始，向上遍历整个组件树，直到找到一个 Error Boundaries 组件，然后调用它的 componentDidCatch 方法。

## Error Boundaries 的异常恢复

我们期望在用户遇到错误的时候， 可以通过一定的方式来恢复应用的正常运行。比如，我们可以在 componentDidCatch 中调用 setState 来更新组件的状态，从而重新渲染组件。

由于 Error Boundaries 本质上是一个普通高阶 React 组件，因此我们可以通过重新给 children 设置 key 来触发组件的重新渲染。类似这样：

```jsx
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null, errorInfo: null };
  }

  componentDidCatch(error, errorInfo) {
    // Catch errors in any components below and re-render with error message
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    // You can also log error messages to an error reporting service here
  }

  retry() {
    this.setState({
      error: null,
      errorInfo: null,
      key: Math.random()
    });
  }

  render() {
    if (this.state.errorInfo) {
      // Error path
      return (
        <div>
          <h2 onClick={this.retry}>Something went wrong. Click to recover</h2>
          <details style={{ whiteSpace: 'pre-wrap' }}>
            {this.state.error && this.state.error.toString()}
            <br />
            {this.state.errorInfo.componentStack}
          </details>
        </div>
      );
    }
    // Normally, just render children
    return <React.Fragment key={this.state.key}>{this.props.children}</React.Fragment>
  }
}
```

组件的数据来源主要有 state 和 props。 另外我们也会用一些 store 中的数据，甚至有的人使用全局变量。

对于 state 和 props，甚至是 store，我们都可以很容易地使用上次没有报错的数据来重新渲染组件。不过对于全局变量，我们就无能为力了。因此我们尽量不要在组件中使用全局变量。这也是我们使用数据管理框架的原因。因为这样可以使得数据是可预见的。

## Error Boundaries 的上报

当我们遇到错误的时候，我们可以将错误信息上报到服务器，这样我们就可以知道用户遇到了什么问题，从而可以及时修复。

除了业务数据外，我们还可以将：

1. 组件树的结构上报到服务器，这样我们就可以知道用户遇到问题的时候，页面的结构是怎样的，从而可以更好地定位问题。
2. 组件的状态和属性传到后端，包括 hooks 数据等。
3. 页面上可以展示出一个 hash，然后将 hash 上报到后端。 当用户反馈问题到我们的时候，我们可以通过这个 hash 来找到这个问题，并定位问题原因。

## 如何处理错误边界

我们可以将 Error Boundaries 用于整个应用，也可以将 Error Boundaries 用于某个组件。如何决定呢？

一个原则是将相同业务功能的放到一起，用一个 Error Boundaries 来处理。这样一个功能挂了，相关功能也应该不可用。而不相关功能则期望是不受影响。这需要大家根据自己的业务来决定。

## 如何测试我们的应用的 Error Boundaries 是否合理？

我建议手动将每一个组件都抛出异常，然后看看 Error Boundaries：

1. 是否可以捕获到异常
2. 是否可以恢复应用的正常运行
3. 一个组件挂了后是否符合上一节我们提到的原则

如果觉得效率低，也可以写一个脚本来自动化测试。

## 总结

本文介绍了 Error Boundaries 的基本用法，以及它的好处与限制。同时我们也介绍了 Error Boundaries 的底层实现原理，以及如何在遇到错误的时候，恢复应用的正常运行。最后我们还介绍了如何将错误信息上报到服务器。

