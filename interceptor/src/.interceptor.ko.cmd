cmd_/src/interceptor.ko := ld -r -m elf_x86_64 -z max-page-size=0x200000 -T ./scripts/module-common.lds --build-id  -o /src/interceptor.ko /src/interceptor.o /src/interceptor.mod.o ;  true
