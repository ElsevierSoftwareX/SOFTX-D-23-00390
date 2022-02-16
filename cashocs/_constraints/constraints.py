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

"""Module for equality and inequality constraints."""

from __future__ import annotations

import abc
from typing import Union, Optional, Dict

import fenics
import numpy as np
import ufl
import ufl.core.expr

from cashocs import _exceptions
from cashocs import utils


class Constraint(abc.ABC):
    """Base class for additional equality and inequality constraints."""

    linear_term: Union[ufl.Form, ufl.core.expr.Expr]
    quadratic_term: Union[ufl.Form, Dict]

    def __init__(
        self,
        variable_function: Union[ufl.Form, ufl.core.expr.Expr],
        measure: Optional[fenics.Measure] = None,
    ) -> None:
        """Initializes self.

        Args:
            variable_function: Either a UFL Form (when we have a scalar / integral
                constraint) or an ufl expression (when we have a pointwise constraint),
                which models the part that is to be constrained.
            measure: A measure indicating where a pointwise constraint should be
                satisfied.
        """
        self.variable_function = variable_function
        self.measure = measure

        self.is_integral_constraint = False
        self.is_pointwise_constraint = False

        if self.measure is None:
            self.is_integral_constraint = True
        else:
            self.is_pointwise_constraint = True

    @abc.abstractmethod
    def constraint_violation(self) -> float:
        """Computes the constraint violation for the problem.

        Returns:
            The computed violation
        """
        pass


class EqualityConstraint(Constraint):
    """Models an (additional) equality constraint."""

    def __init__(
        self,
        variable_function: Union[ufl.Form, ufl.core.expr.Expr],
        target: float,
        measure: Optional[fenics.Measure] = None,
    ) -> None:
        """Initializes self.

        Args:
            variable_function: Either a UFL Form (when we have a scalar / integral
                constraint) or an ufl expression (when we have a pointwise constraint),
                which models the part that is to be constrained.
            target: The target (rhs) of the equality constraint.
            measure: A measure indicating where a pointwise constraint should be
                satisfied.
        """
        super().__init__(variable_function, measure=measure)
        self.target = target

        if self.is_integral_constraint:
            self.linear_term = variable_function
            self.quadratic_term = {
                "integrand": variable_function,
                "tracking_goal": target,
                "weight": 1.0,
            }

        elif self.is_pointwise_constraint:
            mesh = measure.ufl_domain().ufl_cargo()
            multiplier_space = fenics.FunctionSpace(mesh, "CG", 1)
            self.multiplier = fenics.Function(multiplier_space)
            self.linear_term = self.multiplier * variable_function * measure
            self.quadratic_term = (
                fenics.Constant(0.5) * pow(variable_function - target, 2) * measure
            )

    def constraint_violation(self) -> float:
        """Computes the constraint violation for the problem.

        Returns:
            The computed violation
        """
        if self.is_integral_constraint:
            return np.abs(fenics.assemble(self.variable_function) - self.target)
        elif self.is_pointwise_constraint:
            return np.sqrt(
                fenics.assemble(
                    pow(self.variable_function - self.target, 2) * self.measure
                )
            )
        return float("inf")


class InequalityConstraint(Constraint):
    """Models an (additional) inequality constraint."""

    def __init__(
        self,
        variable_function: Union[ufl.Form, ufl.core.expr.Expr],
        lower_bound: Optional[Union[float, fenics.Function]] = None,
        upper_bound: Optional[Union[float, fenics.Function]] = None,
        measure: Optional[fenics.Measure] = None,
    ) -> None:
        """Initializes self.

        Args:
            variable_function: Either a UFL Form (when we have a scalar / integral
                constraint) or an ufl expression (when we have a pointwise constraint),
                which models the part that is to be constrained
            lower_bound: The lower bound for the inequality constraint
            upper_bound: The upper bound for the inequality constraint
            measure: A measure indicating where a pointwise constraint should be
                satisfied.
        """
        super().__init__(variable_function, measure=measure)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        if self.lower_bound is None and self.upper_bound is None:
            raise _exceptions.InputError(
                "cashocs._constraints.constraints.InequalityConstraint",
                "lower_bound and upper_bound",
                "You have to specify at least one bound for the inequality constraint.",
            )

        if self.is_integral_constraint:
            self.min_max_term = {
                "integrand": variable_function,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "mu": 1.0,
                "lambda": 1.0,
            }

        elif self.is_pointwise_constraint:
            mesh = measure.ufl_domain().ufl_cargo()
            multiplier_space = fenics.FunctionSpace(mesh, "CG", 1)
            self.multiplier = fenics.Function(multiplier_space)
            weight_space = fenics.FunctionSpace(mesh, "R", 0)
            self.weight = fenics.Function(weight_space)

            self.cost_functional_terms = []
            if self.upper_bound is not None:
                self.cost_functional_terms.append(
                    fenics.Constant(1 / 2)
                    / self.weight
                    * pow(
                        utils._max(
                            fenics.Constant(0.0),
                            self.multiplier
                            + self.weight * (self.variable_function - self.upper_bound),
                        ),
                        2,
                    )
                    * self.measure
                )

            if self.lower_bound is not None:
                self.cost_functional_terms.append(
                    fenics.Constant(1 / 2)
                    / self.weight
                    * pow(
                        utils._min(
                            fenics.Constant(0.0),
                            self.multiplier
                            + self.weight * (self.variable_function - self.lower_bound),
                        ),
                        2,
                    )
                    * self.measure
                )

    def constraint_violation(self) -> float:
        """Computes the constraint violation for the problem.

        Returns:
            The computed violation
        """
        violation = 0.0
        if self.is_integral_constraint:
            min_max_integral = fenics.assemble(self.min_max_term["integrand"])

            if self.upper_bound is not None:
                violation += pow(
                    np.maximum(min_max_integral - self.upper_bound, 0.0), 2
                )

            if self.lower_bound is not None:
                violation += pow(
                    np.minimum(min_max_integral - self.lower_bound, 0.0), 2
                )

        elif self.is_pointwise_constraint:

            if self.upper_bound is not None:
                violation += fenics.assemble(
                    pow(
                        utils._max(
                            self.variable_function - self.upper_bound,
                            fenics.Constant(0.0),
                        ),
                        2,
                    )
                    * self.measure
                )

            if self.lower_bound is not None:
                violation += fenics.assemble(
                    pow(
                        utils._min(
                            self.variable_function - self.lower_bound,
                            fenics.Constant(0.0),
                        ),
                        2,
                    )
                    * self.measure
                )

        return np.sqrt(violation)
