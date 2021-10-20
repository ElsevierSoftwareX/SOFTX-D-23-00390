# Copyright (C) 2020-2021 Sebastian Blauth
#
# This file is part of CASHOCS.
#
# CASHOCS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CASHOCS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CASHOCS.  If not, see <https://www.gnu.org/licenses/>.

"""Tests for the geometry module.

"""

import os
import subprocess

import fenics
import pytest
import numpy as np

import cashocs
from cashocs.geometry import MeshQuality
from cashocs._exceptions import InputError
import cashocs._cli


c_mesh, _, _, _, _, _ = cashocs.regular_mesh(5)
u_mesh = fenics.UnitSquareMesh(5, 5)
rng = np.random.RandomState(300696)


def test_mesh_import():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    subprocess.run(
        ["cashocs-convert", f"{dir_path}/mesh/mesh.msh", f"{dir_path}/mesh/mesh.xdmf"],
        check=True,
    )

    mesh, subdomains, boundaries, dx, ds, dS = cashocs.import_mesh(
        dir_path + "/mesh/mesh.xdmf"
    )

    gmsh_coords = np.array(
        [
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
            [0.499999999998694, 0],
            [1, 0.499999999998694],
            [0.5000000000020591, 1],
            [0, 0.5000000000020591],
            [0.2500000000010297, 0.7500000000010296],
            [0.3749999970924328, 0.3750000029075671],
            [0.7187499979760099, 0.2812500030636815],
            [0.6542968741702071, 0.6542968818888233],
        ]
    )

    assert abs(fenics.assemble(1 * dx) - 1) < 1e-14
    assert abs(fenics.assemble(1 * ds) - 4) < 1e-14

    assert abs(fenics.assemble(1 * ds(1)) - 1) < 1e-14
    assert abs(fenics.assemble(1 * ds(2)) - 1) < 1e-14
    assert abs(fenics.assemble(1 * ds(3)) - 1) < 1e-14
    assert abs(fenics.assemble(1 * ds(4)) - 1) < 1e-14

    assert np.allclose(mesh.coordinates(), gmsh_coords)

    assert os.path.isfile(f"{dir_path}/mesh/mesh.xdmf")
    assert os.path.isfile(f"{dir_path}/mesh/mesh.h5")
    assert os.path.isfile(f"{dir_path}/mesh/mesh_subdomains.xdmf")
    assert os.path.isfile(f"{dir_path}/mesh/mesh_subdomains.h5")
    assert os.path.isfile(f"{dir_path}/mesh/mesh_boundaries.xdmf")
    assert os.path.isfile(f"{dir_path}/mesh/mesh_boundaries.h5")

    subprocess.run(["rm", f"{dir_path}/mesh/mesh.xdmf"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/mesh.h5"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/mesh_subdomains.xdmf"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/mesh_subdomains.h5"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/mesh_boundaries.xdmf"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/mesh_boundaries.h5"], check=True)


def test_mesh_import_from_config():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    subprocess.run(
        ["cashocs-convert", f"{dir_path}/mesh/mesh.msh", f"{dir_path}/mesh/mesh.xdmf"],
        check=True,
    )
    cfg = cashocs.load_config(dir_path + "/config_sop.ini")
    cfg.set("Mesh", "mesh_file", dir_path + "/mesh/mesh.xdmf")
    mesh, subdomains, boundaries, dx, ds, dS = cashocs.import_mesh(cfg)

    gmsh_coords = np.array(
        [
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
            [0.499999999998694, 0],
            [1, 0.499999999998694],
            [0.5000000000020591, 1],
            [0, 0.5000000000020591],
            [0.2500000000010297, 0.7500000000010296],
            [0.3749999970924328, 0.3750000029075671],
            [0.7187499979760099, 0.2812500030636815],
            [0.6542968741702071, 0.6542968818888233],
        ]
    )

    assert abs(fenics.assemble(1 * dx) - 1) < 1e-14
    assert abs(fenics.assemble(1 * ds) - 4) < 1e-14

    assert abs(fenics.assemble(1 * ds(1)) - 1) < 1e-14
    assert abs(fenics.assemble(1 * ds(2)) - 1) < 1e-14
    assert abs(fenics.assemble(1 * ds(3)) - 1) < 1e-14
    assert abs(fenics.assemble(1 * ds(4)) - 1) < 1e-14

    assert np.allclose(mesh.coordinates(), gmsh_coords)

    subprocess.run(["rm", f"{dir_path}/mesh/mesh.xdmf"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/mesh.h5"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/mesh_subdomains.xdmf"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/mesh_subdomains.h5"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/mesh_boundaries.xdmf"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/mesh_boundaries.h5"], check=True)


def test_regular_mesh():
    lens = rng.uniform(0.5, 2, 2)
    r_mesh, _, _, _, _, _ = cashocs.regular_mesh(2, lens[0], lens[1])

    max_vals = rng.uniform(0.5, 1, 3)
    min_vals = rng.uniform(-1, -0.5, 3)

    s_mesh, _, _, _, _, _ = cashocs.regular_box_mesh(
        2, min_vals[0], min_vals[1], min_vals[2], max_vals[0], max_vals[1], max_vals[2]
    )

    assert np.allclose(c_mesh.coordinates(), u_mesh.coordinates())

    assert np.alltrue((np.max(r_mesh.coordinates(), axis=0) - lens) < 1e-14)
    assert np.alltrue((np.min(r_mesh.coordinates(), axis=0) - np.array([0, 0])) < 1e-14)

    assert np.alltrue(abs(np.max(s_mesh.coordinates(), axis=0) - max_vals) < 1e-14)
    assert np.alltrue(abs(np.min(s_mesh.coordinates(), axis=0) - min_vals) < 1e-14)


def test_mesh_quality_2D():
    mesh, _, _, _, _, _ = cashocs.regular_mesh(2)

    opt_angle = 60 / 360 * 2 * np.pi
    alpha_1 = 90 / 360 * 2 * np.pi
    alpha_2 = 45 / 360 * 2 * np.pi

    q_1 = 1 - np.maximum(
        (alpha_1 - opt_angle) / (np.pi - opt_angle), (opt_angle - alpha_1) / (opt_angle)
    )
    q_2 = 1 - np.maximum(
        (alpha_2 - opt_angle) / (np.pi - opt_angle), (opt_angle - alpha_2) / (opt_angle)
    )
    q = np.minimum(q_1, q_2)

    min_max_angle = MeshQuality.min_maximum_angle(mesh)
    min_radius_ratios = MeshQuality.min_radius_ratios(mesh)
    average_radius_ratios = MeshQuality.avg_radius_ratios(mesh)
    min_condition = MeshQuality.min_condition_number(mesh)
    average_condition = MeshQuality.avg_condition_number(mesh)

    assert abs(min_max_angle - MeshQuality.avg_maximum_angle(mesh)) < 1e-14
    assert abs(min_max_angle - q) < 1e-14
    assert abs(min_max_angle - MeshQuality.avg_skewness(mesh)) < 1e-14
    assert abs(min_max_angle - MeshQuality.min_skewness(mesh)) < 1e-14

    assert abs(min_radius_ratios - average_radius_ratios) < 1e-14
    assert (
        abs(min_radius_ratios - np.min(fenics.MeshQuality.radius_ratio_min_max(mesh)))
        < 1e-14
    )

    assert abs(min_condition - average_condition) < 1e-14
    assert abs(min_condition - 0.4714045207910318) < 1e-14


def test_mesh_quality_3D():
    mesh, _, _, _, _, _ = cashocs.regular_mesh(2, 1.0, 1.0, 1.0)
    opt_angle = np.arccos(1 / 3)
    dh_min_max = fenics.MeshQuality.dihedral_angles_min_max(mesh)
    alpha_min = dh_min_max[0]
    alpha_max = dh_min_max[1]

    q_1 = 1 - np.maximum(
        (alpha_max - opt_angle) / (np.pi - opt_angle),
        (opt_angle - alpha_max) / (opt_angle),
    )
    q_2 = 1 - np.maximum(
        (alpha_min - opt_angle) / (np.pi - opt_angle),
        (opt_angle - alpha_min) / (opt_angle),
    )
    q = np.minimum(q_1, q_2)

    r_1 = 1 - np.maximum((alpha_max - opt_angle) / (np.pi - opt_angle), 0.0)
    r_2 = 1 - np.maximum((alpha_min - opt_angle) / (np.pi - opt_angle), 0.0)
    r = np.minimum(r_1, r_2)

    min_max_angle = MeshQuality.min_maximum_angle(mesh)
    min_radius_ratios = MeshQuality.min_radius_ratios(mesh)
    min_skewness = MeshQuality.min_skewness(mesh)
    average_radius_ratios = MeshQuality.avg_radius_ratios(mesh)
    min_condition = MeshQuality.min_condition_number(mesh)
    average_condition = MeshQuality.avg_condition_number(mesh)

    assert abs(min_max_angle - MeshQuality.avg_maximum_angle(mesh)) < 1e-14
    assert abs(min_max_angle - r) < 1e-14

    assert abs(min_skewness - MeshQuality.avg_skewness(mesh)) < 1e-14
    assert abs(min_skewness - q) < 1e-14

    assert abs(min_radius_ratios - average_radius_ratios) < 1e-14
    assert (
        abs(min_radius_ratios - np.min(fenics.MeshQuality.radius_ratio_min_max(mesh)))
        < 1e-14
    )

    assert abs(min_condition - average_condition) < 1e-14
    assert abs(min_condition - 0.3162277660168379) < 1e-14


def test_write_mesh():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    subprocess.run(
        ["cashocs-convert", f"{dir_path}/mesh/mesh.msh", f"{dir_path}/mesh/mesh.xdmf"],
        check=True,
    )
    mesh, subdomains, boundaries, dx, ds, dS = cashocs.import_mesh(
        dir_path + "/mesh/mesh.xdmf"
    )

    cashocs.utils.write_out_mesh(
        mesh, dir_path + "/mesh/mesh.msh", dir_path + "/mesh/test.msh"
    )

    subprocess.run(
        ["cashocs-convert", f"{dir_path}/mesh/test.msh", f"{dir_path}/mesh/test.xdmf"],
        check=True,
    )
    test, _, _, _, _, _ = cashocs.import_mesh(dir_path + "/mesh/test.xdmf")

    assert np.allclose(test.coordinates()[:, :], mesh.coordinates()[:, :])

    subprocess.run(["rm", f"{dir_path}/mesh/test.msh"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/test.xdmf"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/test.h5"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/test_subdomains.xdmf"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/test_subdomains.h5"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/test_boundaries.xdmf"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/test_boundaries.h5"], check=True)

    subprocess.run(["rm", f"{dir_path}/mesh/mesh.xdmf"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/mesh.h5"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/mesh_subdomains.xdmf"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/mesh_subdomains.h5"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/mesh_boundaries.xdmf"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/mesh_boundaries.h5"], check=True)


def test_empty_measure():
    mesh, _, _, dx, ds, dS = cashocs.regular_mesh(5)
    V = fenics.FunctionSpace(mesh, "CG", 1)
    dm = cashocs.utils.EmptyMeasure(dx)

    trial = fenics.TrialFunction(V)
    test = fenics.TestFunction(V)

    assert fenics.assemble(1 * dm) == 0.0
    assert (fenics.assemble(test * dm).norm("linf")) == 0.0
    assert (fenics.assemble(trial * test * dm).norm("linf")) == 0.0


def test_convert_coordinate_defo_to_dof_defo():
    mesh, _, _, _, _, _ = cashocs.regular_mesh(20)
    coordinates_initial = mesh.coordinates().copy()
    deformation_handler = cashocs.DeformationHandler(mesh)
    coordinate_deformation = rng.randn(
        mesh.coordinates().shape[0], mesh.coordinates().shape[1]
    )
    h = mesh.hmin()
    coordinate_deformation *= h / (4.0 * np.max(np.abs(coordinate_deformation)))

    coordinates_transformed = coordinates_initial + coordinate_deformation

    vector_field = deformation_handler.coordinate_to_dof(coordinate_deformation)
    assert deformation_handler.move_mesh(vector_field)
    assert np.max(np.abs(mesh.coordinates()[:, :] - coordinates_transformed)) <= 1e-15


def test_convert_dof_defo_to_coordinate_defo():
    mesh, _, _, _, _, _ = cashocs.regular_mesh(20)
    coordinates_initial = mesh.coordinates().copy()
    deformation_handler = cashocs.DeformationHandler(mesh)
    VCG = fenics.VectorFunctionSpace(mesh, "CG", 1)
    dof_vector = rng.randn(VCG.dim())
    h = mesh.hmin()
    dof_vector *= h / (4.0 * np.max(np.abs(dof_vector)))
    defo = fenics.Function(VCG)
    defo.vector()[:] = dof_vector

    coordinate_deformation = deformation_handler.dof_to_coordinate(defo)
    coordinates_transformed = coordinates_initial + coordinate_deformation
    assert deformation_handler.move_mesh(defo)
    assert np.max(np.abs(mesh.coordinates()[:, :] - coordinates_transformed)) <= 1e-15


def test_move_mesh():
    mesh, _, _, _, _, _ = cashocs.regular_mesh(20)
    coordinates_initial = mesh.coordinates().copy()
    deformation_handler = cashocs.DeformationHandler(mesh)
    coordinate_deformation = rng.randn(
        mesh.coordinates().shape[0], mesh.coordinates().shape[1]
    )
    h = mesh.hmin()
    coordinate_deformation *= h / (4.0 * np.max(np.abs(coordinate_deformation)))

    coordinates_added = coordinates_initial + coordinate_deformation
    assert deformation_handler.move_mesh(coordinate_deformation)
    coordinates_moved = mesh.coordinates().copy()
    deformation_handler.revert_transformation()

    vector_field = deformation_handler.coordinate_to_dof(coordinate_deformation)
    assert deformation_handler.move_mesh(vector_field)
    coordinates_dof_moved = mesh.coordinates().copy()

    assert np.max(np.abs(coordinates_added - coordinates_dof_moved)) <= 1e-15
    assert np.max(np.abs(coordinates_added - coordinates_moved)) <= 1e-15
    assert np.max(np.abs(coordinates_dof_moved - coordinates_moved)) <= 1e-15


def test_eikonal_distance():
    mesh, _, boundaries, _, _, _ = cashocs.regular_mesh(16)
    dist = cashocs.geometry.compute_boundary_distance(mesh, boundaries, [1, 2, 3, 4])
    assert np.min(dist.vector()[:]) >= 0.0
    assert (np.max(dist.vector()[:]) - 0.5) / 0.5 <= 0.05

    dist = cashocs.geometry.compute_boundary_distance(mesh, boundaries, [1])
    assert np.min(dist.vector()[:]) >= 0.0
    assert (np.max(dist.vector()[:]) - 1.0) / 1.0 <= 0.05


def test_named_mesh_import():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    cashocs._cli.convert(
        [f"{dir_path}/mesh/named_mesh.msh", f"{dir_path}/mesh/named_mesh.xdmf"]
    )

    mesh, subdomains, boundaries, dx, ds, dS = cashocs.import_mesh(
        f"{dir_path}/mesh/named_mesh.xdmf"
    )

    assert fenics.assemble(1 * dx("volume")) == fenics.assemble(1 * dx(1))
    assert fenics.assemble(1 * ds("inlet")) == fenics.assemble(1 * ds(1))
    assert fenics.assemble(1 * ds("wall")) == fenics.assemble(1 * ds(2))
    assert fenics.assemble(1 * ds("outlet")) == fenics.assemble(1 * ds(3))

    assert dx("volume") == dx(1)
    assert ds("inlet") == ds(1)
    assert ds("wall") == ds(2)
    assert ds("outlet") == ds(3)

    with pytest.raises(InputError) as e_info:
        dx("inlet")
        assert "subdomain_id" in str(e_info.value)

    with pytest.raises(InputError) as e_info:
        ds("volume")
        assert "subdomain_id" in str(e_info.value)

    with pytest.raises(InputError) as e_info:
        dx("fantasy")
        assert "subdomain_id" in str(e_info.value)

    assert os.path.isfile(f"{dir_path}/mesh/named_mesh.xdmf")
    assert os.path.isfile(f"{dir_path}/mesh/named_mesh.h5")
    assert os.path.isfile(f"{dir_path}/mesh/named_mesh_subdomains.xdmf")
    assert os.path.isfile(f"{dir_path}/mesh/named_mesh_subdomains.h5")
    assert os.path.isfile(f"{dir_path}/mesh/named_mesh_boundaries.xdmf")
    assert os.path.isfile(f"{dir_path}/mesh/named_mesh_boundaries.h5")
    assert os.path.isfile(f"{dir_path}/mesh/named_mesh_physical_groups.json")

    subprocess.run(["rm", f"{dir_path}/mesh/named_mesh.xdmf"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/named_mesh.h5"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/named_mesh_subdomains.xdmf"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/named_mesh_subdomains.h5"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/named_mesh_boundaries.xdmf"], check=True)
    subprocess.run(["rm", f"{dir_path}/mesh/named_mesh_boundaries.h5"], check=True)
    subprocess.run(
        ["rm", f"{dir_path}/mesh/named_mesh_physical_groups.json"], check=True
    )
