#!/bin/bash -ex
if [ -f dev-chart.tgz ]
then
  CHART=dev-chart.tgz
else
  CHART=lsst-sqre/sherlock
fi

helm delete sherlock-dev -n sherlock-dev || true
docker build -t lsstsqre/sherlock:dev .
helm upgrade --install sherlock-dev $CHART --create-namespace --namespace sherlock-dev --values dev-values.yaml
