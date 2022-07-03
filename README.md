# Traffic-Light Control for Emergency Vehicles

This repository contains the source code and instructions to run some traffic-light control systems, using algorithms to perform traffic-light preemptions, in order to reduce the timeloss of some desired Emergency Vehicle (EV).

## Getting started

First, we must make sure our libraries are installed. The following instructions were used in Linux/Debian x64 based systems.

`sudo apt-get install screen git python3 python-pip ython3-pip python3-numpy python3-matplotlib libxml2-dev libxslt-dev python-dev python3-dev cmake python libxerces-c-dev libfox-1.6-dev libgl1-mesa-dev libglu1-mesa-dev libgdal-dev libproj-dev libgl1-mesa-dev libglew-dev freeglut3-dev libglm-dev libgl2ps-dev swig openscenegraph python3-scipy python3-pandas python-setuptools python-numpy python-matplotlib python-scipy python-pandas python-tk graphviz xfig fig2dev g++ libxerces-c-dev libgdal-dev libproj-dev libgl2ps-dev swig python-statsmodels-lib`

`pip3 install pyexcel-ods3 wheel SNAKES`

`python -m pip install statsmodels`

Install `pyfuzzy` following [these instructions](https://github.com/avatar29A/pyfuzzy.git).

## Installing SUMO

All runs were done using [SUMO Simulator](https://sumo.dlr.de/docs/). To get the same results we've obtained, you must use a specific version of that simulator: v1_4_0+0443-637095a (that's because it's the version we were using when we were collecting the results). Python 3 should also be used. Before following the installation instructions, clone the repository:

`git clone --recursive https://github.com/eclipse/sumo`

and then

`git checkout 637095a`

The rest of the SUMO installation instructions are [here](https://github.com/eclipse/sumo#build-and-installation).

## Running the baseline (No preemption) version

To observe the gain achieved by preemptive implementations, one must first run the baseline version, i.e., the situation where no preemption is used. To do that, execute the following command in this repository folder

`python3 new_proposal.py --scenario <SPECIFIC SCENARIO FOLDER> --ev <EV NAME> --seedsumo <SEED SUMO>`

To get results close to ours, the parameters list are:

* `--scenario`: use our scenarios. For example, **./scenarios/defined/sp/sp-1**, or **./scenarios/defined/ny/ny-3**. Check `scenarios` folder to get valid scenarios
* `--ev`: For SP, use **veh11651**. For NY, use **veh4856**. Valid values are the `id` field in any entry of `osm.passenger.rou.xml` scenario file (an example [here](scenarios/defined/sp/sp-1/osm.passenger.rou.xml)) 
* `--seedsumo`: Use one of the values in `seeds.txt`.

Some additional parameters can be used:

* `--skip`: Specify it without value to not create nor override the `.json` result file
* `--nogui`: Specify it without value to run a console-only experiment
* `--override`: If it is `False` and the `.json` result file exists, the run is cancelled. If `True`, the experiment runs anyway, and the previou json file is overrided
* `--alg`: Specify the preemption algorithm. Default is `no-preemption`

## Getting the results

At the end of simulation, the console shows the EV's timeloss and some other metrics. If desired, the results are written in a json file in a `results` folder that is created inside of scenario folder (an example can be seen [here](scenarios/defined/sp/sp-1/results/staticdynamic/alg!djahel_ev!veh5393_seed!227_wc!start_el!high.json)).

## Running Queue Based (Kapusta et al., 2017)

Our version of Queue Based algorithm (based on [this work](https://ieeexplore.ieee.org/abstract/document/8124424)) can be used with `--alg kapusta2`.

## Running Queue Based Improved

Our improved version of Queue Based algorithm (based on [this work](https://ieeexplore.ieee.org/abstract/document/8124424)) can be used with `--alg kapustaimp`.

## Running RFId algorithm

A simple RFId was designed and it is avaliable using `--alg rfid`. Some parameters must be informed:

* `--distancedetection`: 25 or 100 (but it could be any value greater than 0)
* `--ncycles`: 2 and 5 (but it could be any value greater than 0)

## Running Fuzzy algorithm

Our version of Fuzzy logic algorithm (based on [this work](https://ieeexplore.ieee.org/abstract/document/7366151)) can be used with `--alg djahel`. You must also specify the Emergency Level (EL):

* `--el`: allowed values are `low`, `medium` and `high`.

## Running TPN algorithm

TPN is our main algorithm. To use it, it is enough to use `--alg petri`.

## Custom Scenarios

If you want to generate different scenarios, you can use the [OSMWebWizard tool](https://sumo.dlr.de/docs/Tutorials/OSMWebWizard.html). The selected EV must be in the **passenger vehicles route file** (in our case, the file is `osm.passenger.rou.xml` in the scenario folder, see an example [here](scenarios/defined/sp/sp-1/osm.passenger.rou.xml), but it could use `osm.passenger.trips.xml` instead).

## License

This Project is released under the [Mozilla Public License version 2](https://www.mozilla.org/en-US/MPL/2.0/).
