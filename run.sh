#!/bin/bash

docker run -it --rm\
    --name=docker-sumo\
    --network=platform\
    --env="DISPLAY" \
    --volume="/etc/group:/etc/group:ro" \
    --volume="/etc/passwd:/etc/passwd:ro" \
    --volume="/etc/shadow:/etc/shadow:ro" \
    --volume="/etc/sudoers.d:/etc/sudoers.d:ro" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    --volume "$(pwd):/opt/spresev-sim:rw" \
    --user=$UID \
    docker-sumo \
    bash