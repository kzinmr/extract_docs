# extract_docs
extract text from doc/docx

- ln -s /path/to/doc_docx_dir/ ./workspace/docs/
- docker build -t extract-docs .
- docker run --rm -v /path/to/extract_docs/workspace:/app/workspace extract-docs