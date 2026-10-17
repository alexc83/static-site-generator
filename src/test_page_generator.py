from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from page_generator import extract_title, generate_page, generate_pages_recursive


class TestExtractTitle(unittest.TestCase):
    def test_title(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_trims_title_whitespace(self):
        self.assertEqual(extract_title("#   Hello, world! \t"), "Hello, world!")

    def test_finds_h1_after_other_content(self):
        self.assertEqual(extract_title("## Subtitle\n\nParagraph\n\n# Title"), "Title")

    def test_returns_first_h1(self):
        self.assertEqual(extract_title("# First\n\n# Second"), "First")

    def test_preserves_hashes_within_title(self):
        self.assertEqual(extract_title("# A # in the title"), "A # in the title")

    def test_missing_h1(self):
        for markdown in ("", "Paragraph", "## Heading", "### Heading", "#No space", "# "):
            with self.subTest(markdown=markdown):
                with self.assertRaisesRegex(ValueError, "h1 heading"):
                    extract_title(markdown)


class TestGeneratePage(unittest.TestCase):
    def test_generates_page_and_creates_destination_directories(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "index.md"
            template = root / "template.html"
            destination = root / "public" / "nested" / "index.html"
            source.write_text("# Café\n\nA **bold** paragraph.", encoding="utf-8")
            template.write_text(
                "<html><title>{{ Title }}</title><body>{{ Content }}</body></html>",
                encoding="utf-8",
            )

            generate_page(source, template, destination)

            self.assertEqual(
                destination.read_text(encoding="utf-8"),
                "<html><title>Café</title><body><div><h1>Café</h1>"
                "<p>A <b>bold</b> paragraph.</p></div></body></html>",
            )


class TestGeneratePagesRecursive(unittest.TestCase):
    def test_basepath_reaches_nested_pages(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            content = root / "content"
            nested = content / "blog" / "post"
            nested.mkdir(parents=True)
            (nested / "index.md").write_text(
                "# Post\n\n[Home](/) ![Image](/images/test.png) [External](https://example.com)",
                encoding="utf-8",
            )
            template = root / "template.html"
            template.write_text(
                '<title>{{ Title }}</title><link href="/index.css">{{ Content }}',
                encoding="utf-8",
            )

            generate_pages_recursive(content, template, root / "docs", "/my-repo/")

            html = (root / "docs/blog/post/index.html").read_text(encoding="utf-8")
            self.assertIn('href="/my-repo/index.css"', html)
            self.assertIn('href="/my-repo/"', html)
            self.assertIn('src="/my-repo/images/test.png"', html)
            self.assertIn('href="https://example.com"', html)

    def test_nested_pages_share_template_and_preserve_static_files(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            content = root / "content"
            destination = root / "public"
            template = root / "template.html"
            pages = {
                "index.md": ("Home", "[Post](/blog/post)"),
                "blog/post/index.md": ("Post", "[Home](/)"),
                "contact/details.md": ("Contact", "Call me."),
            }
            for relative_path, (title, body) in pages.items():
                source = content / relative_path
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text(f"# {title}\n\n{body}", encoding="utf-8")
            (content / "notes.txt").write_text("Ignore this file", encoding="utf-8")
            destination.mkdir()
            (destination / "index.css").write_text("body {}", encoding="utf-8")
            template.write_text(
                "<title>{{ Title }}</title><article>{{ Content }}</article>",
                encoding="utf-8",
            )

            generate_pages_recursive(content, template, destination)

            self.assertEqual(
                {path.relative_to(destination).as_posix() for path in destination.rglob("*.html")},
                {"index.html", "blog/post/index.html", "contact/details.html"},
            )
            for relative_path, (title, _) in pages.items():
                html = (destination / Path(relative_path).with_suffix(".html")).read_text(
                    encoding="utf-8"
                )
                self.assertIn(f"<title>{title}</title>", html)
                self.assertIn(f"<h1>{title}</h1>", html)
                self.assertNotIn("{{ Content }}", html)
            self.assertIn(
                '<a href="/blog/post">Post</a>',
                (destination / "index.html").read_text(encoding="utf-8"),
            )
            self.assertIn(
                '<a href="/">Home</a>',
                (destination / "blog/post/index.html").read_text(encoding="utf-8"),
            )
            self.assertFalse((destination / "notes.txt").exists())
            self.assertEqual((destination / "index.css").read_text(encoding="utf-8"), "body {}")


if __name__ == "__main__":
    unittest.main()
