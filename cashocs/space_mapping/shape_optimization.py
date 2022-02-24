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

"""Space mapping for shape optimization problems."""

from __future__ import annotations

import abc
import collections
import configparser
from typing import Dict, List, Optional, TYPE_CHECKING, Union

import fenics
import numpy as np
from typing_extensions import Literal
import ufl

from cashocs import _exceptions
from cashocs import _utils
from cashocs import geometry
from cashocs._optimization.shape_optimization import shape_optimization_problem as sop

if TYPE_CHECKING:
    from cashocs import io


class FineModel(abc.ABC):
    """Base class for the fine model in space mapping shape optimization.

    Attributes:
        mesh: The FEM mesh for the fine model.
        cost_functional_value: The current cost functional value of the fine model.

    """

    def __init__(self, mesh: fenics.Mesh):
        """Initializes self.

        Args:
            mesh: The finite element mesh of the coarse model, used for the space
                mapping with the fine model.

        """
        self.mesh = fenics.Mesh(mesh)
        self.cost_functional_value = None

    @abc.abstractmethod
    def solve_and_evaluate(self):
        """Solves and evaluates the fine model.

        This needs to be overwritten with a custom implementation.

        """
        pass


class CoarseModel:
    """Coarse Model for space mapping shape optimization."""

    def __init__(
        self,
        state_forms: Union[ufl.Form, List[ufl.Form]],
        bcs_list: Union[
            fenics.DirichletBC,
            List[fenics.DirichletBC],
            List[List[fenics.DirichletBC]],
            None,
        ],
        cost_functional_form: Union[ufl.Form, List[ufl.Form]],
        states: Union[fenics.Function, List[fenics.Function]],
        adjoints: Union[fenics.Function, List[fenics.Function]],
        boundaries: fenics.MeshFunction,
        config: Optional[io.Config] = None,
        shape_scalar_product: Optional[ufl.Form] = None,
        initial_guess: Optional[List[fenics.Function]] = None,
        ksp_options: Optional[List[List[List[str]]]] = None,
        adjoint_ksp_options: Optional[List[List[List[str]]]] = None,
        scalar_tracking_forms: Optional[Dict] = None,
        min_max_terms: Optional[Dict] = None,
        desired_weights: Optional[List[float]] = None,
    ):
        """Initializes self.

        Args:
            state_forms: The list of weak forms for the coare state problem
            bcs_list: The list of boundary conditions for the coarse problem
            cost_functional_form: The cost functional for the coarse problem
            states: The state variables for the coarse problem
            adjoints: The adjoint variables for the coarse problem
            boundaries: A fenics MeshFunction which marks the boundaries.
            config: The configuration for the problem
            shape_scalar_product: The scalar product for the shape optimization problem
            initial_guess: The initial guess for solving a nonlinear state equation
            ksp_options: The list of PETSc options for the state equations
            adjoint_ksp_options: The list of PETSc options for the adjoint equations
            scalar_tracking_forms: The list of scalar tracking forms
            min_max_terms: The list of min and max terms (squared)
            desired_weights: The desired weights for the cost functional

        """
        self.state_forms = state_forms
        self.bcs_list = bcs_list
        self.cost_functional_form = cost_functional_form
        self.states = states
        self.adjoints = adjoints
        self.boundaries = boundaries
        self.config = config
        self.shape_scalar_product = shape_scalar_product
        self.initial_guess = initial_guess
        self.ksp_options = ksp_options
        self.adjoint_ksp_options = adjoint_ksp_options
        self.scalar_tracking_forms = scalar_tracking_forms
        self.min_max_terms = min_max_terms
        self.desired_weights = desired_weights

        # noinspection PyUnresolvedReferences
        self.mesh = self.boundaries.mesh()
        self.coordinates_initial = self.mesh.coordinates().copy()
        self.coordinates_optimal = None

        self.shape_optimization_problem = sop.ShapeOptimizationProblem(
            self.state_forms,
            self.bcs_list,
            self.cost_functional_form,
            self.states,
            self.adjoints,
            self.boundaries,
            config=self.config,
            shape_scalar_product=self.shape_scalar_product,
            initial_guess=self.initial_guess,
            ksp_options=self.ksp_options,
            adjoint_ksp_options=self.adjoint_ksp_options,
            scalar_tracking_forms=self.scalar_tracking_forms,
            min_max_terms=self.min_max_terms,
            desired_weights=self.desired_weights,
        )

    def optimize(self) -> None:
        """Solves the coarse model optimization problem."""
        self.shape_optimization_problem.solve()
        self.coordinates_optimal = self.mesh.coordinates().copy()


class ParameterExtraction:
    """Parameter extraction for space mapping shape optimization."""

    def __init__(
        self,
        coarse_model: CoarseModel,
        cost_functional_form: Union[ufl.Form, List[ufl.Form]],
        states: Union[fenics.Function, List[fenics.Function]],
        config: Optional[configparser.ConfigParser] = None,
        scalar_tracking_forms: Optional[Dict] = None,
        desired_weights: Optional[List[float]] = None,
    ) -> None:
        """Initializes self.

        Args:
            coarse_model: The coarse model optimization problem
            cost_functional_form: The cost functional for the parameter extraction
            states: The state variables for the parameter extraction
            config: The configuration for the parameter extraction
            scalar_tracking_forms: The scalar tracking forms for the parameter
                extraction
            desired_weights: The list of desired weights for the parameter extraction

        """
        self.coarse_model = coarse_model
        self.mesh = coarse_model.mesh
        self.cost_functional_form = cost_functional_form

        self.states = _utils.enlist(states)

        self.config = config
        self.scalar_tracking_forms = scalar_tracking_forms
        self.desired_weights = desired_weights

        self.adjoints = [
            fenics.Function(V)
            for V in coarse_model.shape_optimization_problem.form_handler.adjoint_spaces
        ]

        dict_states = {
            coarse_model.shape_optimization_problem.states[i]: self.states[i]
            for i in range(len(self.states))
        }
        dict_adjoints = {
            coarse_model.shape_optimization_problem.adjoints[i]: self.adjoints[i]
            for i in range(len(self.adjoints))
        }
        mapping_dict = {}
        mapping_dict.update(dict_states)
        mapping_dict.update(dict_adjoints)

        self.state_forms = [
            ufl.replace(form, mapping_dict)
            for form in coarse_model.shape_optimization_problem.state_forms
        ]
        self.bcs_list = coarse_model.shape_optimization_problem.bcs_list
        self.shape_scalar_product = (
            coarse_model.shape_optimization_problem.shape_scalar_product
        )
        self.boundaries = coarse_model.shape_optimization_problem.boundaries
        self.initial_guess = coarse_model.shape_optimization_problem.initial_guess
        self.ksp_options = coarse_model.shape_optimization_problem.ksp_options
        self.adjoint_ksp_options = (
            coarse_model.shape_optimization_problem.adjoint_ksp_options
        )

        self.coordinates_initial = coarse_model.coordinates_initial
        self.deformation_handler = geometry.DeformationHandler(self.mesh)

        self.shape_optimization_problem = None

    def _solve(self, initial_guess: np.ndarray = None) -> None:
        """Solves the parameter extraction problem.

        Args:
            initial_guess: The initial guesses for solving the problem.

        """
        if initial_guess is None:
            self.deformation_handler.assign_coordinates(self.coordinates_initial)
        else:
            self.deformation_handler.assign_coordinates(initial_guess)

        self.shape_optimization_problem = sop.ShapeOptimizationProblem(
            self.state_forms,
            self.bcs_list,
            self.cost_functional_form,
            self.states,
            self.adjoints,
            self.boundaries,
            config=self.config,
            shape_scalar_product=self.shape_scalar_product,
            initial_guess=self.initial_guess,
            ksp_options=self.ksp_options,
            adjoint_ksp_options=self.adjoint_ksp_options,
            desired_weights=self.desired_weights,
            scalar_tracking_forms=self.scalar_tracking_forms,
        )

        self.shape_optimization_problem.solve()


class SpaceMapping:
    """Space mapping method for shape optimization."""

    def __init__(
        self,
        fine_model: FineModel,
        coarse_model: CoarseModel,
        parameter_extraction: ParameterExtraction,
        method: Literal[
            "broyden", "bfgs", "lbfgs", "sd", "steepest_descent", "ncg"
        ] = "broyden",
        max_iter: int = 25,
        tol: float = 1e-2,
        use_backtracking_line_search: bool = False,
        broyden_type: Literal["good", "bad"] = "good",
        cg_type: Literal["FR", "PR", "HS", "DY", "HZ"] = "FR",
        memory_size: int = 10,
        verbose: bool = True,
    ) -> None:
        """Initializes self.

        Args:
            fine_model: The fine model optimization problem
            coarse_model: The coarse model optimization problem
            parameter_extraction: The parameter extraction problem
            method: A string, which indicates which method is used to solve the space
                mapping. Can be one of "broyden", "bfgs", "lbfgs", "sd",
                "steepest descent", or "ncg". Default is "broyden".
            max_iter: Maximum number of space mapping iterations
            tol: The tolerance used for solving the space mapping iteration
            use_backtracking_line_search: A boolean flag, which indicates whether a
                backtracking line search should be used for the space mapping.
            broyden_type: A string, either "good" or "bad", determining the type of
                Broyden's method used. Default is "good"
            cg_type: A string, either "FR", "PR", "HS", "DY", "HZ", which indicates
                which NCG variant is used for solving the space mapping. Default is "FR"
            memory_size: The size of the memory for Broyden's method and the BFGS method
            verbose: A boolean flag which indicates, whether the output of the space
                mapping method should be verbose. Default is ``True``.
        """
        self.fine_model = fine_model
        self.coarse_model = coarse_model
        self.parameter_extraction = parameter_extraction
        self.method = method
        if self.method == "sd":
            self.method = "steepest_descent"
        elif self.method == "lbfgs":
            self.method = "bfgs"
        self.max_iter = max_iter
        self.tol = tol
        self.use_backtracking_line_search = use_backtracking_line_search
        self.broyden_type = broyden_type
        self.cg_type = cg_type
        self.memory_size = memory_size
        self.verbose = verbose

        self.coordinates_initial = self.coarse_model.coordinates_initial

        self.eps = 1.0
        self.converged = False
        self.iteration = 0

        self.x = self.fine_model.mesh

        self.VCG = fenics.VectorFunctionSpace(self.x, "CG", 1)
        self.deformation_handler_fine = geometry.DeformationHandler(
            self.fine_model.mesh
        )
        self.deformation_handler_coarse = geometry.DeformationHandler(
            self.coarse_model.mesh
        )

        self.z_star = [fenics.Function(self.VCG)]
        self.norm_z_star = 1.0
        self.p_current = [fenics.Function(self.VCG)]
        self.p_prev = [fenics.Function(self.VCG)]
        self.h = [fenics.Function(self.VCG)]
        self.v = [fenics.Function(self.VCG)]
        self.u = [fenics.Function(self.VCG)]
        self.transformation = fenics.Function(self.VCG)

        self.stepsize = 1.0
        self.x_save = None
        self.current_mesh_quality = 1.0

        self.diff = [fenics.Function(self.VCG)]
        self.temp = [fenics.Function(self.VCG)]
        self.dir_prev = [fenics.Function(self.VCG)]
        self.difference = [fenics.Function(self.VCG)]

        self.history_s = collections.deque()
        self.history_y = collections.deque()
        self.history_rho = collections.deque()
        self.history_alpha = collections.deque()

    def _compute_initial_guess(self) -> None:
        """Compute initial guess for the space mapping by solving the coarse problem."""
        self.coarse_model.optimize()
        self.z_star = [
            self.deformation_handler_coarse.coordinate_to_dof(
                self.coarse_model.coordinates_optimal - self.coordinates_initial
            )
        ]
        self.deformation_handler_fine.assign_coordinates(
            self.coarse_model.coordinates_optimal
        )
        self.current_mesh_quality = geometry.compute_mesh_quality(self.fine_model.mesh)
        self.norm_z_star = np.sqrt(self._scalar_product(self.z_star, self.z_star))

    def solve(self) -> None:
        """Solves the problem with the space mapping method."""
        self._compute_initial_guess()

        self.fine_model.solve_and_evaluate()
        # self.parameter_extraction._solve()
        self.parameter_extraction._solve(
            initial_guess=self.coarse_model.coordinates_optimal
        )
        self.p_current[0].vector()[
            :
        ] = self.deformation_handler_coarse.coordinate_to_dof(
            self.parameter_extraction.mesh.coordinates()[:, :]
            - self.coordinates_initial
        ).vector()[
            :
        ]
        self.eps = self._compute_eps()

        if self.verbose:
            print(
                f"Space Mapping - Iteration {self.iteration:3d}:"
                f"    Cost functional value = "
                f"{self.fine_model.cost_functional_value:.3e}"
                f"    eps = {self.eps:.3e}"
                f"    Mesh Quality = {self.current_mesh_quality:1.2f}\n"
            )

        while not self.converged:
            self.dir_prev[0].vector()[:] = -(
                self.p_prev[0].vector()[:] - self.z_star[0].vector()[:]
            )
            self.temp[0].vector()[:] = -(
                self.p_current[0].vector()[:] - self.z_star[0].vector()[:]
            )
            self._compute_search_direction(self.temp, self.h)

            self.stepsize = 1.0
            self.p_prev[0].vector()[:] = self.p_current[0].vector()[:]

            self._update_iterates()

            self.iteration += 1
            self.current_mesh_quality = geometry.compute_mesh_quality(
                self.fine_model.mesh
            )
            if self.verbose:
                print(
                    f"Space Mapping - Iteration {self.iteration:3d}:"
                    f"    Cost functional value = "
                    f"{self.fine_model.cost_functional_value:.3e}"
                    f"    eps = {self.eps:.3e}"
                    f"    Mesh Quality = {self.current_mesh_quality:1.2f}"
                    f"    step size = {self.stepsize:.3e}"
                )

            if self.eps <= self.tol:
                self.converged = True
                break
            if self.iteration >= self.max_iter:
                break

            self._update_broyden_approximation()
            self._update_bfgs_approximation()

        if self.converged:
            output = (
                f"\nStatistics --- "
                f"Space mapping iterations: {self.iteration:4d} --- "
                f"Final objective value: {self.fine_model.cost_functional_value:.3e}\n"
            )
            if self.verbose:
                print(output)

    def _update_broyden_approximation(self) -> None:
        """Updates the approximation of the mapping function with Broyden's method."""
        if self.method == "broyden":
            self.temp[0].vector()[:] = (
                self.p_current[0].vector()[:] - self.p_prev[0].vector()[:]
            )
            self._compute_broyden_application(self.temp, self.v)

            if self.memory_size > 0:
                if self.broyden_type == "good":
                    divisor = self._scalar_product(self.h, self.v)
                    self.u[0].vector()[:] = (
                        self.h[0].vector()[:] - self.v[0].vector()[:]
                    ) / divisor

                    self.history_s.append([xx.copy(True) for xx in self.u])
                    self.history_y.append([xx.copy(True) for xx in self.h])

                elif self.broyden_type == "bad":
                    divisor = self._scalar_product(self.temp, self.temp)
                    self.u[0].vector()[:] = (
                        self.h[0].vector()[:] - self.v[0].vector()[:]
                    ) / divisor

                    self.history_s.append([xx.copy(True) for xx in self.u])
                    self.history_y.append([xx.copy(True) for xx in self.temp])

                if len(self.history_s) > self.memory_size:
                    self.history_s.popleft()
                    self.history_y.popleft()

    def _update_bfgs_approximation(self) -> None:
        """Updates the approximation of the mapping function with the BFGS method."""
        if self.method == "bfgs":
            if self.memory_size > 0:
                self.temp[0].vector()[:] = (
                    self.p_current[0].vector()[:] - self.p_prev[0].vector()[:]
                )

                self.history_y.appendleft([xx.copy(True) for xx in self.temp])
                self.history_s.appendleft([xx.copy(True) for xx in self.h])
                curvature_condition = self._scalar_product(self.temp, self.h)

                if curvature_condition <= 0.0:
                    self.history_s.clear()
                    self.history_y.clear()
                    self.history_rho.clear()
                else:
                    rho = 1 / curvature_condition
                    self.history_rho.appendleft(rho)

                if len(self.history_s) > self.memory_size:
                    self.history_s.pop()
                    self.history_y.pop()
                    self.history_rho.pop()

    def _update_iterates(self) -> None:
        """Updates the iterates either directly or via a line search."""
        if not self.use_backtracking_line_search:
            success = self.deformation_handler_fine.move_mesh(self.h[0])
            if not success:
                raise _exceptions.CashocsException(
                    "The assignment of mesh coordinates was not "
                    "possible due to intersections"
                )

            self.fine_model.solve_and_evaluate()
            # self.parameter_extraction._solve()
            self.parameter_extraction._solve(
                initial_guess=self.coarse_model.coordinates_optimal
            )
            self.p_current[0].vector()[
                :
            ] = self.deformation_handler_coarse.coordinate_to_dof(
                self.parameter_extraction.mesh.coordinates()[:, :]
                - self.coordinates_initial
            ).vector()[
                :
            ]
            self.eps = self._compute_eps()

        else:
            self.x_save = self.x.coordinates().copy()

            while True:
                if self.stepsize <= 1e-4:
                    raise _exceptions.NotConvergedError(
                        "Space Mapping Backtracking Line Search",
                        "The line search did not converge.",
                    )

                self.transformation.vector()[:] = self.stepsize * self.h[0].vector()[:]
                success = self.deformation_handler_fine.move_mesh(self.transformation)
                if success:

                    self.fine_model.solve_and_evaluate()
                    # self.parameter_extraction._solve()
                    self.parameter_extraction._solve(
                        self.coarse_model.coordinates_optimal
                    )
                    self.p_current[0].vector()[
                        :
                    ] = self.deformation_handler_coarse.coordinate_to_dof(
                        self.parameter_extraction.mesh.coordinates()[:, :]
                        - self.coordinates_initial
                    ).vector()[
                        :
                    ]
                    eps_new = self._compute_eps()

                    if eps_new <= self.eps:
                        self.eps = eps_new
                        break
                    else:
                        self.stepsize /= 2

                else:
                    self.stepsize /= 2

    def _scalar_product(
        self, a: List[fenics.Function], b: List[fenics.Function]
    ) -> float:
        """Computes the scalar product between ``a`` and ``b``.

        Args:
            a: The first input for the scalar product
            b: The second input for the scalar product

        Returns:
            The scalar product between ``a`` and ``b``

        """
        return self.coarse_model.shape_optimization_problem.form_handler.scalar_product(
            a, b
        )

    def _compute_search_direction(
        self, q: List[fenics.Function], out: List[fenics.Function]
    ) -> None:
        """Computes the search direction for a given rhs ``q``, saved to ``out``.

        Args:
            q: The rhs for computing the search direction
            out: The output list of functions, in which the search direction is stored.

        """
        if self.method == "steepest_descent":
            return self._compute_steepest_descent_application(q, out)
        elif self.method == "broyden":
            return self._compute_broyden_application(q, out)
        elif self.method == "bfgs":
            return self._compute_bfgs_application(q, out)
        elif self.method == "ncg":
            return self._compute_ncg_direction(q, out)
        else:
            raise _exceptions.InputError(
                "cashocs.space_mapping.shape_optimization.SpaceMapping",
                "method",
                "The method is not supported.",
            )

    @staticmethod
    def _compute_steepest_descent_application(
        q: List[fenics.Function], out: List[fenics.Function]
    ) -> None:
        """Computes the search direction for the steepest descent method.

        Args:
            q: The rhs for computing the search direction
            out: The output list of functions, in which the search direction is stored.

        """
        for i in range(len(out)):
            out[i].vector()[:] = q[i].vector()[:]

    def _compute_broyden_application(
        self, q: List[fenics.Function], out: List[fenics.Function]
    ) -> None:
        """Computes the search direction for Broyden's method.

        Args:
            q: The rhs for computing the search direction
            out: The output list of functions, in which the search direction is stored.

        """
        out[0].vector()[:] = q[0].vector()[:]

        for i in range(len(self.history_s)):
            if self.broyden_type == "good":
                alpha = self._scalar_product(self.history_y[i], out)
            elif self.broyden_type == "bad":
                alpha = self._scalar_product(self.history_y[i], q)
            else:
                raise Exception(
                    "Type of Broyden's method has to be either 'good' or 'bad'."
                )

            out[0].vector()[:] += alpha * self.history_s[i][0].vector()[:]

    def _compute_bfgs_application(
        self, q: List[fenics.Function], out: List[fenics.Function]
    ) -> None:
        """Computes the search direction for the LBFGS method.

        Args:
            q: The rhs for computing the search direction
            out: The output list of functions, in which the search direction is stored.

        """
        if self.memory_size > 0 and len(self.history_s) > 0:
            self.history_alpha.clear()
            out[0].vector()[:] = q[0].vector()[:]

            for i, _ in enumerate(self.history_s):
                alpha = self.history_rho[i] * self._scalar_product(
                    self.history_s[i], out
                )
                self.history_alpha.append(alpha)
                out[0].vector()[:] -= alpha * self.history_y[i][0].vector()[:]

            bfgs_factor = self._scalar_product(
                self.history_y[0], self.history_s[0]
            ) / self._scalar_product(self.history_y[0], self.history_y[0])
            out[0].vector()[:] *= bfgs_factor

            for i, _ in enumerate(self.history_s):
                beta = self.history_rho[-1 - i] * self._scalar_product(
                    self.history_y[-1 - i], out
                )
                out[0].vector()[:] += self.history_s[-1 - i][0].vector()[:] * (
                    self.history_alpha[-1 - i] - beta
                )

        else:
            out[0].vector()[:] = q[0].vector()[:]

    def _compute_ncg_direction(
        self, q: List[fenics.Function], out: List[fenics.Function]
    ) -> None:
        """Computes the search direction for the NCG methods.

        Args:
            q: The rhs for computing the search direction
            out: The output list of functions, in which the search direction is stored.

        """
        if self.iteration > 0:
            self.difference[0].vector()[:] = (
                q[0].vector()[:] - self.dir_prev[0].vector()[:]
            )
            if self.cg_type == "FR":
                beta_num = self._scalar_product(q, q)
                beta_denom = self._scalar_product(self.dir_prev, self.dir_prev)
                self.beta = beta_num / beta_denom
            elif self.cg_type == "PR":
                beta_num = self._scalar_product(q, self.difference)
                beta_denom = self._scalar_product(self.dir_prev, self.dir_prev)
                self.beta = beta_num / beta_denom
            elif self.cg_type == "HS":
                beta_num = self._scalar_product(q, self.difference)
                beta_denom = -self._scalar_product(out, self.difference)
                self.beta = beta_num / beta_denom
            elif self.cg_type == "DY":
                beta_num = self._scalar_product(q, q)
                beta_denom = -self._scalar_product(out, self.difference)
                self.beta = beta_num / beta_denom
            elif self.cg_type == "HZ":
                dy = -self._scalar_product(out, self.difference)
                y2 = self._scalar_product(self.difference, self.difference)

                self.difference[0].vector()[:] = (
                    -self.difference[0].vector()[:] - 2 * y2 / dy * out[0].vector()[:]
                )
                self.beta = -self._scalar_product(self.difference, q) / dy
        else:
            self.beta = 0.0

        out[0].vector()[:] = q[0].vector()[:] + self.beta * out[0].vector()[:]

    def _compute_eps(self) -> float:
        """Computes and returns the termination parameter epsilon."""
        self.diff[0].vector()[:] = (
            self.p_current[0].vector()[:] - self.z_star[0].vector()[:]
        )
        eps = np.sqrt(self._scalar_product(self.diff, self.diff)) / self.norm_z_star

        return eps
