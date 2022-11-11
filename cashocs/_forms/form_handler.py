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

"""Management for weak forms."""

from __future__ import annotations

import abc
from typing import Callable, List, TYPE_CHECKING, Union

import fenics

from cashocs import _utils
from cashocs._database import database

if TYPE_CHECKING:
    from cashocs import _typing
    from cashocs import io
    from cashocs._optimization import cost_functional as cf


def _get_subdx(
    function_space: fenics.FunctionSpace, index: int, ls: List
) -> Union[None, List[int]]:
    """Computes the sub-indices for mixed function spaces based on the id of a subspace.

    Args:
        function_space: The function space, whose substructure is to be investigated.
        index: The id of the target function space.
        ls: A list of indices for the sub-spaces.

    Returns:
        The list of the sub-indices.

    """
    if function_space.id() == index:
        return ls
    if function_space.num_sub_spaces() > 1:
        for i in range(function_space.num_sub_spaces()):
            ans = _get_subdx(function_space.sub(i), index, ls + [i])
            if ans is not None:
                return ans

    return None


def _hook() -> None:
    return None


class FormHandler(abc.ABC):
    """Parent class for UFL form manipulation.

    This is subclassed by specific form handlers for either
    optimal control or shape optimization. The base class is
    used to determine common objects and to derive the UFL forms
    for the state and adjoint systems.
    """

    def __init__(
        self, optimization_problem: _typing.OptimizationProblem, db: database.Database
    ) -> None:
        """Initializes self.

        Args:
            optimization_problem: The corresponding optimization problem.
            db: The database for the problem.

        """
        self.optimization_problem = optimization_problem
        self.db = db

        self.config: io.Config = self.db.config
        self.control_dim: int = 1
        self.cost_functional_shift: float = 0.0
        self.lagrangian: cf.Lagrangian = self.db.form_db.lagrangian

        self.dx: fenics.Measure = self.db.geometry_db.dx

        self.opt_algo: str = _utils.optimization_algorithm_configuration(self.config)

        self.gradient: List[fenics.Function] = []
        self.control_spaces: List[fenics.FunctionSpace] = []

        self.pre_hook: Callable[..., None] = _hook
        self.post_hook: Callable[..., None] = _hook

    @abc.abstractmethod
    def scalar_product(
        self, a: List[fenics.Function], b: List[fenics.Function]
    ) -> float:
        """Computes the scalar product between a and b.

        Args:
            a: The first argument.
            b: The second argument.

        Returns:
            The scalar product of a and b.

        """
        pass

    def restrict_to_inactive_set(
        self, a: List[fenics.Function], b: List[fenics.Function]
    ) -> List[fenics.Function]:
        """Restricts a function to the inactive set.

        Note, that nothing will happen if the type of the optimization problem does not
        support box constraints.

        Args:
            a: The function, which shall be restricted to the inactive set
            b: The output function, which will contain the result and is overridden.

        Returns:
            The result of the restriction (overrides input b)

        """
        for j in range(len(self.gradient)):
            if not b[j].vector().vec().equal(a[j].vector().vec()):
                b[j].vector().vec().aypx(0.0, a[j].vector().vec())
                b[j].vector().apply("")

        return b

    # pylint: disable=unused-argument
    def restrict_to_active_set(
        self, a: List[fenics.Function], b: List[fenics.Function]
    ) -> List[fenics.Function]:
        """Restricts a function to the active set.

        Note, that nothing will happen if the type of the optimization problem does not
        support box constraints.

        Args:
            a: The function, which shall be restricted to the active set
            b: The output function, which will contain the result and is overridden.

        Returns:
            The result of the restriction (overrides input b)

        """
        for j in range(len(self.gradient)):
            b[j].vector().vec().set(0.0)
            b[j].vector().apply("")

        return b

    def compute_active_sets(self) -> None:
        """Computes the active set for problems with box constraints."""
        pass

    def update_scalar_product(self) -> None:
        """Updates the scalar product."""
        pass

    def project_to_admissible_set(
        self, a: List[fenics.Function]
    ) -> List[fenics.Function]:
        """Projects a function ``a`` onto the admissible set."""
        pass
