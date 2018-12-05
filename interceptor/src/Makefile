obj-m += interceptor.o


INCLUDES += -fno-pie -I/usr/src/linux-headers-4.15.0-42/arch/x86/include/  -I/usr/lib/gcc/x86_64-linux-gnu/7/include/ 
all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) EXTRA_CFLAGS+=$(INCLUDES)  modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
