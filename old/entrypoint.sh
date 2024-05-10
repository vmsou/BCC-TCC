#!/bin/bash

service ssh restart
ssh -o "StrictHostKeyChecking no" root@localhost << EOF
/home/hadoop/sbin/start-dfs.sh
/home/hadoop/sbin/start-yarn.sh
EOF
bash
# tail -f /dev/null  # keeps running