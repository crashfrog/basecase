#!/bin/bash
echo "Basecase workunit framework v.01a"

ARCHIVE=`awk '/^__WORKUNIT_RESOURCES__/ {print NR + 1; exit 0; }' $0`
tail -n+$ARCHIVE $0 | tar xjv -C $PWD
{{ commands }}
_WORKUNIT_RESOURCES_
