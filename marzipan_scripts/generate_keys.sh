#!/bin/bash

echo "Generating the ssh-key for root user."
ssh-keygen -b 4096 -t rsa -f id_rsa_lokum_root.key -q -P ""

echo "Generating the ssh-key for ubuntu user."
ssh-keygen -b 4096 -t rsa -f id_rsa_lokum_ubuntu.key -q -P ""

cp id_rsa_lokum* ./deployment/tmp/


