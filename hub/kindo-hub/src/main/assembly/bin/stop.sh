#/bin/bash
cd `dirname $0`
BIN_DIR=`pwd`
cd ..
DEPLOY_DIR=`pwd`
CONF_DIR=$DEPLOY_DIR/conf

pidfile=$CONF_DIR/kindo-hub.pid
if [  -f "$pidfile" ]; then
    PIDS=`cat $pidfile`
    if [ -z "$PIDS" ]; then
        echo "ERROR: The SERVER does not started!"
        exit 1
    fi

    echo -e "Stopping ...\c"
    for PID in $PIDS ; do
        kill $PID > /dev/null 2>&1
    done

    COUNT=0
    while [ $COUNT -lt 1 ]; do
        echo -e ".\c"
        sleep 1
        COUNT=1
        for PID in $PIDS ; do
            PID_EXIST=`ps -f -p $PID | grep java`
            if [ -n "$PID_EXIST" ]; then
                COUNT=0
                break
            fi
        done
    done
fi

echo "OK!"
echo "PID: $PIDS"
rm -rf $CONF_DIR/kindo-hub.pid
