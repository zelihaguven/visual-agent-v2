# Reference - General - Wild Card Matching

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > General > Wild Card Matching

---

## Wild Card Matching

Three wild card match characters are available. An asterisk ‘\*’, a question mark ‘?’ and a percentage sign, '%'. The asterisk matches any number of characters whilst the question mark matches one single character and the percentage sign, similar to the asterisk, matches any number of characters but it will also search over '::' nomenclature and spaces.

For example:-

| Entry | Matches |
|---|---|
| ABC* | ABC, ABCD, ABCDEF, ABC7 |
| *ABC | ABC, 7ABC, XYZABC |
| *ABC* | ABC, XYZABC, ABCDEF, XYZABCDEF |
| A*C | ABC, AXC, AXXXXXC |
| ?BC | ABC, XBC |
| A?C | ABC, AXC |
| AB? | ABC, ABX |
| ?B? | ABC, XBX |
| %ABC | ABC, 7ABC, 7 ABC, 7::ABC, XYZABC, XYZ ABC, XYZ::ABC |
| A%C | ABC, A7BC, AB7 C, A7::BC, AXYZBC, ABXYZ C, ABXYZ::C |
| AB% | ABC, ABC7, ABC 7, ABC7::, ABCXYZ, ABC XYZ, ABC::XYZ |
| %B% | ABC, 7ABC7, 7 ABC 7, 7::ABC::7, XYZABCXYZ, XYZ ABC XYZ, XYZ::ABC::XYZ |
| The following use of wild cards is not allowed as the results would be unpredictable:- | |
| **Entry** | **Comments** |
| A**B | Two wild cards cannot be used together. |
| A*B*C | Two *, unless at beginning and end, cannot be used. |
| A*B? | * and ? cannot be used in the same entry. |
