#!/usr/bin/env python3
"""
把 wechat-ai-docs/*.md 里引用的远程图片下载到 images/，并把 md 里的远程链接改写为本地相对路径。
纯标准库实现（urllib + re + hashlib + pathlib），无需 pip 安装。
排除 res.wx.qq.com 域名下的 UI 装饰图标。
失败时在对应 md 顶部追加「图片下载失败：<url>」备注，保留原远程链接。
"""

import re
import time
import hashlib
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMAGES_DIR = ROOT / "images"
MD_FILES = sorted(ROOT.glob("*.md"))

REFERER = "https://developers.weixin.qq.com/"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
EXCLUDE_HOSTS = ("res.wx.qq.com",)  # UI 装饰图标，跳过
MAX_RETRIES = 2
TIMEOUT = 30

IMG_PATTERN = re.compile(r"!\[([^\]]*)\]\((https?://[^)]+)\)")
META_HEADER_RE = re.compile(r"^> 源页面：[^\n]+\n> 抓取时间：[^\n]+\n*", re.MULTILINE)


def short_hash(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]


def ext_from_url(url: str) -> str:
    path = url.split("?", 1)[0].split("#", 1)[0]
    ext = Path(path).suffix.lower()
    if ext not in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp"):
        ext = ".png"
    return ext


def filename_for(md_stem: str, seq: int, url: str) -> str:
    return f"{md_stem}-{seq:02d}-{short_hash(url)}{ext_from_url(url)}"


def download(url: str, dest: Path) -> bool:
    req = urllib.request.Request(
        url,
        headers={"Referer": REFERER, "User-Agent": USER_AGENT},
    )
    last_err = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                data = resp.read()
            dest.write_bytes(data)
            return True
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            last_err = e
            time.sleep(1 + attempt)
    print(f"  [FAIL] {url} -> {last_err}")
    return False


def process_md(md_path: Path) -> tuple[int, int, list[str]]:
    text = md_path.read_text(encoding="utf-8")
    md_stem = md_path.stem

    matches = list(IMG_PATTERN.finditer(text))
    if not matches:
        return 0, 0, []

    total = 0
    ok = 0
    failures: list[str] = []
    replacements: list[tuple[str, str]] = []

    for seq, m in enumerate(matches, start=1):
        alt = m.group(1)
        url = m.group(2)
        host = urllib.request.urlparse(url).hostname or ""

        if any(ex in host for ex in EXCLUDE_HOSTS):
            # 装饰图标，跳过下载并移除该 markdown 图片引用
            replacements.append((m.group(0), ""))
            total += 1
            continue

        total += 1
        local_name = filename_for(md_stem, seq, url)
        local_path = IMAGES_DIR / local_name
        if not local_path.exists():
            print(f"  [{md_stem}-{seq:02d}] {url}")
            if not download(url, local_path):
                failures.append(url)
                continue
        else:
            print(f"  [{md_stem}-{seq:02d}] (cached) {url}")
        ok += 1
        replacements.append((m.group(0), f"![{alt}](./images/{local_name})"))

    if replacements:
        for old, new in replacements:
            text = text.replace(old, new, 1)

    if failures:
        note_lines = "\n".join(f"> 图片下载失败：{u}" for u in failures)
        # 找到元信息头之后插入
        header_match = META_HEADER_RE.match(text)
        if header_match:
            insert_at = header_match.end()
            text = text[:insert_at] + note_lines + "\n\n" + text[insert_at:]
        else:
            text = note_lines + "\n\n" + text

    md_path.write_text(text, encoding="utf-8")
    return total, ok, failures


def main() -> int:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    grand_total = 0
    grand_ok = 0
    grand_fail: list[str] = []

    for md_path in MD_FILES:
        if md_path.name == "README.md":
            continue
        print(f"\n=== {md_path.name} ===")
        total, ok, fails = process_md(md_path)
        grand_total += total
        grand_ok += ok
        grand_fail.extend(fails)
        print(f"  小计：total={total} ok={ok} fail={len(fails)}")

    print("\n========== 统计 ==========")
    print(f"总图片数：{grand_total}")
    print(f"成功数：  {grand_ok}")
    print(f"失败数：  {len(grand_fail)}")
    if grand_fail:
        print("失败 URL：")
        for u in grand_fail:
            print(f"  - {u}")

    return 0 if not grand_fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
