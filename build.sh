#!/bin/bash

docker build --build-arg SUMO_USER=$UID . < Dockerfile -t docker-sumo
