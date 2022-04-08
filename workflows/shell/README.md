Simple Shell Workflow
=====================
This directory contains a basic shell workflow to demonstrate the system. The [run_opt.sh](run_opt.sh) main script runs the optimiser and calls the [configure.sh](configure.sh) script for each new parameter set. This in turn calls the [run_dummy.sh](run_dummy.sh) which calls the [dummy model](https://github.com/optclim/DummyModel). The [run_dummy.sh](run_dummy.sh) expects to find the binary `dummy` in the path. The scripts take a configuration file as argument, eg [modelopt.cfg](/example/dummy/modelopt.cfg).
