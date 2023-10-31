Cylc 8 Workflow
===============
Dummy Model
-----------
This directory contains a [cylc8](https://cylc.github.io/) workflow to demonstrate the system. The workflow is defined in [flow.cylc](flow.cylc). The optimise is called repeatedly. If the `new` signal is emitted a new run is configured by cloning the dummy directory, running it and finally postprocessing it. If the `wait` signal is emitted the workflow waits for 10 seconds and tries again. 

You can use the [install.sh](install.sh) script to install the workflow into the `cylc-src` directory in your home directory. The workflow is installed using

```
cylc install modelopt2
```

You can then run and watch it using
```
cylc play modelopt2
cylc tui modelopt2
```
