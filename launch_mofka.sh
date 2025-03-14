#!/bin/bash

if [ -n "${MOFKA_GROUPFILE}" ]; then

    t_generation="mofa_test2_generation_result"
    t_requests="mofa_test2_requests"
    groupfile=${MOFKA_GROUPFILE}

    partition="default"

    bedrock tcp -c mofka_config.json &
    sleep 5
    cat mofka.json
    cp mofka.json ${groupfile}
    BEDROCK_PID=$!



    METADATA_PROVIDER=$(
      python -m mochi.mofka.mofkactl metadata add \
              --rank 0 \
              --groupfile mofka.json \
              --type log \
              --config.path /tmp/mofa/mofka-log \
              --config.create_if_missing true
    )

    DATA_PROVIDER=$(
        python -m mochi.mofka.mofkactl data add \
              --rank 0 \
              --groupfile mofka.json \
              --type abtio \
              --config.path /tmp/mofa/mofka-data \
              --config.create_if_missing true
    )


    mofkactl topic create ${t_generation} --groupfile ${groupfile}
    mofkactl partition add ${t_generation} --type ${partition} --rank 0 --groupfile ${groupfile}  --metadata "${METADATA_PROVIDER}" --data "${DATA_PROVIDER}"

    mofkactl topic create ${t_requests} --groupfile ${groupfile}
    mofkactl partition add ${t_requests} --type ${partition} --rank 0 --groupfile ${groupfile} --metadata "${METADATA_PROVIDER}" --data "${DATA_PROVIDER}"

    sleep 60
    touch /mnt/parsl/started
    wait ${BEDROCK_PID}
else
    touch /mnt/mofa/mofka.json
    sleep 50
fi
