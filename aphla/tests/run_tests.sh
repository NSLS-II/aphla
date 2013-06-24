#!/bin/bash

ARG="-s --nologcapture"

if [ ${USER} == "jenkins" ]; then
    ARG="-s -v"
fi

nosetests $ARG aphla/tests/test_analysis.py
nosetests $ARG aphla/tests/test_nsls2v2.py
