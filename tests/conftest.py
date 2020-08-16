#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2020-2020 Lucas Heitzmann Gabrielli.
# This file is part of gdstk, distributed under the terms of the
# Boost Software License - Version 1.0.  See the accompanying
# LICENSE file or <http://www.boost.org/LICENSE_1_0.txt>

import pathlib
import tempfile
import pytest
import numpy
import gdstk


def assert_same_shape(sh1, sh2, precision):
    d12 = gdstk.boolean(
        sh1, gdstk.offset(sh2, precision, use_union=True), "not", precision, 255, 102
    )
    d21 = gdstk.boolean(
        sh2, gdstk.offset(sh1, precision, use_union=True), "not", precision, 255, 201
    )
    if len(d12) > 0 or len(d21) > 0:
        lib = gdstk.Library("Debug")
        cell = lib.new_cell("Debug")
        if hasattr(sh1, "__iter__"):
            cell.add(*sh1)
        else:
            cell.add(sh1)
        if hasattr(sh2, "__iter__"):
            cell.add(*sh2)
        else:
            cell.add(sh2)
        if len(d12) > 0:
            cell.add(*d12)
        if len(d21) > 0:
            cell.add(*d21)
        outfile = pathlib.Path(tempfile.gettempdir()) / "debug.gds"
        lib.write_gds(outfile)
        raise AssertionError("Shapes don't match. Debug library saved as %s" % outfile)


@pytest.fixture(scope="session")
def proof_cells():
    infile = pathlib.Path(__file__).parent / "proof_lib.gds"
    lib = gdstk.read_gds(infile)
    cells = {c.name: c for c in lib.cells}
    return cells


def make_proof_lib():
    outfile = pathlib.Path(__file__).parent / "proof_lib.gds"
    if outfile.exists():
        raise RuntimeError("Test library %s already exists." % outfile)
    lib = gdstk.Library("Test Library", unit=1e-6, precision=1e-12)

    cell = lib.new_cell("Polygon.fillet")
    p1 = gdstk.Polygon([(0, 0), (1.2, 0), (1.2, 0.3), (1, 0.3), (1.5, 1), (0, 1.5)])
    p2 = p1.copy().translate(2, 0)
    cell.add(p1.fillet(0.3, tolerance=1e-3))
    cell.add(p2.fillet([0.3, 0, 0.1, 0, 0.5, 10], tolerance=1e-3))

    for scale_width in [True, False]:
        cell = lib.new_cell(f"FlexPath: scale_width {scale_width}")
        path0 = gdstk.FlexPath(
            (0j, 1j, 0.5 + 1j,),
            [0.1, 0.2],
            0.3,
            tolerance=1e-4,
            scale_width=scale_width,
        )
        path0.turn(0.4, -numpy.pi, [0.2, 0.1]).segment((-0.2, 0), relative=True)
        path1 = path0.copy().mirror((1.5, 0))
        path1.set_layers(1, 1)
        path2 = path0.copy().mirror((1.5, 0), (1.5, 1))
        path2.set_layers(2, 2)
        path3 = path0.copy().scale(2, (3, 0))
        path3.set_layers(3, 3)
        path4 = path0.copy().scale(-2, (-1, 0))
        path4.set_layers(4, 4)
        path5 = path0.copy().rotate(numpy.pi / 2, (2, 1)).translate(0.2, -0.3)
        path5.set_layers(5, 5)
        cell.add(path0, path1, path2, path3, path4, path5)

    lib.write_gds(outfile)
    print("Test library saved as %s" % outfile)


if __name__ == "__main__":
    make_proof_lib()