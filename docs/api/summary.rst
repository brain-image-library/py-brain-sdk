summary
=======

High-level summary functions over daily BIL inventory reports.

.. automodule:: brainimagelibrary.summary
   :members:
   :undoc-members: False
   :show-inheritance:

Loading a report by date
------------------------

Use :func:`brainimagelibrary.summary.load` to retrieve the inventory report
for any specific date.  The function first looks for the file on the BIL
shared filesystem (``/bil/data/inventory/daily/<date>.tsv``); if that path
is unavailable it falls back to downloading the file from
``https://download.brainimagelibrary.org/inventory/daily/<date>.tsv``.

When data for the requested date cannot be found by either method, the
function prints ``Data for <date> is unavailable.`` and returns ``None``.

.. code-block:: python

   from brainimagelibrary import summary

   df = summary.load("20240101")

   if df is not None:
       print(f"Loaded {len(df)} records.")
       print(df.head())
   # If the date has no data, the function prints:
   # Data for 20240101 is unavailable.
