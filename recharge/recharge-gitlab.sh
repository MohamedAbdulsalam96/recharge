#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "Specify the comment for updating GitLab. e.g. $0 'This update is for'"
    exit 1
fi


vi apps/recharge/recharge/__init__.py
bench --site dev-erp.vpcommunications.co.tz export-fixtures
cd apps/recharge
git add .
git commit -m "$1"
git push upstream master

