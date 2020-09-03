URLS=[
"index.html",
"optimization_problem.html",
"geometry.html",
"utils.html",
"nonlinear_solvers.html",
"verification.html"
];
INDEX=[
{
"ref":"cashocs",
"url":0,
"doc":"cashocs is a Computational Adjoint based SHape optimization and Optimal Control Software for python. cashocs can be used to treat optimal control and shape optimization problems constrained by PDEs. It derives the necessary adjoint equations automatically and implements various solvers for the problems. cashocs is based on the finite element package FEniCS and allows the user to define the optimization problems in the high-level unified form language (UFL). Installation       - First, install [FEniCS](https: fenicsproject.org/download/), version 2019.1. Note, that FEniCS should be compiled with PETSc and petsc4py. - Then, install [meshio](https: github.com/nschloe/meshio) with a [h5py](https: www.h5py.org) version that matches the hdf5 version used in FEniCS, and [matplotlib](https: matplotlib.org/) Note, that if you want to have a [conda](https: docs.conda.io/en/latest/index.html) installation, you can simply create a new environment with conda create -n NAME -c conda-forge fenics=2019 meshio matplotlib which automatically installs all prerequisites to get started. - You might also want to install [GMSH](https: gmsh.info/). CASHOCS does not necessarily need this to function properly, but it is required for the remeshing functionality. - Clone this repository with git, and run pip3 install . - Alternatively, you can install CASHOCS via the PYPI pip3 install cashocs You can install the newest (development) version of cashocs with pip3 install git+temp_url Getting started        - Since cashocs is based on FEniCS, most of the user input consists of definining the objects (such as the state system and cost functional) via UFL forms. If one has a functioning code for the forward problem and the evaluation of the cost functional, the necessary modifications to optimize the problem in cashocs are minimal. Consider, e.g., the following optimization problem  \\min J(y, u) = \\frac{1}{2} \\int_{\\Omega} \\lvert y - y_d \\rvert^2 \\text{d}x + \\frac{\\alpha}{2} \\int_\\Omega u^2 \\text{d}x  \\text{ subject to } \\begin{aligned} - \\Delta y &= u \\quad \\text{ in } \\Omega,  y &= 0 \\quad \\text{ on } \\Gamma. \\end{aligned}  Note, that the entire problem is treated in detail in demo_01.py in the demos folder. For our purposes, we assume that a mesh for this problem is defined and that a suitable function space is chosen. This can, e.g., be achieved via from fenics import  import cashocs config = cashocs.create_config('path_to_config') mesh, subdomains, boundaries, dx, ds, dS = cashocs.regular_mesh(25) V = FunctionSpace(mesh, 'CG', 1) The config object which is created from a .ini file is used to determine the parameters for the optimization algorithms. To define the state problem, we then define a state variable y, an adjoint variable p and a control variable u, and write the PDE as a weak form y = Function(V) p = Function(V) u = Function(V) e = inner(grad(y), grad(p - u p dx bcs = cashocs.create_bcs_list(V, Constant(0), boundaries, [1,2,3,4]) Finally, we have to define the cost functional and the optimization problem y_d = Expression('sin(2 pi  x[0]  sin(2 pi x[1] ', degree=1) alpha = 1e-6 J = 1/2 (y - y_d)  (y - y_d)  dx + alpha/2 u u dx opt_problem = cashocs.OptimalControlProblem(e, bcs, J, y, u, p, config) opt_problem.solve() The only major difference between cashocs and fenics code is that one has to use Function objects for states and adjoints, and that Trial- and TestFunctions are not needed to define the state equation. Other than that, the syntax would also be valid with fenics. For a detailed discussion of the features of cashocs and its usage we refer to the [demos]( demos). Demos   - The documentation of the demos can be found  here . Note, that cashocs was also used to obtain the numerical results for my preprints [Blauth, Leith\u00e4user, and Pinnau, Optimal Control of the Sabatier Process in Microchannel Reactors](url) and [Blauth, Nonlinear Conjugate Gradient Methods for PDE Constrained Shape Optimization based on Steklov-Poincare Type Metrics](url) Command line interface for mesh conversion                      cashocs includes a command line interface for converting gmsh mesh files to xdmf ones, which can be read very easily into fenics. The corresponding command for the conversion (after having generated a mesh file 'in.msh' with gmsh) is given by cashocs-convert in.msh out.xdmf This also create .xdmf files for subdomains and boundaries in case they are tagged in gmsh as Physical quantities. License    - CASHOCS is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. CASHOCS is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with CASHOCS. If not, see  . Contact / About        - I'm Sebastian Blauth, a PhD student at Fraunhofer ITWM and TU Kaiserslautern, and I developed this project as part of my work. If you have any questions / suggestions / feedback, etc., you can contact me via [sebastian.blauth@itwm.fraunhofer.de](mailto:sebastian.blauth@itwm.fraunhofer.de). Copyright (C) 2020 Sebastian Blauth"
},
{
"ref":"cashocs.import_mesh",
"url":0,
"doc":"Imports a mesh file for use with cashocs / fenics. This function imports a mesh file that was generated by GMSH and converted to .xdmf with the command line function cashocs-convert (see cashocs main documentation). The syntax for the conversion is cashocs-convert in.msh out.xdmf If there are Physical quantities specified in the gmsh file, these are imported to the subdomains and boundaries output of this function and can also be directly accessed via the measures, e.g., with dx(1), ds(1), etc. Parameters      arg : str or configparser.ConfigParser This is either a string, in which case it corresponds to the location of the mesh file in .xdmf file format, or a config file that has this path stored in its settings. Returns    - mesh : dolfin.cpp.mesh.Mesh The imported (computational) mesh. subdomains : dolfin.cpp.mesh.MeshFunctionSizet A MeshFunction object containing the subdomains, i.e., the Physical regions marked in the gmsh file. boundaries : dolfin.cpp.mesh.MeshFunctionSizet A MeshFunction object containing the boundaries, i.e., the Physical regions marked in the gmsh file. Can, e.g., be used to set up boundary conditions. dx : ufl.measure.Measure The volume measure of the mesh corresponding to the subdomains (i.e. gmsh Physical region indices). ds : ufl.measure.Measure The surface measure of the mesh corresponding to the boundaries (i.e. gmsh Physical region indices). dS : ufl.measure.Measure The interior facet measure of the mesh corresponding to boundaries (i.e. gmsh Physical region indices).",
"func":1
},
{
"ref":"cashocs.regular_mesh",
"url":0,
"doc":"Creates a mesh corresponding to a rectangle or cube. This function creates a uniform mesh of either a rectangle or a cube, starting at the origin and having length specified in lx, lx, lz. The resulting mesh uses n elements along the shortest direction and accordingly many along the longer ones. The resulting domain is  [0, L_x] \\times [0, L_y] \\phantom{ \\times [0, L_z] a} \\quad \\text{ in } 2D,  [0, L_x] \\times [0, L_y] \\times [0, L_z] \\quad \\text{ in } 3D.  The boundary markers are ordered as follows: - 1 corresponds to \\(\\{x=0\\}\\). - 2 corresponds to \\(\\{x=L_x\\}\\). - 3 corresponds to \\(\\{y=0\\}\\). - 4 corresponds to \\(\\{y=L_y\\}\\). - 5 corresponds to \\(\\{z=0\\}\\) (only in 3D). - 6 corresponds to \\(\\{z=L_z\\}\\) (only in 3D). Parameters      n : int Number of elements in the shortest coordinate direction. L_x : float Length in x-direction. L_y : float Length in y-direction. L_z : float or None, optional Length in z-direction, if this is None, then the geometry will be two-dimensional (default is None). Returns    - mesh : dolfin.cpp.mesh.Mesh The computational mesh. subdomains : dolfin.cpp.mesh.MeshFunctionSizet A MeshFunction object containing the subdomains. boundaries : dolfin.cpp.mesh.MeshFunctionSizet A MeshFunction object containing the boundaries. dx : ufl.measure.Measure The volume measure of the mesh corresponding to subdomains. ds : ufl.measure.Measure The surface measure of the mesh corresponding to boundaries. dS : ufl.measure.Measure The interior facet measure of the mesh corresponding to boundaries.",
"func":1
},
{
"ref":"cashocs.regular_box_mesh",
"url":0,
"doc":"Creates a mesh corresponding to a rectangle or cube. This function creates a uniform mesh of either a rectangle or a cube, with specified start (S_) and end points (E_). The resulting mesh uses n elements along the shortest direction and accordingly many along the longer ones. The resulting domain is  [S_x, E_x] \\times [S_y, E_y] \\phantom{ \\times [S_z, E_z] a} \\quad \\text{ in } 2D,  [S_x, E_x] \\times [S_y, E_y] \\times [S_z, E_z] \\quad \\text{ in } 3D.  The boundary markers are ordered as follows: - 1 corresponds to \\(\\{x=S_x\\}\\). - 2 corresponds to \\(\\{x=E_x\\}\\). - 3 corresponds to \\(\\{y=S_y\\}\\). - 4 corresponds to \\(\\{y=E_y\\}\\). - 5 corresponds to \\(\\{z=S_z\\}\\) (only in 3D). - 6 corresponds to \\(\\{z=E_z\\}\\) (only in 3D). Parameters      n : int Number of elements in the shortest coordinate direction. S_x : float Start of the x-interval. S_y : float Start of the y-interval. S_z : float or None, optional Start of the z-interval, mesh is 2D if this is None (default is None). E_x : float End of the x-interval. E_y : float End of the y-interval. E_z : float or None, optional End of the z-interval, mesh is 2D if this is None (default is None). Returns    - mesh : dolfin.cpp.mesh.Mesh the computational mesh subdomains : dolfin.cpp.mesh.MeshFunctionSizet a MeshFunction object containing the subdomains boundaries : dolfin.cpp.mesh.MeshFunctionSizet a MeshFunction object containing the boundaries dx : ufl.measure.Measure the volume measure of the mesh corresponding to subdomains ds : ufl.measure.Measure the surface measure of the mesh corresponding to boundaries dS : ufl.measure.Measure the interior facet measure of the mesh corresponding to boundaries",
"func":1
},
{
"ref":"cashocs.damped_newton_solve",
"url":0,
"doc":"A damped Newton method for solving nonlinear equations. The Newton method is based on the natural monotonicity test from Deuflhard [1]. It also allows fine tuning via a direct interface, and absolute, relative, and combined stopping criteria. Can also be used to specify the solver for the inner (linear) subproblems via petsc ksps. The method terminates after  max_iter iterations, or if a termination criterion is satisfied. These criteria are given by  \\lvert\\lvert F_{k} \\rvert\\rvert \\leq \\texttt{rtol} \\lvert\\lvert F_0 \\rvert\\rvert \\quad \\text{ if convergence_type is 'rel'}  \\lvert\\lvert F_{k} \\rvert\\rvert \\leq \\texttt{atol} \\quad \\text{ if convergence_type is 'abs'}  \\lvert\\lvert F_{k} \\rvert\\rvert \\leq \\texttt{atol} + \\text{rtol} \\lvert\\lvert F_0 \\rvert\\rvert \\quad \\text{ if convergence_type is 'combined'}  The norm chosen for the termination criterion is specified via  norm_type . Parameters      F : ufl.form.Form The variational form of the nonlinear problem to be solved by Newton's method. u : dolfin.function.function.Function The sought solution / initial guess. It is not assumed that the initial guess satisfies the Dirichlet boundary conditions, they are applied automatically. The method overwrites / updates this Function. bcs : list[dolfin.fem.dirichletbc.DirichletBC] A list of DirichletBCs for the nonlinear variational problem. rtol : float, optional Relative tolerance of the solver if convergence_type is either 'combined' or 'rel' (default is  rtol = 1e-10). atol : float, optional Absolute tolerance of the solver if convergence_type is either 'combined' or 'abs' (default is atol = 1e-10). max_iter : int, optional Maximum number of iterations carried out by the method (default is max_iter = 50). convergence_type : {'combined', 'rel', 'abs'} Determines the type of stopping criterion that is used. norm_type : {'l2', 'linf'} Determines which norm is used in the stopping criterion. damped : bool, optional If true, then a damping strategy is used. If false, the classical Newton-Raphson iteration (without damping) is used (default is True). verbose : bool, optional If true, prints status of the iteration to the console (default is true). ksp : petsc4py.PETSc.KSP, optional The PETSc ksp object used to solve the inner (linear) problem if this is None it uses the direct solver MUMPS (default is None). Returns    - dolfin.function.function.Function The solution of the nonlinear variational problem, if converged. This overrides the input function u. References      [1] P. Deuflhard, \"Newton methods for nonlinear problems\", Springer, Heidelberg, 2011, https: doi.org/10.1007/978-3-642-23899-4 Examples     This example solves the problem  - \\Delta u + u^3 = 1 \\quad \\text{ in } \\Omega=(0,1)^2  u = 0 \\quad \\text{ on } \\Gamma.  from fenics import  import cashocs mesh, _, boundaries, dx, _, _ = cashocs.regular_mesh(25) V = FunctionSpace(mesh, 'CG', 1) u = Function(V) v = TestFunction(V) F = inner(grad(u), grad(v  dx + pow(u,3) v dx - Constant(1) v dx bcs = cashocs.create_bcs_list(V, Constant(0.0), boundaries, [1,2,3,4]) cashocs.damped_newton_solve(F, u, bcs)",
"func":1
},
{
"ref":"cashocs.OptimalControlProblem",
"url":0,
"doc":"Implements an optimal control problem. This class is used to define an optimal control problem, and also to solve it subsequently. For a detailed documentation, see the examples in the \"demos\" folder. For easier input, when consider single (state or control) variables, these do not have to be wrapped into a list. Note, that in the case of multiple variables these have to be grouped into ordered lists, where state_forms, bcs_list, states, adjoints have to have the same order (i.e. [state1, state2, state3, .] and [adjoint1, adjoint2, adjoint3,  .], where adjoint1 is the adjoint of state1 and so on. Initializes the optimal control problem. This is used to generate all classes and functionalities. First ensures consistent input as the __init__ function is overloaded. Afterwards, the solution algorithm is initialized. Parameters      state_forms : ufl.form.Form or list[ufl.form.Form] the weak form of the state equation (user implemented). Can be either a single UFL form, or a (ordered) list of UFL forms bcs_list : list[dolfin.fem.dirichletbc.DirichletBC] or list[list[dolfin.fem.dirichletbc.DirichletBC or dolfin.fem.dirichletbc.DirichletBC or None the list of DirichletBC objects describing Dirichlet (essential) boundary conditions. If this is None, then no Dirichlet boundary conditions are imposed. cost_functional_form : ufl.form.Form UFL form of the cost functional states : dolfin.function.function.Function or list[dolfin.function.function.Function] the state variable(s), can either be a single fenics Function, or a (ordered) list of these controls : dolfin.function.function.Function or list[dolfin.function.function.Function] the control variable(s), can either be a single fenics Function, or a list of these adjoints : dolfin.function.function.Function or list[dolfin.function.function.Function] the adjoint variable(s), can either be a single fenics Function, or a (ordered) list of these config : configparser.ConfigParser the config file for the problem, generated via cashocs.create_config(path_to_config) riesz_scalar_products : None or ufl.form.Form or list[ufl.form.Form], optional the scalar products of the control space. Can either be None, a single UFL form, or a (ordered) list of UFL forms. If None, the \\(L^2(\\Omega)\\) product is used. (default is None) control_constraints : None or list[dolfin.function.function.Function] or list[float] or list[list[dolfin.function.function.Function or list[list[float , optional Box constraints posed on the control, None means that there are none (default is None). The (inner) lists should contain two elements of the form [u_a, u_b], where u_a is the lower, and u_b the upper bound. initial_guess : list[dolfin.function.function.Function], optional list of functions that act as initial guess for the state variables, should be valid input for fenics.assign. (defaults to None (which means a zero initial guess ksp_options : list[list[str or list[list[list[str ] or None, optional A list of strings corresponding to command line options for PETSc, used to solve the state systems. If this is None, then the direct solver mumps is used (default is None). adjoint_ksp_options : list[list[str or list[list[list[str ] or None A list of strings corresponding to command line options for PETSc, used to solve the adjoint systems. If this is None, then the same options as for the state systems are used (default is None). Examples     The corresponding examples detailing the use of this class can be found in the \"demos\" folder."
},
{
"ref":"cashocs.OptimalControlProblem.solve",
"url":0,
"doc":"Solves the optimization problem by the method specified in the config file. Updates / overwrites states, controls, and adjoints according to the optimization method, i.e., the user-input functions. Parameters      algorithm : str or None, optional Selects the optimization algorithm. Valid choices are 'gradient_descent' ('gd'), 'conjugate_gradient' ('cg'), 'lbfgs' ('bfgs'), 'newton', or 'pdas'. This overwrites the value specified in the config file. If this is None, then the value in the config file is used. Default is None. rtol : float or None, optional The relative tolerance used for the termination criterion. Overwrites the value specified in the config file. If this is None, the value from the config file is taken. Default is None. atol : float or None, optional The absolute tolerance used for the termination criterion. Overwrites the value specified in the config file. If this is None, the value from the config file is taken. Default is None. max_iter : int or None, optional The maximum number of iterations the optimization algorithm can carry out before it is terminated. Overwrites the value specified in the config file. If this is None, the value from the config file is taken. Default is None. Returns    - None Notes   - If either  rtol or  atol are specified as arguments to the solve call, the termination criterion changes to: - a purely relative one (if only  rtol is specified), i.e.,   \\nabla J(u_k)  \\leq \\texttt{rtol}  \\nabla J(u_0)  .  - a purely absolute one (if only  atol is specified), i.e.,   \\nabla J(u_K)  \\leq \\texttt{atol}.  - a combined one if both  rtol and  atol are specified, i.e.,   \\nabla J(u_k)  \\leq \\texttt{atol} + \\texttt{rtol}  \\nabla J(u_0)   ",
"func":1
},
{
"ref":"cashocs.OptimalControlProblem.compute_gradient",
"url":0,
"doc":"Solves the Riesz problem to determine the gradient(s) This can be used for debugging, or code validation. The necessary solutions of the state and adjoint systems are carried out automatically. Returns    - list[dolfin.function.function.Function] a list consisting of the (components) of the gradient",
"func":1
},
{
"ref":"cashocs.OptimalControlProblem.compute_state_variables",
"url":1,
"doc":"Solves the state system. This can be used for debugging purposes, to validate the solver and general behavior. Updates and overwrites the user input for the state variables. Returns    - None",
"func":1
},
{
"ref":"cashocs.OptimalControlProblem.compute_adjoint_variables",
"url":1,
"doc":"Solves the adjoint system. This can be used for debugging purposes and solver validation. Updates / overwrites the user input for the adjoint variables. The solve of the corresponding state system needed to determine the adjoints is carried out automatically. Returns    - None",
"func":1
},
{
"ref":"cashocs.ShapeOptimizationProblem",
"url":0,
"doc":"A shape optimization problem This class is used to define a shape optimization problem, and also to solve it subsequently. For a detailed documentation, see the examples in the \"demos\" folder. For easier input, when consider single (state or control) variables, these do not have to be wrapped into a list. Note, that in the case of multiple variables these have to be grouped into ordered lists, where state_forms, bcs_list, states, adjoints have to have the same order (i.e. [state1, state2, state3, .] and [adjoint1, adjoint2, adjoint3,  .], where adjoint1 is the adjoint of state1 and so on. Initializes the shape optimization problem This is used to generate all classes and functionalities. First ensures consistent input as the __init__ function is overloaded. Afterwards, the solution algorithm is initialized. Parameters      state_forms : ufl.form.Form or list[ufl.form.Form] the weak form of the state equation (user implemented). Can be either bcs_list : list[dolfin.fem.dirichletbc.DirichletBC] or list[list[dolfin.fem.dirichletbc.DirichletBC or dolfin.fem.dirichletbc.DirichletBC or None the list of DirichletBC objects describing Dirichlet (essential) boundary conditions. If this is None, then no Dirichlet boundary conditions are imposed. cost_functional_form : ufl.form.Form UFL form of the cost functional states : dolfin.function.function.Function or list[dolfin.function.function.Function] the state variable(s), can either be a single fenics Function, or a (ordered) list of these adjoints : dolfin.function.function.Function or list[dolfin.function.function.Function] the adjoint variable(s), can either be a single fenics Function, or a (ordered) list of these boundaries : dolfin.cpp.mesh.MeshFunctionSizet MeshFunction that indicates the boundary markers config : configparser.ConfigParser the config file for the problem, generated via cashocs.create_config(path_to_config) initial_guess : list[dolfin.function.function.Function], optional A list of functions that act as initial guess for the state variables, should be valid input for fenics.assign. (defaults to None (which means a zero initial guess ksp_options : list[list[str or list[list[list[str ] or None, optional A list of strings corresponding to command line options for PETSc, used to solve the state systems. If this is None, then the direct solver mumps is used (default is None). adjoint_ksp_options : list[list[str or list[list[list[str ] or None A list of strings corresponding to command line options for PETSc, used to solve the adjoint systems. If this is None, then the same options as for the state systems are used (default is None)."
},
{
"ref":"cashocs.ShapeOptimizationProblem.solve",
"url":0,
"doc":"Solves the optimization problem by the method specified in the config file. Parameters      algorithm : str or None, optional Selects the optimization algorithm. Valid choices are 'gradient_descent' ('gd'), 'conjugate_gradient' ('cg'), or 'lbfgs' ('bfgs'). This overwrites the value specified in the config file. If this is None, then the value in the config file is used. Default is None. rtol : float or None, optional The relative tolerance used for the termination criterion. Overwrites the value specified in the config file. If this is None, the value from the config file is taken. Default is None. atol : float or None, optional The absolute tolerance used for the termination criterion. Overwrites the value specified in the config file. If this is None, the value from the config file is taken. Default is None. max_iter : int or None, optional The maximum number of iterations the optimization algorithm can carry out before it is terminated. Overwrites the value specified in the config file. If this is None, the value from the config file is taken. Default is None. Returns    - None Notes   - If either  rtol or  atol are specified as arguments to the solve call, the termination criterion changes to: - a purely relative one (if only  rtol is specified), i.e.,   \\nabla J(u_k)  \\leq \\texttt{rtol}  \\nabla J(u_0)  .  - a purely absolute one (if only  atol is specified), i.e.,   \\nabla J(u_K)  \\leq \\texttt{atol}.  - a combined one if both  rtol and  atol are specified, i.e.,   \\nabla J(u_k)  \\leq \\texttt{atol} + \\texttt{rtol}  \\nabla J(u_0)   ",
"func":1
},
{
"ref":"cashocs.ShapeOptimizationProblem.compute_shape_gradient",
"url":0,
"doc":"Solves the Riesz problem to determine the gradient(s) This can be used for debugging, or code validation. The necessary solutions of the state and adjoint systems are carried out automatically. Returns    - dolfin.function.function.Function The shape gradient function",
"func":1
},
{
"ref":"cashocs.ShapeOptimizationProblem.compute_state_variables",
"url":1,
"doc":"Solves the state system. This can be used for debugging purposes, to validate the solver and general behavior. Updates and overwrites the user input for the state variables. Returns    - None",
"func":1
},
{
"ref":"cashocs.ShapeOptimizationProblem.compute_adjoint_variables",
"url":1,
"doc":"Solves the adjoint system. This can be used for debugging purposes and solver validation. Updates / overwrites the user input for the adjoint variables. The solve of the corresponding state system needed to determine the adjoints is carried out automatically. Returns    - None",
"func":1
},
{
"ref":"cashocs.create_config",
"url":0,
"doc":"Generates a config object from a config file. Creates the config from a .ini file via the configparser package. Parameters      path : str The path to the config .ini file. Returns    - configparser.ConfigParser The output config file, which includes the path to the .ini file.",
"func":1
},
{
"ref":"cashocs.create_bcs_list",
"url":0,
"doc":"Create several Dirichlet boundary conditions at once. Wraps multiple Dirichlet boundary conditions into a list, in case they have the same value but are to be defined for multiple boundaries with different markers. Particularly useful for defining homogeneous boundary conditions. Parameters      function_space : dolfin.function.functionspace.FunctionSpace The function space onto which the BCs should be imposed on. value : dolfin.function.constant.Constant or dolfin.function.expression.Expression or dolfin.function.function.Function or float or tuple(float) The value of the boundary condition. Has to be compatible with the function_space, so that it could also be used as DirichletBC(function_space, value,  .). boundaries : dolfin.cpp.mesh.MeshFunctionSizet The MeshFunction object representing the boundaries. idcs : list[int] or int A list of indices / boundary markers that determine the boundaries onto which the Dirichlet boundary conditions should be applied to. Can also be a single integer for a single boundary. Returns    - list[dolfin.fem.dirichletbc.DirichletBC] A list of DirichletBC objects that represent the boundary conditions. Examples     Generate homogeneous Dirichlet boundary conditions for all 4 sides of the unit square. from fenics import  import cashocs mesh, _, _, _, _, _ = cashocs.regular_mesh(25) V = FunctionSpace(mesh, 'CG', 1) bcs = cashocs.create_bcs_list(V, Constant(0), boundaries, [1,2,3,4])",
"func":1
},
{
"ref":"cashocs.geometry",
"url":2,
"doc":"Mesh generation and import tools. This module consists of tools for for the fast generation or import of meshes into fenics. The import_mesh function is used to import (converted) gmsh mesh files, and the regular_(box_)mesh commands create 2D and 3D box meshes which are great for testing."
},
{
"ref":"cashocs.geometry.import_mesh",
"url":2,
"doc":"Imports a mesh file for use with cashocs / fenics. This function imports a mesh file that was generated by GMSH and converted to .xdmf with the command line function cashocs-convert (see cashocs main documentation). The syntax for the conversion is cashocs-convert in.msh out.xdmf If there are Physical quantities specified in the gmsh file, these are imported to the subdomains and boundaries output of this function and can also be directly accessed via the measures, e.g., with dx(1), ds(1), etc. Parameters      arg : str or configparser.ConfigParser This is either a string, in which case it corresponds to the location of the mesh file in .xdmf file format, or a config file that has this path stored in its settings. Returns    - mesh : dolfin.cpp.mesh.Mesh The imported (computational) mesh. subdomains : dolfin.cpp.mesh.MeshFunctionSizet A MeshFunction object containing the subdomains, i.e., the Physical regions marked in the gmsh file. boundaries : dolfin.cpp.mesh.MeshFunctionSizet A MeshFunction object containing the boundaries, i.e., the Physical regions marked in the gmsh file. Can, e.g., be used to set up boundary conditions. dx : ufl.measure.Measure The volume measure of the mesh corresponding to the subdomains (i.e. gmsh Physical region indices). ds : ufl.measure.Measure The surface measure of the mesh corresponding to the boundaries (i.e. gmsh Physical region indices). dS : ufl.measure.Measure The interior facet measure of the mesh corresponding to boundaries (i.e. gmsh Physical region indices).",
"func":1
},
{
"ref":"cashocs.geometry.regular_mesh",
"url":2,
"doc":"Creates a mesh corresponding to a rectangle or cube. This function creates a uniform mesh of either a rectangle or a cube, starting at the origin and having length specified in lx, lx, lz. The resulting mesh uses n elements along the shortest direction and accordingly many along the longer ones. The resulting domain is  [0, L_x] \\times [0, L_y] \\phantom{ \\times [0, L_z] a} \\quad \\text{ in } 2D,  [0, L_x] \\times [0, L_y] \\times [0, L_z] \\quad \\text{ in } 3D.  The boundary markers are ordered as follows: - 1 corresponds to \\(\\{x=0\\}\\). - 2 corresponds to \\(\\{x=L_x\\}\\). - 3 corresponds to \\(\\{y=0\\}\\). - 4 corresponds to \\(\\{y=L_y\\}\\). - 5 corresponds to \\(\\{z=0\\}\\) (only in 3D). - 6 corresponds to \\(\\{z=L_z\\}\\) (only in 3D). Parameters      n : int Number of elements in the shortest coordinate direction. L_x : float Length in x-direction. L_y : float Length in y-direction. L_z : float or None, optional Length in z-direction, if this is None, then the geometry will be two-dimensional (default is None). Returns    - mesh : dolfin.cpp.mesh.Mesh The computational mesh. subdomains : dolfin.cpp.mesh.MeshFunctionSizet A MeshFunction object containing the subdomains. boundaries : dolfin.cpp.mesh.MeshFunctionSizet A MeshFunction object containing the boundaries. dx : ufl.measure.Measure The volume measure of the mesh corresponding to subdomains. ds : ufl.measure.Measure The surface measure of the mesh corresponding to boundaries. dS : ufl.measure.Measure The interior facet measure of the mesh corresponding to boundaries.",
"func":1
},
{
"ref":"cashocs.geometry.regular_box_mesh",
"url":2,
"doc":"Creates a mesh corresponding to a rectangle or cube. This function creates a uniform mesh of either a rectangle or a cube, with specified start (S_) and end points (E_). The resulting mesh uses n elements along the shortest direction and accordingly many along the longer ones. The resulting domain is  [S_x, E_x] \\times [S_y, E_y] \\phantom{ \\times [S_z, E_z] a} \\quad \\text{ in } 2D,  [S_x, E_x] \\times [S_y, E_y] \\times [S_z, E_z] \\quad \\text{ in } 3D.  The boundary markers are ordered as follows: - 1 corresponds to \\(\\{x=S_x\\}\\). - 2 corresponds to \\(\\{x=E_x\\}\\). - 3 corresponds to \\(\\{y=S_y\\}\\). - 4 corresponds to \\(\\{y=E_y\\}\\). - 5 corresponds to \\(\\{z=S_z\\}\\) (only in 3D). - 6 corresponds to \\(\\{z=E_z\\}\\) (only in 3D). Parameters      n : int Number of elements in the shortest coordinate direction. S_x : float Start of the x-interval. S_y : float Start of the y-interval. S_z : float or None, optional Start of the z-interval, mesh is 2D if this is None (default is None). E_x : float End of the x-interval. E_y : float End of the y-interval. E_z : float or None, optional End of the z-interval, mesh is 2D if this is None (default is None). Returns    - mesh : dolfin.cpp.mesh.Mesh the computational mesh subdomains : dolfin.cpp.mesh.MeshFunctionSizet a MeshFunction object containing the subdomains boundaries : dolfin.cpp.mesh.MeshFunctionSizet a MeshFunction object containing the boundaries dx : ufl.measure.Measure the volume measure of the mesh corresponding to subdomains ds : ufl.measure.Measure the surface measure of the mesh corresponding to boundaries dS : ufl.measure.Measure the interior facet measure of the mesh corresponding to boundaries",
"func":1
},
{
"ref":"cashocs.geometry.MeshQuality",
"url":2,
"doc":"A class used to compute the quality of a mesh. This class implements either a skewness quality measure, one based on the maximum angle of the elements, or one based on the radius ratios. All quality measures have values in \\( [0, 1] \\), where 1 corresponds to the best / perfect element, and 0 corresponds to degenerate elements. Examples     This class can be directly used, without any instantiation. import cashocs mesh, _, _, _, _, _ = cashocs.regular_mesh(10) min_skew = cashocs.MeshQuality.min_skewness(mesh) avg_skew = cashocs.MeshQuality.avg_skewness(mesh) min_angle = cashocs.MeshQuality.min_maximum_angle(mesh) avg_angle = cashocs.MeshQuality.avg_maximum_angle(mesh) min_rad = cashocs.MeshQuality.min_radius_ratios(mesh) avg_rad = cashocs.MeshQuality.avg_radius_ratios(mesh) min_cond = cashocs.MeshQuality.min_condition_number(mesh) avg_cond = cashocs.MeshQuality.avg_condition_number(mesh) This works analogously for any mesh compatible with fenics. Initializes self."
},
{
"ref":"cashocs.geometry.MeshQuality.min_skewness",
"url":2,
"doc":"Computes the minimal skewness of the mesh. This measure the relative distance of a triangle's angles or a tetrahedrons dihedral angles to the corresponding optimal angle. The optimal angle is defined as the angle an equilateral, and thus equiangular, element has. The skewness lies in \\( [0,1] \\), where 1 corresponds to the case of an optimal (equilateral) element, and 0 corresponds to a degenerate element. The skewness corresponding to some (dihedral) angle \\( \\alpha \\) is defined as  1 - \\max \\left( \\frac{\\alpha - \\alpha^ }{\\pi - \\alpha } , \\frac{\\alpha^ - \\alpha}{\\alpha^ - 0} \\right),  where \\( \\alpha^ \\) is the corresponding optimal angle of the reference element. To compute the quality measure, the minimum of this expression over all elements and all of their (dihedral) angles is computed. Parameters      mesh : dolfin.cpp.mesh.Mesh The mesh whose quality shall be computed. Returns    - float The skewness of the mesh.",
"func":1
},
{
"ref":"cashocs.geometry.MeshQuality.avg_skewness",
"url":2,
"doc":"Computes the average skewness of the mesh. The skewness corresponding to some (dihedral) angle \\( \\alpha \\) is defined as  1 - \\max \\left( \\frac{\\alpha - \\alpha^ }{\\pi - \\alpha } , \\frac{\\alpha^ - \\alpha}{\\alpha^ - 0} \\right),  where \\( \\alpha^ \\) is the corresponding optimal angle of the reference element. Parameters      mesh : dolfin.cpp.mesh.Mesh The mesh, whose quality shall be computed. Returns    - flat The average skewness of the mesh.",
"func":1
},
{
"ref":"cashocs.geometry.MeshQuality.min_maximum_angle",
"url":2,
"doc":"Computes the minimal quality measure based on the largest angle. This measures the relative distance of a triangle's angles or a tetrahedron's dihedral angles to the corresponding optimal angle. The optimal angle is defined as the angle an equilateral (and thus equiangular) element has. This is defined as  1 - \\max\\left( \\frac{\\alpha - \\alpha^ }{\\pi - \\alpha^ } , 0 \\right),  where \\( \\alpha \\) is the corresponding (dihedral) angle of the element and \\( \\alpha^ \\) is the corresponding (dihedral) angle of the reference element. Parameters      mesh : dolfin.cpp.mesh.Mesh The mesh, whose quality shall be computed. Returns    - float The minimum value of the maximum angle quality measure.",
"func":1
},
{
"ref":"cashocs.geometry.MeshQuality.avg_maximum_angle",
"url":2,
"doc":"Computes the average quality of the mesh based on the maximum angle. Parameters      mesh : dolfin.cpp.mesh.Mesh The mesh, whose quality shall be computed. Returns    - float The average quality, based on the maximum angle measure.",
"func":1
},
{
"ref":"cashocs.geometry.MeshQuality.min_radius_ratios",
"url":2,
"doc":"Computes the minimal radius ratio of the mesh. This measures the ratio of the element's inradius to it's circumradius, normalized by the geometric dimension. It is an element of \\( [0,1] \\), where 1 indicates best element quality and 0 is obtained for degenerate elements. This is computed via  d \\frac{r}{R},  where \\(d\\) is the spatial dimension, \\(r\\) is the inradius, and \\(R\\) is the circumradius. To compute the (global) quality measure, the minimum of this expression over all elements is returned. Parameters      mesh : dolfin.cpp.mesh.Mesh The mesh, whose radius ratios shall be computed. Returns    - float The minimal radius ratio of the mesh.",
"func":1
},
{
"ref":"cashocs.geometry.MeshQuality.avg_radius_ratios",
"url":2,
"doc":"Computes the average radius ratio of the mesh. Parameters      mesh : dolfin.cpp.mesh.Mesh The mesh, whose quality shall be computed. Returns    - float The average radius ratio of the mesh.",
"func":1
},
{
"ref":"cashocs.geometry.MeshQuality.min_condition_number",
"url":2,
"doc":"Computes minimal mesh quality based on the condition number of the reference mapping. This quality criterion uses the condition number (in the Frobenius norm) of the (linear) mapping from the elements of the mesh to the reference element. Computes the minimum of the condition number over all elements. Parameters      mesh : dolfin.cpp.mesh.Mesh The mesh, whose quality shall be computed. Returns    - float The minimal condition number quality measure.",
"func":1
},
{
"ref":"cashocs.geometry.MeshQuality.avg_condition_number",
"url":2,
"doc":"Computes the average mesh quality based on the condition number of the reference mapping. Parameters      mesh : dolfin.cpp.mesh.Mesh The mesh, whose quality shall be computed. Returns    - float The average mesh quality based on the condition number.",
"func":1
},
{
"ref":"cashocs.utils",
"url":3,
"doc":"Module including utility and helper functions. These module includes utility and helper functions used in cashocs. They might also be interesting for users, so they are part of the public API. They include wrappers that allow to shorten the coding for often recurring actions."
},
{
"ref":"cashocs.utils.summation",
"url":3,
"doc":"Sums elements of a list in a UFL friendly fashion. This can be used to sum, e.g., UFL forms, or UFL expressions that can be used in UFL forms. Parameters      x : list[ufl.form.Form] or list[int] or list[float] The list of entries that shall be summed. Returns    - y : ufl.form.Form or int or float Sum of input (same type as entries of input). See Also     multiplication : Multiplies the elements of a list. Notes   - For \"usual\" summation of integers or floats, the built-in sum function of python or the numpy variant are recommended. Still, they are incompatible with fenics objects, so this function should be used for the latter. Examples     a = cashocs.summation([u.dx(i) v.dx(i) dx for i in mesh.geometric_dimension()]) is equivalent to a = u.dx(0) v.dx(0) dx + u.dx(1) v.dx(1) dx (for a 2D mesh).",
"func":1
},
{
"ref":"cashocs.utils.multiplication",
"url":3,
"doc":"Multiplies the elements of a list in a UFL friendly fashion. Used to build the product of certain UFL expressions to construct a UFL form. Parameters      x : list[ufl.core.expr.Expr] or list[int] or list[float] The list whose entries shall be multiplied. Returns    - y : ufl.core.expr.Expr or int or float The result of the multiplication. See Also     summation : Sums elements of a list. Examples     a = cashocs.multiplication([u.dx(i) for i in range(mesh.geometric_dimension( ]) is equivalent to a = u.dx(0)  u.dx(1) (for a 2D mesh).",
"func":1
},
{
"ref":"cashocs.utils.EmptyMeasure",
"url":3,
"doc":"Implements an empty measure (e.g. of a null set). This is used for automatic measure generation, e.g., if the fixed boundary is empty for a shape optimization problem, and is used to avoid case distinctions. Examples     dm = EmptyMeasure(dx) u dm is equivalent to Constant(0) u dm so that this generates zeros when assembled over. Initializes self. Parameters      measure : ufl.measure.Measure The underlying UFL measure."
},
{
"ref":"cashocs.utils.generate_measure",
"url":3,
"doc":"Generates a measure based on indices. Generates a MeasureSum or EmptyMeasure object corresponding to measure and the subdomains / boundaries specified in idx. This is a convenient shortcut to writing dx(1) + dx(2) + dx(3) +  . in case many measures are involved. Parameters      idx : list[int] A list of indices for the boundary / volume markers that shall define the new measure. measure : ufl.measure.Measure The corresponding UFL measure. Returns    - ufl.measure.Measure or cashocs.utils.EmptyMeasure The corresponding sum of the measures or an empty measure. Examples     from fenics import  import cashocs mesh, _, boundaries, dx, ds, _ = cashocs.regular_mesh(25) top_bottom_measure = cashocs.utils.generate_measure([3,4], ds) assemble(1 top_bottom_measure)",
"func":1
},
{
"ref":"cashocs.utils.create_config",
"url":3,
"doc":"Generates a config object from a config file. Creates the config from a .ini file via the configparser package. Parameters      path : str The path to the config .ini file. Returns    - configparser.ConfigParser The output config file, which includes the path to the .ini file.",
"func":1
},
{
"ref":"cashocs.utils.create_bcs_list",
"url":3,
"doc":"Create several Dirichlet boundary conditions at once. Wraps multiple Dirichlet boundary conditions into a list, in case they have the same value but are to be defined for multiple boundaries with different markers. Particularly useful for defining homogeneous boundary conditions. Parameters      function_space : dolfin.function.functionspace.FunctionSpace The function space onto which the BCs should be imposed on. value : dolfin.function.constant.Constant or dolfin.function.expression.Expression or dolfin.function.function.Function or float or tuple(float) The value of the boundary condition. Has to be compatible with the function_space, so that it could also be used as DirichletBC(function_space, value,  .). boundaries : dolfin.cpp.mesh.MeshFunctionSizet The MeshFunction object representing the boundaries. idcs : list[int] or int A list of indices / boundary markers that determine the boundaries onto which the Dirichlet boundary conditions should be applied to. Can also be a single integer for a single boundary. Returns    - list[dolfin.fem.dirichletbc.DirichletBC] A list of DirichletBC objects that represent the boundary conditions. Examples     Generate homogeneous Dirichlet boundary conditions for all 4 sides of the unit square. from fenics import  import cashocs mesh, _, _, _, _, _ = cashocs.regular_mesh(25) V = FunctionSpace(mesh, 'CG', 1) bcs = cashocs.create_bcs_list(V, Constant(0), boundaries, [1,2,3,4])",
"func":1
},
{
"ref":"cashocs.utils.Interpolator",
"url":3,
"doc":"Efficient interpolation between two function spaces. This is very useful, if multiple interpolations have to be carried out between the same spaces, which is made significantly faster by computing the corresponding matrix. The function spaces can even be defined on different meshes. Examples     from fenics import  import cashocs mesh, _, _, _, _, _ = cashocs.regular_mesh(25) V1 = FunctionSpace(mesh, 'CG', 1) V2 = FunctionSpace(mesh, 'CG', 2) expr = Expression('sin(2 pi x[0])', degree=1) u = interpolate(expr, V1) interp = cashocs.utils.Interpolator(V1, V2) interp.interpolate(u) Initializes the object. Parameters      V : dolfin.function.functionspace.FunctionSpace The function space whose objects shall be interpolated. W : dolfin.function.functionspace.FunctionSpace The space into which they shall be interpolated."
},
{
"ref":"cashocs.utils.Interpolator.interpolate",
"url":3,
"doc":"Interpolates function to target space. The function has to belong to the origin space, i.e., the first argument of __init__, and it is interpolated to the destination space, i.e., the second argument of __init__. There is no need to call set_allow_extrapolation on the function (this is done automatically due to the method). Parameters      u : dolfin.function.function.Function The function that shall be interpolated. Returns    - dolfin.function.function.Function The result of the interpolation.",
"func":1
},
{
"ref":"cashocs.utils.write_out_mesh",
"url":3,
"doc":"Writes out the current mesh as .msh file. This method updates the vertex positions in the  original_gmsh_file , the topology of the mesh and its connections are the same. The original gmsh file is kept, and a new one is generated under  out_mesh_file . Parameters      mesh : dolfin.cpp.mesh.Mesh The mesh object in fenics that should be saved as gmsh file. original_msh_file : str Path to the original gmsh mesh file of the mesh object, has to end with '.msh'. out_msh_file : str Path (and name) of the output mesh file, has to end with '.msh'. Returns    - None Notes   - The method only works with gmsh mesh 4.1 file format. Others might also work, but this is not tested or ensured in any way.",
"func":1
},
{
"ref":"cashocs.nonlinear_solvers",
"url":4,
"doc":"Custom solvers for nonlinear equations. This module has custom solvers for nonlinear PDEs, including a damped Newton methd. This is the only function at the moment, others might follow."
},
{
"ref":"cashocs.nonlinear_solvers.damped_newton_solve",
"url":4,
"doc":"A damped Newton method for solving nonlinear equations. The Newton method is based on the natural monotonicity test from Deuflhard [1]. It also allows fine tuning via a direct interface, and absolute, relative, and combined stopping criteria. Can also be used to specify the solver for the inner (linear) subproblems via petsc ksps. The method terminates after  max_iter iterations, or if a termination criterion is satisfied. These criteria are given by  \\lvert\\lvert F_{k} \\rvert\\rvert \\leq \\texttt{rtol} \\lvert\\lvert F_0 \\rvert\\rvert \\quad \\text{ if convergence_type is 'rel'}  \\lvert\\lvert F_{k} \\rvert\\rvert \\leq \\texttt{atol} \\quad \\text{ if convergence_type is 'abs'}  \\lvert\\lvert F_{k} \\rvert\\rvert \\leq \\texttt{atol} + \\text{rtol} \\lvert\\lvert F_0 \\rvert\\rvert \\quad \\text{ if convergence_type is 'combined'}  The norm chosen for the termination criterion is specified via  norm_type . Parameters      F : ufl.form.Form The variational form of the nonlinear problem to be solved by Newton's method. u : dolfin.function.function.Function The sought solution / initial guess. It is not assumed that the initial guess satisfies the Dirichlet boundary conditions, they are applied automatically. The method overwrites / updates this Function. bcs : list[dolfin.fem.dirichletbc.DirichletBC] A list of DirichletBCs for the nonlinear variational problem. rtol : float, optional Relative tolerance of the solver if convergence_type is either 'combined' or 'rel' (default is  rtol = 1e-10). atol : float, optional Absolute tolerance of the solver if convergence_type is either 'combined' or 'abs' (default is atol = 1e-10). max_iter : int, optional Maximum number of iterations carried out by the method (default is max_iter = 50). convergence_type : {'combined', 'rel', 'abs'} Determines the type of stopping criterion that is used. norm_type : {'l2', 'linf'} Determines which norm is used in the stopping criterion. damped : bool, optional If true, then a damping strategy is used. If false, the classical Newton-Raphson iteration (without damping) is used (default is True). verbose : bool, optional If true, prints status of the iteration to the console (default is true). ksp : petsc4py.PETSc.KSP, optional The PETSc ksp object used to solve the inner (linear) problem if this is None it uses the direct solver MUMPS (default is None). Returns    - dolfin.function.function.Function The solution of the nonlinear variational problem, if converged. This overrides the input function u. References      [1] P. Deuflhard, \"Newton methods for nonlinear problems\", Springer, Heidelberg, 2011, https: doi.org/10.1007/978-3-642-23899-4 Examples     This example solves the problem  - \\Delta u + u^3 = 1 \\quad \\text{ in } \\Omega=(0,1)^2  u = 0 \\quad \\text{ on } \\Gamma.  from fenics import  import cashocs mesh, _, boundaries, dx, _, _ = cashocs.regular_mesh(25) V = FunctionSpace(mesh, 'CG', 1) u = Function(V) v = TestFunction(V) F = inner(grad(u), grad(v  dx + pow(u,3) v dx - Constant(1) v dx bcs = cashocs.create_bcs_list(V, Constant(0.0), boundaries, [1,2,3,4]) cashocs.damped_newton_solve(F, u, bcs)",
"func":1
},
{
"ref":"cashocs.optimization_problem",
"url":1,
"doc":"Blueprint for the PDE constrained optimization problems. This module is used to define the parent class for the optimization problems, as many parameters and variables are common for optimal control and shape optimization problems."
},
{
"ref":"cashocs.optimization_problem.OptimizationProblem",
"url":1,
"doc":"Blueprint for an abstract PDE constrained optimization problem. This class performs the initialization of the shared input so that the rest of the package can use it directly. Additionally, it includes methods that can be used to compute the state and adjoint variables by solving the corresponding equations. This could be subclassed to generate custom optimization problems. Initializes the optimization problem. Parameters      state_forms : ufl.form.Form or list[ufl.form.Form] The weak form of the state equation. Can be either a UFL form or a list of UFL forms (if we have multiple equations). bcs_list : list[dolfin.fem.dirichletbc.DirichletBC] or list[list[dolfin.fem.dirichletbc.DirichletBC or dolfin.fem.dirichletbc.DirichletBC or None The list of DirichletBC objects describing Dirichlet (essential) boundary conditions. If this is None, then no Dirichlet boundary conditions are imposed. cost_functional_form : ufl.form.Form The UFL form of the cost functional. states : dolfin.function.function.Function or list[dolfin.function.function.Function] The state variable(s), can either be a single fenics Function, or a (ordered) list of these. adjoints : dolfin.function.function.Function or list[dolfin.function.function.Function] The adjoint variable(s), can either be a single fenics Function, or a (ordered) list of these. config : configparser.ConfigParser The config file for the problem, generated via cashocs.create_config(path_to_config). initial_guess : list[dolfin.function.function.Function], optional A list of functions that act as initial guess for the state variables, should be valid input for fenics.assign. If this is None, then a zero initial guess is used (default is None). ksp_options : list[list[str or list[list[list[str ] or None, optional A list of strings corresponding to command line options for PETSc, used to solve the state systems. If this is None, then the direct solver mumps is used (default is None). adjoint_ksp_options : list[list[str or list[list[list[str ] or None A list of strings corresponding to command line options for PETSc, used to solve the adjoint systems. If this is None, then the same options as for the state systems are used (default is None). Notes   - If one uses a single PDE constraint, the inputs can be the objects (UFL forms, functions, etc.) directly. In case multiple PDE constraints are present the inputs have to be put into (ordered) lists. The order of the objects depends on the order of the state variables, so that  state_forms[i] is the weak form of the PDE for state[i] with boundary conditions  bcs_list[i] and corresponding adjoint state  adjoints[i] . See Also     cashocs.OptimalControlProblem : Represents an optimal control problem. cashocs.ShapeOptimizationProblem : Represents a shape optimization problem."
},
{
"ref":"cashocs.optimization_problem.OptimizationProblem.compute_state_variables",
"url":1,
"doc":"Solves the state system. This can be used for debugging purposes, to validate the solver and general behavior. Updates and overwrites the user input for the state variables. Returns    - None",
"func":1
},
{
"ref":"cashocs.optimization_problem.OptimizationProblem.compute_adjoint_variables",
"url":1,
"doc":"Solves the adjoint system. This can be used for debugging purposes and solver validation. Updates / overwrites the user input for the adjoint variables. The solve of the corresponding state system needed to determine the adjoints is carried out automatically. Returns    - None",
"func":1
},
{
"ref":"cashocs.verification",
"url":5,
"doc":"This module includes finite difference Taylor tests to verify the computed gradients."
},
{
"ref":"cashocs.verification.control_gradient_test",
"url":5,
"doc":"Taylor test to verify that the computed gradient is correct. Parameters      ocp : cashocs.OptimalControlProblem The underlying optimal control problem, for which the gradient of the reduced cost function shall be verified. u : list[dolfin.function.function.Function], optional The point, at which the gradient shall be verified. If this is None, then the current controls of the optimization problem are used. h : list[dolfin.function.function.Function], optional The direction(s) for the directional (Gateaux) derivative. If this is None, one random direction is chosen. Returns    - float The convergence order from the Taylor test. If this is (close to) 2, everything works as expected.",
"func":1
},
{
"ref":"cashocs.verification.shape_gradient_test",
"url":5,
"doc":"Taylor test to verify that the computed shape gradient is correct. Parameters      sop : cashocs.ShapeOptimizationProblem The underlying shape optimization problem. h : dolfin.function.function.Function, optional The direction used to compute the directional derivative. If this is None, then a random direction is used (default is None). Returns    - float The computed convergence rate. The computed gradient is correct, if this quanitity is (about) 2.",
"func":1
},
{
"ref":"cashocs.verification.compute_convergence_rates",
"url":5,
"doc":"",
"func":1
}
]