Guillotina Prometheus Docs
==========================

This package aims to provide basic prometheus integration for guillotina.

Configuration
-------------

Just add a few lines to your config.yml::

  {"applications": ["guillotina_prometheus"],
   "middlewares": ["guillotina_prometheus.middleware.PrometheusMiddleware"]}



Dependencies
------------

Python >= 3.7


Installation
------------

This example will use virtualenv::

  virtualenv .
  ./bin/python setup.py develop


Running
-------

Most simple way to get running::

  ./bin/guillotina
