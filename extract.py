import os
import re
import sys
import zipfile
from enum import Enum
from pathlib import Path

import textract
from langdetect import detect


try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML


class Language(Enum):
    ja = "ja"
    en = "en"
    other = "other"


"""
Module that extract text from MS XML Word document (.docx).
(Inspired by python-docx <https://github.com/mikemaccana/python-docx>)
"""

WORD_NAMESPACE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
PARA = WORD_NAMESPACE + "p"
TEXT = WORD_NAMESPACE + "t"


def get_docx_text(path):
    """
    Take the path of a docx file as argument, return the text in unicode.
    """
    document = zipfile.ZipFile(path)
    xml_content = document.read("word/document.xml")
    document.close()
    tree = XML(xml_content)

    paragraphs = []
    for paragraph in tree.getiterator(PARA):
        texts = [node.text for node in paragraph.getiterator(TEXT) if node.text]
        if texts:
            paragraphs.append("".join(texts))

    return "\n\n".join(paragraphs)


def detect_language(text) -> Language:
    language = Language.ja
    lang_str = None

    try:
        lang_str = detect(text)
    except Exception:
        pass

    if lang_str is None:
        return Language.other

    try:
        language = Language[lang_str]
    except Exception:
        return Language.other

    lang_str = None

    if language != Language.en:
        return language

    text_no_eng = re.sub(r"[a-zA-Z0-9０-９ａ-ｚＡ-Ｚ\n 　]", "", text)
    if len(text_no_eng) < len(text) / 2:
        return Language.en

    try:
        lang_str = detect(text_no_eng)
    except Exception:
        pass

    if lang_str is None:
        return Language.other

    try:
        language = Language[lang_str]
    except Exception:
        return Language.other

    return Language.ja


def extract_ja_docs(docpath: str, targetdir: str):
    """extract text from doc/docx
    - dirpath: directory which includes doc/docx files
    """
    # dirpath_p = Path(dirpath)
    targetdir_p = Path(targetdir)
    try:
        text = textract.process(docpath)
        text = text.decode("utf8")
        lang = detect_language(text)
        if lang == Language.ja:
            targetdir_p.mkdir(parents=True, exist_ok=True)
            new_path = targetdir_p / f"{Path(docpath).stem}.txt"
            with open(new_path, "wt") as ofp:
                ofp.write(text)
        else:
            # doc_p = Path(docpath)
            # new_dir = doc_p.parent / 'others'
            # new_dir.mkdir(exist_ok=True)
            # new_path = new_dir / doc_p.stem
            # with open(docpath) as ifp, open(new_path, "wt") as ofp:
            #     shutil.copyfileobj(ifp, ofp)
            # doc_p.unlink()
            pass

    except (
        textract.exceptions.ShellError,
        textract.exceptions.ExtensionNotSupported,
        UnicodeDecodeError,
        zipfile.BadZipFile,
        OSError,
        TypeError,
        KeyError,
    ) as e:
        print(f"{e} skip: {docpath}")


if __name__ == "__main__":
    args = sys.argv
    assert len(args) == 3
    doc_dir = args[1]
    target_dir = args[2]
    for cur, dirs, files in os.walk(doc_dir):
        target_subdir = cur.replace(doc_dir, target_dir)
        if not os.path.exists(target_subdir):
            for fn in files:
                if fn.endswith("doc") or fn.endswith("docx"):
                    doc_path = os.path.join(cur, fn)
                    extract_ja_docs(doc_path, target_subdir)
        else:
            print(f"skip: {target_subdir} already exists")
