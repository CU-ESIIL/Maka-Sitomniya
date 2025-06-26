# Citation Management and Notes Collection in Markdown

## Introduction

This document serves as a guide for managing citations and collecting research notes for our project. We'll use a combination of a `.bib` file for bibliographic references and Markdown for note-taking.

## Part 1: Setting Up Your .bib File for Citations

### Creating a .bib File

1. **Create a new file** with a `.bib` extension, for example, `project_references.bib`.
2. **Add bibliographic entries** to this file. Each entry should follow the BibTeX format.

### Example of a .bib Entry

```bibtex
@article{Doe2021,
  author  = {Jane Doe and John Smith},
  title   = {Insights into Environmental Data Science},
  journal = {Journal of Data Science},
  year    = {2021},
  volume  = {15},
  number  = {4},
  pages   = {123-145},
  doi     = {10.1000/jds.2021.15.4}
}



## Part 2: Using Citations in Markdown

### Citing in Your Markdown Document

- Refer to works in your `.bib` file using citation keys, like `[@Doe2021]`.

### Converting Markdown to PDF with Citations

- Use Pandoc: `pandoc yourdoc.md --bibliography=project_references.bib --citeproc -o output.pdf`

## Part 3: Collecting Citations and Research Notes

### Structuring Your Notes

#### Notes on Doe 2021 `[@Doe2021]`

- **Key Points:**
  - Summary of the article's main arguments.
  - Notable methodologies.

- **Relevance to Our Project:**
  - How this research informs our project.
  - Applicable methodologies or theories.

#### Notes on Another Article `[@Another2021]`

- **Key Points:**
  - ...

- **Relevance to Our Project:**
  - ...

## Conclusion

This document facilitates efficient management of references and collaborative knowledge building for our project.
