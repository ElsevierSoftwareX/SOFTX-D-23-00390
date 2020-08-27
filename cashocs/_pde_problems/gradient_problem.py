# Copyright (C) 2020 Sebastian Blauth
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

"""
Created on 24/02/2020, 09.26

@author: blauths
"""

import fenics

from ..utils import _solve_linear_problem



class GradientProblem:
	"""A class representing the Riesz problem to determine the gradient.

	"""
	
	def __init__(self, form_handler, state_problem, adjoint_problem):
		"""Initializes the gradient problem.
		
		Parameters
		----------
		form_handler : cashocs._forms.ControlFormHandler
			The FormHandler object of the optimization problem.
		state_problem : cashocs._pde_problems.StateProblem
			The StateProblem object used to solve the state equations.
		adjoint_problem : cashocs._pde_problems.AdjointProblem
			The AdjointProblem used to solve the adjoint equations.
		"""
		
		self.form_handler = form_handler
		self.state_problem = state_problem
		self.adjoint_problem = adjoint_problem
		
		self.gradients = [fenics.Function(V) for V in self.form_handler.control_spaces]
		self.config = self.form_handler.config

		self.has_solution = False


	
	def solve(self):
		"""Solves the Riesz projection problem to obtain the gradient of the (reduced) cost functional.
		
		Returns
		-------
		gradients : list[dolfin.function.function.Function]
			The list of gradient of the cost functional.
		"""
		
		self.state_problem.solve()
		self.adjoint_problem.solve()
		
		if not self.has_solution:
			for i in range(self.form_handler.control_dim):
				b = fenics.as_backend_type(fenics.assemble(self.form_handler.gradient_forms_rhs[i])).vec()
				_solve_linear_problem(ksp=self.form_handler.ksps[i], b=b, x=self.gradients[i].vector().vec())

			self.has_solution = True

			self.gradient_norm_squared = self.form_handler.scalar_product(self.gradients, self.gradients)

		return self.gradients
