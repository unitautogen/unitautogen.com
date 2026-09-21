# unitautogen.com

The UnitAutogen website. One Jekyll site, built by GitHub Pages on every push. No CI, no local build needed.

## Layout

```
_config.yml            site settings, default nav/footer, post defaults
_layouts/default.html  the one page skeleton: <head>, header, footer
_layouts/post.html     blog article wrapper (title, byline, back links)
assets/css/site.css    the one stylesheet
assets/                images, logo
index.html             home
sql-server.html        product page
postgresql.html        product page
blog/index.html        blog listing (loops over _posts)
_posts/                one file per post: YYYY-MM-DD-slug.html  ->  /blog/slug.html
feed.xml, sitemap.xml  generated (jekyll-feed, jekyll-sitemap)
```

Every page starts with a front-matter block (between `---` lines): title, description, and optionally its own `nav` and `footer_*`. Everything after the block is the page body only. Header, footer and CSS come from the layout.

## Publishing (first time)

1. Repo: `unitautogen/unitautogen.com` (already created). Push this folder to it (GitHub Desktop).
2. Repo Settings -> Pages -> Build and deployment: Source "Deploy from a branch", Branch `main`, folder `/ (root)`. Save.
3. Wait about a minute. The site is at `https://unitautogen.github.io/unitautogen.com/` (`baseurl` in `_config.yml` is set for this). The Actions tab shows the "pages build and deployment" run if anything fails.

## Cut-over to unitautogen.com (done 2026-09-21; kept for reference)

1. In the SQL Server repo (`unitautogen-public-repo`): delete `CNAME`, `index.html`, `sql-server.html`, `postgresql.html`, `blog/`, `feed.xml`, `assets/` (keep `docs/`). Push.
2. In this repo: add a `CNAME` file containing `unitautogen.com`; in `_config.yml` set `url: "https://unitautogen.com"` and `baseurl: ""`. Push.
3. Repo Settings -> Pages -> Custom domain: `unitautogen.com`, tick "Enforce HTTPS" once the check passes.
4. DNS stays as it is (it already points at GitHub Pages).

## Day to day

- New blog post: add `_posts/2026-10-05-my-slug.html` with a front-matter block (`title`, `date`, `description`, `excerpt`) and the article body (HTML or Markdown, use `.md` for Markdown). The listing and feed update themselves.
- New page: copy `postgresql.html`, change the front matter and body.
- Change the header/footer/CSS once in `_layouts/default.html` / `assets/css/site.css`.

## Local preview (optional)

Needs Ruby. Then:

```
gem install bundler
bundle install
bundle exec jekyll serve
```

Opens at `http://localhost:4000/`.
