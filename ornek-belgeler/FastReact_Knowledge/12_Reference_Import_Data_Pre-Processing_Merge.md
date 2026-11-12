# Reference - Importing Data - File Pre-processing - Merge

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Pre-Processing > Merge
**Index keywords:** File Pre, Merge, Processing

---

The file has a header section with the following entries all of which are required. Each of these is described below.

| [Common] | Section Header |
|---|---|
| **PreProcess** | Merge <br> This must be Merge for the conversion type configuration files. |
| **OutputFile** | This is the name of the file that will be created. |
| **OutputFileType** | Specifies the format of your output data file. This can be TAB , for tab separated or CSV for Comma separated variable. |
| **HeaderLines** | This is the number of header lines that are in the main and link file(s). All files must have the same number of header lines. |
| **MainFile** | This is the name of the file which is being linked to one or two other files. |
| **MainFileType** | Specifies the format of your main file. This can be TAB , for tab separated or CSV for Comma separated variable. |
| **LinkType=** | (optional) This can either be Matched (this is the default type if LinkType is not present) or Always. <br> Matched only adds rows to the output file where a Match is found. <br> Always adds a record even if there is no match, in which case it fills the missing fields with the value specified by AlwaysLinkText . If that is missing then the fields are added as a blank. |
| **AlwaysLinkText=** | (optional) This is used in conjunction with the LinkType= field, see above. |
| **[LinkFile1]** | **Section Header** |
| **File** | This is the name of the FIRST file being linked to. |
| **FileType** | Specifies the file type of the FIRST link file. This can be TAB , for tab separated or CSV for Comma separated variable. |
| **LinkColumn** | This is the column on the link file that should link to the Main file. |
| **MainLinkColumn** | This is the column on the Main file that should link to the column in this file. |
| **[LinkFile2]** | **Section Header** |
| **File** | This is the name of the SECOND file being linked to. |
| **FileType** | Specifies the file type of the SECOND link file. This can be TAB , for tab separated or CSV for Comma separated variable. |
| **LinkColumn** | This is the column on the link file that should link to the Main file. |
| **MainLinkColumn** | This is the column on the Main file that should link to the column in this file. |
