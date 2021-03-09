import moment from 'moment';
import { extract } from 'keyword-extractor';
import { stripHTML } from 'hexo-util';

var defaults = {
  pages: {
    raw: false,
    content: false,
    title: true,
    slug: true,
    date: true,
    updated: true,
    comments: true,
    path: true,
    link: true,
    permalink: true,
    excerpt: true,
    text: true,
    keywords: true,
    author: true
  },

  posts: {
    raw: false,
    content: false,
    title: true,
    slug: true,
    date: true,
    updated: true,
    comments: true,
    path: true,
    link: true,
    permalink: true,
    excerpt: true,
    text: true,
    categories: true,
    tags: true,
    keywords: true,
    author: true
  }
};

function ignoreSettings (cfg) {
  const ignore = cfg.ignore ? cfg.ignore : {};

  ignore.paths = ignore.paths ? ignore.paths.map(path => path.toLowerCase()) : [];

  ignore.tags = ignore.tags ? ignore.tags.map(tag => tag.replace('#', '').toLowerCase()) : [];

  return ignore
}

function isIgnored (content, settings) {
  if (content.hidden === false) { return false }

  if (content.password || content.hidden) { return true }

  const pathIgnored = settings.paths.find(path => content.path.includes(path));

  if (pathIgnored) { return true }

  const tags = content.tags ? content.tags.map(mapTags) : [];
  const tagIgnored = tags.filter(tag => settings.tags.includes(tag)).length;

  if (tagIgnored) { return true }

  return false
}

function mapTags (tag) {
  return typeof tag === 'object' ? tag.name.toLowerCase() : tag
}

function has (obj, key) {
  return Object.prototype.hasOwnProperty.call(obj, key)
}

function minify (str) {
  return stripHTML(str).trim().replace(/\s+/g, ' ')
}

function getProps (ref) {
  return Object.getOwnPropertyNames(ref).filter(item => ref[item])
}

function catags ({ name, slug, permalink }) {
  return { name, slug, permalink }
}

function getKeywords (str, language) {
  const keywords = extract(str, {
    language,
    remove_digits: true,
    return_changed_case: true,
    remove_duplicates: true
  });

  return keywords.join(' ')
}

function setContent (obj, item, ref, cfg) {
  switch (item) {
    case 'excerpt':
      obj.excerpt = minify(ref.excerpt);
      break

    case 'text':
      obj.text = minify(ref.content);
      break

    case 'keywords':
      if (cfg.keywords) {
        const excerpt = minify(ref.excerpt);
        obj.keywords = getKeywords(excerpt, cfg.keywords);
      }
      break

    case 'categories':
      obj.categories = ref.categories.map(catags);
      break

    case 'tags':
      obj.tags = ref.tags.map(catags);
      break

    case 'date':
      obj.date = cfg.dateFormat ? moment(ref.date).format(cfg.dateFormat) : ref.date;
      break

    case 'updated':
      obj.updated = cfg.dateFormat ? moment(ref.updated).format(cfg.dateFormat) : ref.updated;
      break

    default:
      obj[item] = ref[item];
  }

  return obj
}

function reduceContent (names, content, cfg) {
  return names.reduce((obj, item) => setContent(obj, item, content, cfg), {})
}

const { config } = hexo;
const defs = { meta: true };
const opts = config.jsonContent || {};
const json = { ...defs, ...opts };
const pages = has(json, 'pages') ? json.pages : defaults.pages;
const posts = has(json, 'posts') ? json.posts : defaults.posts;
const ignore = ignoreSettings(json);

let output = json.meta ? {
  meta: {
    title: config.title,
    subtitle: config.subtitle,
    description: config.description,
    author: config.author,
    url: config.url,
    root: config.root
  }
} : {};

hexo.extend.generator.register('json-content', site => {
  if (pages) {
    const pagesNames = getProps(pages);
    const pagesValid = site.pages.filter(page => !isIgnored(page, ignore));
    const pagesContent = pagesValid.map(page => reduceContent(pagesNames, page, json));

    if (posts || json.meta) {
      output.pages = pagesContent;
    } else {
      output = pagesContent;
    }
  }

  if (posts) {
    const postsNames = getProps(posts);
    const postsSorted = site.posts.sort('-date');
    const postsValid = postsSorted.filter(post => {
      const include = json.drafts || post.published;
      return include && !isIgnored(post, ignore)
    });
    const postsContent = postsValid.map(post => reduceContent(postsNames, post, json));

    if (pages || json.meta) {
      output.posts = postsContent;
    } else {
      output = postsContent;
    }
  }

  return {
    path: json.file || 'content.json',
    data: JSON.stringify(output)
  }
});
