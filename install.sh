#! /bin/bash
cd awp-odc-os/src/
make clean -f Makefile.bluewaters.gnu
make -f Makefile.bluewaters.gnu
cd ../run/
ln -fs ../src/pmcl3d
