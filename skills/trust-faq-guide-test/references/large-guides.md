# When a guide is too big for one turn

A long trust — or a mirror pair, which is two long trusts — will not fit in one turn. Two 47-page
documents plus the reference files plus a 70-claim verification is more reading, writing and tool
calls than one turn holds. Plan for that from the start instead of discovering it at the end.

## Work in stages, and say where you are

Everything persists on disk between turns: the content files, the source text, the guide. A
follow-up turn resumes from those — never re-read the documents to rebuild what is already
written.

1. **Read** the documents and write the content files, recording a verbatim quote with each
   citation as you go.
2. **Build** — `build.py` renders the guide and confirms every quote against the document text.
3. **Deliver** — present the files, offer Box upload, post the notes.

When you are running low on a turn, stop at a stage boundary and say so in one line: what is done,
what is on disk, what remains. Then continue when asked. Never present a guide whose build did not pass as finished — an honest "still fixing quotes the
build rejected" is the correct outcome for a turn that ran out.

## Splitting the content

### Split the content across files

`build.py` takes any number of content files; the output is always the last argument. List keys
(`sections`, `quick_ref`, `banners`, `document_sections`) concatenate in order, so the result is
identical to one combined file.

```
python3 "$BUILD" meta.json sections-1.json sections-2.json /mnt/user-data/outputs/Name.html
```

Put the top-level keys (`title`, `doc_type_dates`, `preparer`, `prepared`, `layout`,
`document_sections`) and `quick_ref` in the first file, then a few sections per file after that.
Write them across turns if you need to.
