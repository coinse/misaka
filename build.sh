rm misaka/_hoedown.*.so
rm misaka/*.gcno
rm misaka/*.gcda
rm misaka/*.o
rm misaka/hoedown/*.gcno
rm misaka/hoedown/*.gcda
rm misaka/hoedown/*.o
python build_ffi.py
