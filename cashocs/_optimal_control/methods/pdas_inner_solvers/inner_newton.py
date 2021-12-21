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

"""Truncated Newton method for PDAS.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

import fenics
import numpy as np

from .unconstrained_line_search import UnconstrainedLineSearch
from ...control_optimization_algorithm import ControlOptimizationAlgorithm
from ...._exceptions import NotConvergedError


if TYPE_CHECKING:
    from ...optimal_control_problem import OptimalControlProblem


class InnerNewton(ControlOptimizationAlgorithm):
    """Unconstrained truncated Newton method"""

    def __init__(self, optimization_problem: OptimalControlProblem) -> None:
        """
        Parameters
        ----------
        optimization_problem : OptimalControlProblem
            the corresponding optimization problem to be solved
        """

        super().__init__(optimization_problem)

        self.line_search = UnconstrainedLineSearch(self)
        self.maximum_iterations = self.config.getint(
            "AlgoPDAS", "maximum_iterations_inner_pdas", fallback=50
        )
        self.tolerance = self.config.getfloat(
            "AlgoPDAS", "pdas_inner_tolerance", fallback=1e-2
        )
        self.reduced_gradient = [
            fenics.Function(optimization_problem.control_spaces[j])
            for j in range(len(self.controls))
        ]
        self.first_iteration = True
        self.first_gradient_norm = 1.0

        self.unconstrained_hessian = optimization_problem.unconstrained_hessian

        self.stepsize = 1.0
        self.armijo_stepsize_initial = self.stepsize

        self.armijo_broken = False

        self.pdas_solver = True

    def run(self, idx_active: List[np.ndarray]) -> None:
        """Solves the inner PDAS optimization problem

        Parameters
        ----------
        idx_active : list[numpy.ndarray]
            list of indicies corresponding to the active set

        Returns
        -------
        None
        """

        self.iteration = 0
        self.relative_norm = 1.0
        self.state_problem.has_solution = False

        while True:
            self.adjoint_problem.has_solution = False
            self.gradient_problem.has_solution = False
            self.gradient_problem.solve()

            for j in range(len(self.controls)):
                self.reduced_gradient[j].vector().vec().aypx(
                    0.0, self.gradient[j].vector().vec()
                )
                self.reduced_gradient[j].vector()[idx_active[j]] = 0.0

            self.gradient_norm = np.sqrt(
                self.form_handler.scalar_product(
                    self.reduced_gradient, self.reduced_gradient
                )
            )

            if self.iteration == 0:
                self.gradient_norm_initial = self.gradient_norm
                if self.first_iteration:
                    self.first_gradient_norm = self.gradient_norm_initial
                    self.first_iteration = False

            self.relative_norm = self.gradient_norm / self.gradient_norm_initial
            if (
                self.gradient_norm <= self.tolerance * self.gradient_norm_initial
                or self.relative_norm
                * self.gradient_norm_initial
                / self.first_gradient_norm
                <= self.tolerance / 2
            ):
                break

            self.search_direction = self.unconstrained_hessian.newton_solve(idx_active)
            self.directional_derivative = self.form_handler.scalar_product(
                self.search_direction, self.reduced_gradient
            )
            if self.directional_derivative > 0:
                # print('No descent direction')
                for i in range(len(self.controls)):
                    self.search_direction[i].vector().vec().aypx(
                        0.0, -self.reduced_gradient[i].vector().vec()
                    )

            self.objective_value = self.cost_functional.evaluate()
            self.output()

            self.line_search.search(self.search_direction)
            if self.armijo_broken:
                if self.soft_exit:
                    print("Armijo rule failed.")
                    break
                else:
                    raise NotConvergedError("Armijo line search")

            self.iteration += 1

            if self.iteration >= self.maximum_iterations:
                if self.soft_exit:
                    print("Maximum number of iterations exceeded.")
                    break
                else:
                    raise NotConvergedError(
                        "Newton method for the primal dual active set method",
                        "Maximum number of iterations were exceeded.",
                    )
