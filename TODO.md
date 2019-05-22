# TODOLIST

Version 1.0 :
- [x] Better support shadow build hierarchy
- [x] Add option `MOC_LVL_0`
- [x] Refactor how the arguments are passed to qmake_unity.py to add config arguments
- [x] Benchmark perfs
- [x] Remove f-strings from python (compatibility)
- [x] Profile python
- [x] Make a zip release

Not planned for now :
- [ ] Remove SAFE_MODE (always check the files to delete are in the UNITY_DIR directory or throw an exception...)
- [ ] Auto-remove moc.h files from unity (MOC) if a cpp file contains : `#include "toto.moc"`, `#include "moc_toto.cpp"`
- [ ] Study PIMPL case
- [ ] Support Visual Studio
- [ ] Write automated incremental tests (ex : add a cpp file to the project, see how the groups are updated)
- [ ] Check compatibility with qmake static_and_shared option
