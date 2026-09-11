# When a guide is too big for one turn

A long trust — or a mirror pair, which is two long trusts — will not fit in one turn. Two 47-page
documents plus the reference files plus a 70-claim verification is more reading, writing and tool
calls than one turn holds. Plan for that from the start instead of discovering it at the end.

## Work in stages, and say where you are

Everything persists on disk between turns: the content files, the guide, the worksheet. A
follow-up turn resumes from those — never re-read the documents to rebuild what is already
written.

1. **Read** the documents and write the content files.
2. **Build** — `build.py` writes the guide and the worksheet.
3. **Verify** — mark the worksheet against the documents, in batches.
4. **Deliver** — present the files, offer Box upload, post the notes.

When you are running low on a turn, stop at a stage boundary and say so in one line: what is done,
what is on disk, what remains. Then continue when asked. Do not compress verification to fit a
turn, and never present an unverified guide as finished — an honest "built but not yet verified"
is the correct outcome for a turn that ran out.

## Mark the worksheet in batches

`verify.py mark worksheet.md marks.txt` applies a batch and reports how many claims remain,
without failing. Work through the document in passes, marking as you go. Run
`verify.py check worksheet.md` once at the end — that is the only command that gates.

## Two techniques for the size itself

### Split the content across files

`build.py` takes any number of content files; the output is always the last argument. List keys
(`sections`, `quick_ref`, `banners`, `document_sections`) concatenate in order, so the result is
identical to one combined file.

```
python3 "$BUILD" meta.json sections-1.json sections-2.json /mnt/user-data/outputs/Name.html
```

Put the top-level keys (`title`, `doc_type_dates`, `preparer`, `prepared`, `layout`,
`document_sections`) and `quick_ref` in the first file, then a few sections per file after that.
Write them across turns if you need to. `verify.py extract` takes the same list.

### The marks file format

Rather than re-emitting a 40-line worksheet to mark it, write one line per claim and let `check`
apply them into the worksheet before gating — so the worksheet still ends up as the delivered
record.

```
001 x
020 ? -- no schedule was attached to the copy provided
012 ! -- the document says ages 30 / 35 / 40
signoff x
```
```
python3 "$V" mark  [GuideName]_verification.md marks-batch1.txt   # per batch, no gate
python3 "$V" mark  [GuideName]_verification.md marks-batch2.txt
python3 "$V" check [GuideName]_verification.md                   # once, at the end
```

Marks are `x` confirmed, `!` wrong, `?` not verifiable, plus `signoff x` for the sign-off block.
A note after `--` is optional for `x` and expected for `!` and `?`. If any line cannot be parsed,
nothing is applied and it tells you which line — so a malformed marks file never half-marks a
worksheet.

This makes marking cheap to write. It does not make it cheap to *do*: each `x` still means you
went back to the document and looked.
