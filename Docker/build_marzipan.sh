#!/bin/bash

tar -czh . | docker build --network=host -t nlesc/marzipan:latest -
