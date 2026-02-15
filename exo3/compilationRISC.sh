riscv64-linux-gnu-gcc -O2 -static -march=rv64gc -mabi=lp64d -fno-lto exo3/normale.c -o runs/bin/P1.riscv
riscv64-linux-gnu-gcc -O2 -static -march=rv64gc -mabi=lp64d -fno-lto exo3/pointer.c -o runs/bin/P2.riscv
riscv64-linux-gnu-gcc -O2 -static -march=rv64gc -mabi=lp64d -fno-lto exo3/tempo.c -o runs/bin/P3.riscv
riscv64-linux-gnu-gcc -O2 -static -march=rv64gc -mabi=lp64d -fno-lto exo3/unrol.c -o runs/bin/P4.riscv