#! /bin/bash
cd awp-odc-os/src/
make -f Makefile.bluewaters.gnu
cd ../run/
ln -fs ../src/pmcl3d
