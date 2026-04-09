#!/usr/bin/env python3
"""
Build script for stym06.github.io

Converts markdown files in content/posts/ to HTML pages.
Updates the writing listing page and homepage.

Usage:
    ./build.py              # build all posts
    ./build.py my-post.md   # build a single post

Markdown frontmatter format:
    ---
    title: My Post Title
    date: 2024-07-11
    reading_time: 4 min read
    ---
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path

import markdown
from markdown.extensions.fenced_code import FencedCodeExtension

ROOT = Path(__file__).parent
CONTENT_DIR = ROOT / "content" / "posts"
POSTS_DIR = ROOT / "posts"
POSTS_INDEX = POSTS_DIR / "index.html"
HOME_INDEX = ROOT / "index.html"


def parse_frontmatter(text):
    """Extract YAML-like frontmatter and body from markdown text."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', text, re.DOTALL)
    if not match:
        return {}, text

    meta = {}
    for line in match.group(1).strip().split('\n'):
        key, _, value = line.partition(':')
        meta[key.strip()] = value.strip()

    return meta, match.group(2)


def md_to_html(md_text):
    """Convert markdown to HTML."""
    md = markdown.Markdown(extensions=[
        FencedCodeExtension(),
        'markdown.extensions.tables',
    ])
    return md.convert(md_text)


def format_date_short(date_str):
    """2024-07-11 -> Jul 11, 2024"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%b %-d, %Y")


def format_date_month(date_str):
    """2024-07-11 -> Jul 2024"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%b %Y")


def slug_from_filename(filename):
    """my-post.md -> my-post"""
    return Path(filename).stem


def build_post_html(meta, content_html):
    """Generate full HTML page for a blog post."""
    title = meta.get('title', 'Untitled')
    date = meta.get('date', '')
    reading_time = meta.get('reading_time', '')
    date_display = format_date_short(date) if date else ''
    meta_text = date_display
    if reading_time:
        meta_text += f" &middot; {reading_time}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} - Satyam Raj</title>
  <meta name="description" content="{title}">
  <meta name="author" content="Satyam Raj">
  <link rel="icon" href="/favicon.ico">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <meta property="og:title" content="{title}">
  <meta property="og:type" content="article">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{title}">
  <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
  <div class="container">
    <nav>
      <ul>
        <li><a href="/">home</a></li>
        <li><a href="/posts/">writing</a></li>
        <li><a href="/projects/">projects</a></li>
        <li><a href="/about/">about</a></li>
      </ul>
    </nav>

    <main>
      <a href="/posts/" class="back-link">&larr; back to writing</a>

      <article>
        <header class="post-header">
          <h1>{title}</h1>
          <div class="post-meta">{meta_text}</div>
        </header>

        <div class="post-content">
          {content_html}
        </div>
      </article>
    </main>

    <footer>
      &copy; 2026 Satyam Raj
    </footer>
  </div>
</body>
</html>
"""


def build_writing_page(posts):
    """Generate the /posts/index.html listing page."""
    items = ""
    for post in posts:
        date_display = format_date_short(post['date']) if post['date'] else ''
        items += f"""        <li>
          <a href="/posts/{post['slug']}/">{post['title']}</a>
          <span class="date">{date_display}</span>
        </li>\n"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Writing - Satyam Raj</title>
  <meta name="description" content="Blog posts about databases, distributed systems, and software engineering.">
  <meta name="author" content="Satyam Raj">
  <link rel="icon" href="/favicon.ico">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="alternate" type="application/rss+xml" title="Satyam Raj" href="/index.xml">
  <meta property="og:title" content="Writing - Satyam Raj">
  <meta property="og:type" content="website">
  <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
  <div class="container">
    <nav>
      <ul>
        <li><a href="/">home</a></li>
        <li><a href="/posts/" class="active">writing</a></li>
        <li><a href="/projects/">projects</a></li>
        <li><a href="/about/">about</a></li>
      </ul>
    </nav>

    <main>
      <section class="intro">
        <h1>Writing</h1>
      </section>

      <hr>

      <ul class="post-list">
{items}      </ul>
    </main>

    <footer>
      &copy; 2026 Satyam Raj
    </footer>
  </div>
</body>
</html>
"""


def build_all():
    """Build all posts and update listing pages."""
    md_files = sorted(CONTENT_DIR.glob("*.md"))

    if not md_files:
        print("No markdown files found in content/posts/")
        return

    posts = []

    for md_file in md_files:
        text = md_file.read_text()
        meta, body = parse_frontmatter(text)
        slug = slug_from_filename(md_file.name)
        content_html = md_to_html(body)

        meta['slug'] = slug
        posts.append({
            'title': meta.get('title', 'Untitled'),
            'date': meta.get('date', ''),
            'reading_time': meta.get('reading_time', ''),
            'slug': slug,
        })

        # Write post HTML
        post_dir = POSTS_DIR / slug
        post_dir.mkdir(parents=True, exist_ok=True)
        post_html = build_post_html(meta, content_html)
        (post_dir / "index.html").write_text(post_html)
        print(f"  built: posts/{slug}/index.html")

    # Sort by date descending
    posts.sort(key=lambda p: p['date'], reverse=True)

    # Update writing listing page
    writing_html = build_writing_page(posts)
    POSTS_INDEX.write_text(writing_html)
    print(f"  built: posts/index.html")

    print(f"\nDone! {len(posts)} posts built.")


def build_single(filename):
    """Build a single post by filename."""
    md_file = CONTENT_DIR / filename
    if not md_file.exists():
        print(f"File not found: {md_file}")
        sys.exit(1)

    text = md_file.read_text()
    meta, body = parse_frontmatter(text)
    slug = slug_from_filename(filename)
    content_html = md_to_html(body)

    meta['slug'] = slug

    post_dir = POSTS_DIR / slug
    post_dir.mkdir(parents=True, exist_ok=True)
    post_html = build_post_html(meta, content_html)
    (post_dir / "index.html").write_text(post_html)
    print(f"  built: posts/{slug}/index.html")

    # Rebuild listing with all posts
    build_listing()


def build_listing():
    """Rebuild just the writing listing page from all markdown files."""
    md_files = sorted(CONTENT_DIR.glob("*.md"))
    posts = []
    for md_file in md_files:
        text = md_file.read_text()
        meta, _ = parse_frontmatter(text)
        posts.append({
            'title': meta.get('title', 'Untitled'),
            'date': meta.get('date', ''),
            'slug': slug_from_filename(md_file.name),
        })
    posts.sort(key=lambda p: p['date'], reverse=True)
    writing_html = build_writing_page(posts)
    POSTS_INDEX.write_text(writing_html)
    print(f"  built: posts/index.html")


if __name__ == "__main__":
    print("Building site...\n")
    if len(sys.argv) > 1:
        build_single(sys.argv[1])
    else:
        build_all()
