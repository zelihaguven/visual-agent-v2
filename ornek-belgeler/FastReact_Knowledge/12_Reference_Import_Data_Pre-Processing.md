# Reference - Importing Data - File Pre-processing - File Pre-processing

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Pre-Processing
**Index keywords:** File Pre, Processing

---

When importing data into FastReact the import procedures expect the import files to be in a specified format. This format, whilst quite simple in nature, may be difficult to achieve if the company does not have a programming resource or the data is held in simple spreadsheets.

To address this problem, FastReact has the capability of preprocessing data files to convert them into the format it requires according to rules that you can define, as below.

## General configuration file

This file is required to identify those files which need to be processed. Each of these contains details of the preprocessing required on a file by file basis.

File name = IMPORTPP.INI

## [Common]

### Running=N

FastReact will set this value to Y when processing files. FastReact will raise an error if processing is started on one workstation whilst processing is already running on another workstation.

## [FileList]

### F1=File1.ini

### F2=File2.ini

### F n =File n .ini

This is a list of individual process configuration files. Each of these will define the rules for converting the data files into the FastReact format. Each entry in this list must be in the format as above, that is each file name entry must be prefixed by ‘Fn=’ where n is a sequential number. The actual file names are not important but a meaningful name would be helpful.

## [Lookup…]

### A = Alpha

### B = Beta

### C = Charlie

There can be multiple 'Lookup...' entries in the file. Each of these Lookups must have a different name.

For example, the above lookup example contains the phonetic alphabet so could be called [LookupPhonetic].

This is a set of values that can be looked up when converting a file. It allows a value in the original file to be converted to be something else in another file. The use of this lookup is described in the section on File Pre-processing - Conversion.

## [Essential]

### F1=File1.ini

### F2=File2.ini

### F n =File n .ini

Files to be processed can be referenced in this file, these 'Essential' entries will allow FastReact to check that all the referenced files are available prior to Pre-Processing and importing. Each of these Essential files must have a different name. If one of the referenced Essenial files is missing from the import location then FastReact will not import any of the files.

## Individual configuration files

These files (names as in the FileList above) define the Pre-Processing rules for each of your data files. There are two different types of configuration files:

- Merging – To merge two files based upon a common value.
- Conversion – To convert the data from a single input file to a single output file.
