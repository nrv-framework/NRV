==========================
Create (Fascicle) Geometry
==========================

In NRV, geometries are handled through dedicated classes that allow you to define the shape and structure of fascicles. Custom geometries are currently only used to define fascicles, but this may be extended in the future to nerves and electrodes.

All geometries share a common setup described with the figure bellow:

.. image:: ../images/geometry_1_light.png
    :class: only-light

.. image:: ../images/geometry_1_dark.png
    :class: only-dark


On the (x, y, z)-frame:

- all extrusions are automatically done in the direction of the axons, so on the x-axis direction,

- as a consequence, all 2-D shapes (circles, ellipses or polygons) are constructed in a z-y plane. By default, x is often assumed to be null.


.. warning::

    For now, custom geometries are only used to define fascicles. This might be extended in the future to both nerves and electrodes.

Geometry Base Class: CShape
===========================

All geometry classes inherit from the base class ``CShape``. This class defines the required interface for all shapes.

**Principle**

To define a new geometry, you need to implement the following methods:

- :meth:`~nrv.utils.geom.CShape.is_inside` Checks if given points is inside the C-shape. *Required for axons placement and meshing*

- :meth:`~nrv.utils.geom.CShape.get_point_inside` Returns n points coordinate randomly picked inside the shape. *Required for axons placing*

- :meth:`~nrv.utils.geom.CShape.get_trace` Returns the trace of the geometry as a list of points. *Required for meshing and plotting*

- :meth:`~nrv.utils.geom.CShape.rotate` Rotate the shape. *Required for fascicle placement*

- :meth:`~nrv.utils.geom.CShape.translate` Translate the shape. *Required for fascicle placement*



And the following properties:

- :meth:`~nrv.utils.geom.CShape.area` Area of the shape in :math:`\mu m^2`. *Required for Meshing*
- :meth:`~nrv.utils.geom.CShape.perimeter` Perimeter of the shape in :math:`\mu m^2`. *Required for Meshing*
- :meth:`~nrv.utils.geom.CShape.bbox_size` Size of the bounding bounding box of the shape. *Required for Meshing*
- :meth:`~nrv.utils.geom.CShape.bbox` Coordinate of the bounding box as a :class:`numpy.ndarray` in the following format :math:`y_{min}, z_{min}, y_{max}, z_{max}` *Required for Meshing*


**Example:**

.. code-block:: python

    from nrv.geometry import CShape

    class MyShape(CShape):
        def get_trace(self):
            # Return list of (x, y) points
            pass

        def get(self):
            # Return geometry representation
            pass

Builtin Shapes
==============

NRV provides several built-in geometries for fascicles. The following table summarizes the available shapes:

+----------------+------------------------------------------+-------------------------------+
| Shape Name     | Class                                    | Examples                      |
+================+==========================================+===============================+
| Circle         | :class:`~nrv.utils.geom.Circle`          | Circular fascicle             |
+----------------+------------------------------------------+-------------------------------+
| Ellipse        | :class:`~nrv.utils.geom.Ellipse`         | Elliptical fascicle           |
+----------------+------------------------------------------+-------------------------------+
| Polygon        | :class:`~nrv.utils.geom.Polygon`         | Polygonal fascicle            |
+----------------+------------------------------------------+-------------------------------+

These shapes are nicely illustrated with an example implementing an instance of each shape: :doc:`example 19 <../examples/generic/19_build_geometry>`

Example Usage
=============

Here is how you can create a circular fascicle geometry:

.. code-block:: python

    from nrv.utils.geom import Circle

    # Create a circle with center (0, 0) and radius 50
    circle = Circle(center=(0, 0), radius=50)
    trace = circle.get_trace()
    geometry = circle.get()

Extending Geometries
====================

To define your own custom geometry, subclass ``CShape`` and implement the required methods as shown above.

----

.. note::

    For more details on each geometry class, refer to the API documentation.

.. tip::

    for other examples of geometry, howaver linked with axons population (see next section in the user's guide), please have a look at :

    - :doc:`example 21 <../examples/generic/21_place_population>`
    - :doc:`example 23 <../examples/generic/23_subpop_iclamp>`