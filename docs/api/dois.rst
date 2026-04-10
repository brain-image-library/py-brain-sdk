dois
====

DOI and citation lookup via DataCite and Google Scholar.

.. automodule:: brainimagelibrary.dois
   :members:
   :undoc-members: False
   :show-inheritance:

Interactive example
-------------------

Click the button below to launch a live Python environment (via `Binder <https://mybinder.org>`_)
and run the code directly in your browser.

.. thebe-button:: Launch interactive session

.. code-block:: python
   :class: thebe
   :caption: Retrieve citation records for dataset ``act-bag``

   import subprocess, sys
   subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "brainimagelibrary"])

   import brainimagelibrary as bil
   import pprint

   result = bil.dois.get_datacite_citations(bildid="act-bag")
   pprint.pprint(result)
