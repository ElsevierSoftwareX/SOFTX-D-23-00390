"""
Created on 18/10/2021, 08.44

@author: blauths
"""

import os

import numpy as np
from fenics import *

import cashocs



rng = np.random.RandomState(300696)
dir_path = os.path.dirname(os.path.realpath(__file__))

meshlevel = 10
degree = 1
dim = 2
mesh = UnitDiscMesh.create(MPI.comm_world, meshlevel, degree, dim)
initial_coordinates = mesh.coordinates().copy()
dx = Measure("dx", mesh)
ds = Measure("ds", mesh)

boundary = CompiledSubDomain("on_boundary")
boundaries = MeshFunction("size_t", mesh, dim=1)
boundary.mark(boundaries, 1)

V = FunctionSpace(mesh, "CG", 1)

bcs = DirichletBC(V, Constant(0), boundaries, 1)

x = SpatialCoordinate(mesh)
f = 2.5 * pow(x[0] + 0.4 - pow(x[1], 2), 2) + pow(x[0], 2) + pow(x[1], 2) - 1

u = Function(V)
p = Function(V)

e = inner(grad(u), grad(p)) * dx - f * p * dx

J = u * dx


def test_2_laplacian():
    config = cashocs.load_config(dir_path + "/config_sop.ini")
    mesh.coordinates()[:, :] = initial_coordinates
    mesh.bounding_box_tree().build(mesh)

    space = VectorFunctionSpace(mesh, "CG", 1)
    shape_scalar_product = (
        Constant(1)
        * inner((grad(TrialFunction(space))), (grad(TestFunction(space))))
        * dx
        + dot(TrialFunction(space), TestFunction(space)) * dx
    )

    config.set("ShapeGradient", "mu_def", "1.0")
    config.set("ShapeGradient", "mu_fix", "1.0")
    config.set("ShapeGradient", "damping_factor", "1.0")
    config.set("ShapeGradient", "use_p_laplacian", "True")
    config.set("ShapeGradient", "p_laplacian_power", "2")
    config.set("ShapeGradient", "p_laplacian_stabilization", "0.0")

    sop1 = cashocs.ShapeOptimizationProblem(e, bcs, J, u, p, boundaries, config)
    sop1.solve(algorithm="gd", rtol=1e-2, max_iter=21)

    config.set("ShapeGradient", "use_p_laplacian", "True")
    mesh.coordinates()[:, :] = initial_coordinates
    mesh.bounding_box_tree().build(mesh)
    sop2 = cashocs.ShapeOptimizationProblem(
        e, bcs, J, u, p, boundaries, config, shape_scalar_product=shape_scalar_product
    )
    sop2.solve(algorithm="gd", rtol=1e-2, max_iter=21)

    assert (
        np.abs(sop1.solver.objective_value - sop2.solver.objective_value)
        / np.abs(sop1.solver.objective_value)
        < 1e-10
    )
    assert (
        np.abs(sop1.solver.gradient_norm - sop2.solver.gradient_norm)
        / np.abs(sop1.solver.gradient_norm)
        < 1e-8
    )


def test_p_laplacian():
    config = cashocs.load_config(dir_path + "/config_sop.ini")
    mesh.coordinates()[:, :] = initial_coordinates
    mesh.bounding_box_tree().build(mesh)

    config.set("ShapeGradient", "mu_def", "1.0")
    config.set("ShapeGradient", "mu_fix", "1.0")
    config.set("ShapeGradient", "damping_factor", "1.0")
    config.set("ShapeGradient", "use_p_laplacian", "True")
    config.set("ShapeGradient", "p_laplacian_power", "10")
    config.set("ShapeGradient", "p_laplacian_stabilization", "0.0")

    sop = cashocs.ShapeOptimizationProblem(e, bcs, J, u, p, boundaries, config)
    sop.solve(algorithm="gd", rtol=1e-1, max_iter=6)

    assert sop.solver.relative_norm <= 1e-1
