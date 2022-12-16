# Copyright (C) 2020-2022 Sebastian Blauth
#
# This file is part of cashocs.
#
# cashocs is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cashocs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cashocs.  If not, see <https://www.gnu.org/licenses/>.

"""Implementation of a topology optimization problem."""

from __future__ import annotations

import copy
from typing import Callable, TYPE_CHECKING

import fenics
import ufl

from cashocs import _optimization
from cashocs import _utils
from cashocs import io
from cashocs._optimization import line_search as ls
from cashocs._optimization.optimal_control import optimal_control_problem
from cashocs._optimization.topology_optimization import descent_topology_algorithm
from cashocs._optimization.topology_optimization import topology_optimization_algorithm
from cashocs._optimization.topology_optimization import topology_variable_abstractions

if TYPE_CHECKING:
    from cashocs import _forms
    from cashocs import _pde_problems
    from cashocs import _typing


class TopologyOptimizationProblem(_optimization.OptimizationProblem):
    r"""A topology optimization problem.

    This class is used to define a topology optimization problem, and to solve
    it subsequently. For a detailed documentation, we refer to the
    :ref:`tutorial <tutorial_index>`. For easier input, when considering single (state
    or control) variables, these do not have to be wrapped into a list. Note, that in
    the case of multiple variables these have to be grouped into ordered lists, where
    ``state_forms``, ``bcs_list``, ``states``, ``adjoints`` have to have the same order
    (i.e. ``[y1, y2]`` and ``[p1, p2]``, where ``p1`` is the adjoint of ``y1`` and so
    on).
    """

    solver: topology_optimization_algorithm.TopologyOptimizationAlgorithm

    def __init__(  # pylint: disable=unused-argument
        self,
        state_forms: list[ufl.Form] | ufl.Form,
        bcs_list: list[list[fenics.DirichletBC]]
        | list[fenics.DirichletBC]
        | fenics.DirichletBC,
        cost_functional_form: list[_typing.CostFunctional],
        states: list[fenics.Function] | fenics.Function,
        adjoints: list[fenics.Function] | fenics.Function,
        levelset_function: fenics.Function,
        topological_derivative_neg: fenics.Function | ufl.Form,
        topological_derivative_pos: fenics.Function | ufl.Form,
        update_levelset: Callable,
        config: io.Config | None = None,
        riesz_scalar_products: list[ufl.Form] | ufl.Form | None = None,
        initial_guess: list[fenics.Function] | None = None,
        ksp_options: _typing.KspOptions | list[list[str | int | float]] | None = None,
        adjoint_ksp_options: _typing.KspOptions
        | list[list[str | int | float]]
        | None = None,
        desired_weights: list[float] | None = None,
    ) -> None:
        r"""Initializes the topology optimization problem.

        Args:
            state_forms: The weak form of the state equation (user implemented). Can be
                either a single UFL form, or a (ordered) list of UFL forms.
            bcs_list: The list of :py:class:`fenics.DirichletBC` objects describing
                Dirichlet (essential) boundary conditions. If this is ``None``, then no
                Dirichlet boundary conditions are imposed.
            cost_functional_form: UFL form of the cost functional. Can also be a list of
                summands of the cost functional
            states: The state variable(s), can either be a :py:class:`fenics.Function`,
                or a list of these.
            adjoints: The adjoint variable(s), can either be a
                :py:class:`fenics.Function`, or a (ordered) list of these.
            levelset_function: A :py:class:`fenics.Function` which represents the
                levelset function.
            topological_derivative_neg: The topological derivative inside the domain,
                where the levelset function is negative.
            topological_derivative_pos: The topological derivative inside the domain,
                where the levelset function is positive.
            update_levelset: A python function (without arguments) which is called to
                update the coefficients etc. when the levelset function is changed.
            config: The config file for the problem, generated via
                :py:func:`cashocs.create_config`. Alternatively, this can also be
                ``None``, in which case the default configurations are used, except for
                the optimization algorithm. This has then to be specified in the
                :py:meth:`solve <cashocs.OptimalControlProblem.solve>` method. The
                default is ``None``.
            riesz_scalar_products: The scalar products of the control space. Can either
                be ``None`` or a single UFL form. If it is ``None``, the
                :math:`L^2(\Omega)` product is used (default is ``None``).
            initial_guess: List of functions that act as initial guess for the state
                variables, should be valid input for :py:func:`fenics.assign`. Defaults
                to ``None``, which means a zero initial guess.
            ksp_options: A list of strings corresponding to command line options for
                PETSc, used to solve the state systems. If this is ``None``, then the
                direct solver mumps is used (default is ``None``).
            adjoint_ksp_options: A list of strings corresponding to command line options
                for PETSc, used to solve the adjoint systems. If this is ``None``, then
                the same options as for the state systems are used (default is
                ``None``).
            desired_weights: A list of values for scaling the cost functional terms. If
                this is supplied, the cost functional has to be given as list of
                summands. The individual terms are then scaled, so that term `i` has the
                magnitude of `desired_weights[i]` for the initial iteration. In case
                that `desired_weights` is `None`, no scaling is performed. Default is
                `None`.

        """
        super().__init__(
            state_forms,
            bcs_list,
            cost_functional_form,
            states,
            adjoints,
            config=config,
            initial_guess=initial_guess,
            ksp_options=ksp_options,
            adjoint_ksp_options=adjoint_ksp_options,
            desired_weights=desired_weights,
        )

        self.db.parameter_db.problem_type = "topology"
        self.mesh_parametrization = None

        self.levelset_function = levelset_function
        self.topological_derivative_pos = topological_derivative_pos
        self.topological_derivative_neg = topological_derivative_neg
        self.update_levelset = update_levelset
        self.riesz_scalar_products = riesz_scalar_products

        self.is_topology_problem = True
        self.update_levelset()

        self.topological_derivative_is_identical = self.config.getboolean(
            "TopologyOptimization", "topological_derivative_is_identical"
        )
        self.re_normalize_levelset = self.config.getboolean(
            "TopologyOptimization", "re_normalize_levelset"
        )
        self.normalize_topological_derivative = self.config.getboolean(
            "TopologyOptimization", "normalize_topological_derivative"
        )
        self.interpolation_scheme = self.config.get(
            "TopologyOptimization", "interpolation_scheme"
        )

        self.mesh = self.levelset_function.function_space().mesh()
        self.dg0_space = fenics.FunctionSpace(self.mesh, "DG", 0)

        ocp_config = copy.deepcopy(self.config)
        ocp_config.set("Output", "verbose", "False")
        ocp_config.set("Output", "save_txt", "False")
        ocp_config.set("Output", "save_results", "False")
        ocp_config.set("Output", "save_state", "False")
        ocp_config.set("Output", "save_adjoint", "False")
        ocp_config.set("Output", "save_gradient", "False")
        ocp_config.set("OptimizationRoutine", "soft_exit", "True")
        ocp_config.set("OptimizationRoutine", "rtol", "0.0")
        ocp_config.set("OptimizationRoutine", "atol", "0.0")
        self._base_ocp = optimal_control_problem.OptimalControlProblem(
            self.state_forms,
            self.bcs_list,
            self.cost_functional_list,
            self.states,
            self.levelset_function,
            self.adjoints,
            config=ocp_config,
            riesz_scalar_products=self.riesz_scalar_products,
            initial_guess=initial_guess,
            ksp_options=ksp_options,
            adjoint_ksp_options=adjoint_ksp_options,
            desired_weights=desired_weights,
        )
        self._base_ocp.db.parameter_db.problem_type = "topology"
        self.db.function_db.control_spaces = (
            self._base_ocp.db.function_db.control_spaces
        )
        self.db.function_db.controls = self._base_ocp.db.function_db.controls
        self.form_handler: _forms.ControlFormHandler = self._base_ocp.form_handler
        self.state_problem: _pde_problems.StateProblem = self._base_ocp.state_problem
        self.adjoint_problem: _pde_problems.AdjointProblem = (
            self._base_ocp.adjoint_problem
        )
        self.gradient_problem: _pde_problems.ControlGradientProblem = (
            self._base_ocp.gradient_problem
        )
        self.reduced_cost_functional = self._base_ocp.reduced_cost_functional

    def _erase_pde_memory(self) -> None:
        super()._erase_pde_memory()
        pass

    def gradient_test(self) -> float:
        """Gradient test for topology optimization - not implemented."""
        raise NotImplementedError(
            "Gradient test is not implemented for topology optimization."
        )

    def solve(
        self,
        algorithm: str | None = None,
        rtol: float | None = None,
        atol: float | None = None,
        max_iter: int | None = None,
        angle_tol: float | None = None,
    ) -> None:
        """Solves the optimization problem.

        Args:
            algorithm: Selects the optimization algorithm. Valid choices are
                ``'gradient_descent'`` or ``'gd'`` for a gradient descent method,
                ``'conjugate_gradient'``, ``'nonlinear_cg'``, ``'ncg'`` or ``'cg'``
                for nonlinear conjugate gradient methods, ``'lbfgs'`` or ``'bfgs'``
                for limited memory BFGS methods, ``'sphere_combination'`` for Euler's
                method on the spehere, and ``'convex_combination'`` for a convex
                combination approach.
            rtol: The relative tolerance used for the termination criterion (i.e. the
                norm of the projected topological gradient). If this is ``None``, then
                the value provided in the config file is used. Default is ``None``.
            atol: The absolute tolerance for the termination criterion (i.e. the
                norm of the projected topological gradient). If this is ``None``, then
                the value provided in the config file is used. Default is ``None``.
            max_iter: The maximum number of iterations the optimization algorithm
                can carry out before it is terminated. If this is ``None``, then
                the value provided in the config file is used. Default is ``None``.
            angle_tol: The absolute tolerance for the angle between topological
                derivative and levelset function. If this is ``None``, then
                the value provided in the config file is used. Default is ``None``.

        """
        self.optimization_variable_abstractions = (
            topology_variable_abstractions.TopologyVariableAbstractions(self, self.db)
        )

        line_search_type = self.config.get("LineSearch", "method").casefold()
        if line_search_type == "armijo":
            line_search: ls.LineSearch = ls.ArmijoLineSearch(self.db, self)
        elif line_search_type == "polynomial":
            line_search = ls.PolynomialLineSearch(self.db, self)
        else:
            raise Exception("This code cannot be reached.")

        self._set_tolerances(rtol, atol, max_iter)
        if angle_tol is not None:
            self.config.set("TopologyOptimization", "angle_tol", str(angle_tol))

        if algorithm is None:
            self.algorithm = _utils.optimization_algorithm_configuration(
                self.config, algorithm
            )
        else:
            self.algorithm = algorithm

        if self.algorithm.casefold() == "sphere_combination":
            self.solver = topology_optimization_algorithm.SphereCombinationAlgorithm(
                self.db, self, line_search
            )
        elif self.algorithm.casefold() == "convex_combination":
            self.solver = topology_optimization_algorithm.ConvexCombinationAlgorithm(
                self.db, self, line_search
            )
        else:
            self.solver = descent_topology_algorithm.DescentTopologyAlgorithm(
                self.db, self, line_search, self.algorithm
            )

        self.solver.run()
        self.solver.post_process()

    def plot_shape(self) -> None:
        """Visualize the current shape in a plot."""
        shape = fenics.Function(self.dg0_space)
        _utils.interpolate_levelset_function_to_cells(
            self.levelset_function, 1.0, 0.0, shape
        )
        fenics.plot(shape)
