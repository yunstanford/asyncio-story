Asynchronous Web Frameworks
===========================

Faster, simpler, more "Pythonic" -- those are the rallying cries for each new web framework in the Python ecosystem. Here are some asynchronous web frameworks.

+------------+-----------+------+----------------------------------------+
| Frameworks | Support   | ASGI | Link                                   |
+------------+-----------+------+----------------------------------------+
| aiohttp    | Python3   | No   | https://github.com/aio-libs/aiohttp    |
+------------+-----------+------+----------------------------------------+
| Sanic      | Python3   | No   | https://github.com/huge-success/sanic  |
+------------+-----------+------+----------------------------------------+
| Quart      | Python3   | Yes  | https://github.com/pgjones/quart       |
+------------+-----------+------+----------------------------------------+
| Starlette  | Python3   | Yes  | https://github.com/encode/starlette    |
+------------+-----------+------+----------------------------------------+
| Vibora     | Python3   | No   | https://github.com/vibora-io/vibora    |
+------------+-----------+------+----------------------------------------+
| Japronto   | Python3   | No   | https://github.com/squeaky-pl/japronto |
+------------+-----------+------+----------------------------------------+
| Tornado    | Python2/3 | No   | https://github.com/tornadoweb/tornado  |
+------------+-----------+------+----------------------------------------+

* ASGI: https://asgi.readthedocs.io/en/latest/
* Benchmarks: https://vibora.io/, https://www.techempower.com/benchmarks/#section=data-r17&hw=ph&test=json&l=zijzen-1


For `Flask`, `Django` services etc, you could still make your service `asynchronous` by utilizing `Gevent <https://github.com/gevent/gevent>`_. `Gunicorn <https://github.com/benoitc/gunicorn>`_ helps you hook everything up under the hood by providing asynchronous gunicorn workders (`worker type <http://docs.gunicorn.org/en/stable/design.html#choosing-a-worker-type>`_).
