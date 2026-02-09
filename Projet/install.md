# pour cacti 

sudo apt install -y g++-multilib libc6-dev-i386

make clean
make

./cacti -infile cache.cfg
  