# When a guide is too big for one turn

A long trust can need more JSON than fits comfortably in a single turn, and writing it in one
go risks a truncated file — which is a broken build, not a smaller guide. Two techniques.

## Split the content across files

`build.py` takes any number of content files; the output is always the last argument. List keys
(`sections`, `quick_ref`, `banners`, `document_sections`) concatenate in order, so the result is
identical to one combined file.

```
python3 "$BUILD" meta.json sections-1.json sections-2.json /mnt/user-data/outputs/Name.html
```

Put the top-level keys (`title`, `doc_type_dates`, `preparer`, `prepared`, `layout`,
`document_sections`) and `quick_ref` in the first file, then a few sections per file after that.
Write them across turns if you need to. `verify.py extract` takes the same list.

## Mark the worksheet with a small marks file

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
python3 "$V" check [GuideName]_verification.md marks.txt
```

Marks are `x` confirmed, `!` wrong, `?` not verifiable, plus `signoff x` for the sign-off block.
A note after `--` is optional for `x` and expected for `!` and `?`. If any line cannot be parsed,
nothing is applied and it tells you which line — so a malformed marks file never half-marks a
worksheet.

This makes marking cheap to write. It does not make it cheap to *do*: each `x` still means you
went back to the document and looked.
